"""Password and session operations shared by the HTTP API and local admin CLI."""

import hashlib
import os
import secrets
from dataclasses import dataclass
from datetime import UTC, timedelta
from typing import Annotated, Literal

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field

from ledger_api.db import SQLiteDatabase
from ledger_api.domain.errors import ConflictError, LedgerError
from ledger_api.providers import SecureTokenProvider, SystemClock, UUIDProvider
from ledger_api.providers.protocols import (
    ClockProvider,
    DatabaseProvider,
    IdProvider,
    TokenProvider,
)
from ledger_api.repositories.sessions import SessionRepository
from ledger_api.repositories.users import UserRepository


def normalize_email(value):
    return value.strip().lower() if isinstance(value, str) else value


Email = Annotated[EmailStr, BeforeValidator(normalize_email)]
Password = Annotated[str, Field(min_length=12, max_length=128)]


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: Email
    password: Password


class Registration(Credentials):
    name: str = Field(min_length=1, max_length=100)


class User(BaseModel):
    user_id: str
    name: str
    email: str
    role: Literal["USER", "ADMIN"]
    created_at: str


class Unauthenticated(LedgerError):
    code = "UNAUTHENTICATED"

    def __init__(self):
        super().__init__("Authentication failed")


class Forbidden(LedgerError):
    code = "FORBIDDEN"


class DuplicateEmail(ConflictError):
    code = "DUPLICATE_EMAIL"


class WalletExists(ConflictError):
    code = "WALLET_EXISTS"


@dataclass(frozen=True)
class Principal:
    user: User
    session_id: str


def public_user(row):
    return User(email=row["normalized_email"], **dict(row))


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


def timestamp(value):
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


class AuthService:
    def __init__(
        self,
        db: DatabaseProvider,
        clock: ClockProvider,
        ids: IdProvider,
        tokens: TokenProvider,
    ):
        self.db = db
        self.clock = clock
        self.ids = ids
        self.tokens = tokens
        self.hasher = PasswordHasher(type=Type.ID)
        self.dummy_hash = self.hasher.hash(secrets.token_urlsafe(32))

    def register(self, data: Registration, role: Literal["USER", "ADMIN"] = "USER"):
        hashed = self.hasher.hash(data.password)
        with self.db.write_transaction() as conn:
            users = UserRepository(conn)
            if users.get_by_email(data.email):
                raise DuplicateEmail("Email already registered")
            user_id = self.ids.new_id()
            users.create(
                user_id,
                data.email,
                data.name,
                hashed,
                role,
                timestamp(self.clock.now()),
            )
            return public_user(users.get(user_id))

    def login(self, data: Credentials):
        with self.db.connection() as conn:
            user = UserRepository(conn).get_by_email(data.email)
        try:
            self.hasher.verify(
                user["password_hash"] if user else self.dummy_hash, data.password
            )
        except VerifyMismatchError:
            raise Unauthenticated() from None
        if user is None:
            raise Unauthenticated()
        token = self.tokens.generate_token()
        now = self.clock.now()
        with self.db.write_transaction() as conn:
            SessionRepository(conn).create(
                session_id=self.ids.new_id(),
                user_id=user["user_id"],
                token_digest=digest(token),
                created_at=timestamp(now),
                expires_at=timestamp(now + timedelta(minutes=30)),
            )
        return {"token": token, "expires_in": 1800, "role": user["role"]}

    def authenticate(self, token):
        with self.db.connection() as conn:
            session = SessionRepository(conn).get_active_by_digest(
                digest(token), timestamp(self.clock.now())
            )
            if session is None:
                raise Unauthenticated()
            user = public_user(UserRepository(conn).get(session["user_id"]))
            return Principal(user, session["session_id"])


def configured_service():
    db = SQLiteDatabase(os.environ.get("LEDGER_DB_PATH", "data/ledger.sqlite3"))
    db.initialize()
    return AuthService(db, SystemClock(), UUIDProvider(), SecureTokenProvider())
