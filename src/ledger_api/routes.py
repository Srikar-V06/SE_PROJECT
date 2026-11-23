"""Authentication and wallet HTTP endpoints."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict

from ledger_api.auth import (
    AuthService,
    Credentials,
    Forbidden,
    Principal,
    Registration,
    Unauthenticated,
    User,
    WalletExists,
    timestamp,
)
from ledger_api.domain.errors import NotFoundError
from ledger_api.repositories.accounts import AccountRepository
from ledger_api.repositories.sessions import SessionRepository
from ledger_api.repositories.wallets import WalletRepository

router = APIRouter()


def service(request: Request) -> AuthService:
    return request.app.state.auth


Service = Annotated[AuthService, Depends(service)]
Bearer = Annotated[
    HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))
]


def current_user(auth: Service, bearer: Bearer) -> Principal:
    if bearer is None:
        raise Unauthenticated()
    return auth.authenticate(bearer.credentials)


Caller = Annotated[Principal, Depends(current_user)]


def require_admin(caller: Caller) -> Principal:
    if caller.user.role != "ADMIN":
        raise Forbidden("Administrator role required")
    return caller


class WalletRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    currency: Literal["INR", "USD"]


class Wallet(WalletRequest):
    model_config = ConfigDict(extra="ignore")
    wallet_id: str
    user_id: str
    balance_minor: int
    created_at: str


@router.post("/auth/register", status_code=201)
def register(data: Registration, auth: Service) -> User:
    return auth.register(data)


@router.post("/auth/login")
def login(data: Credentials, auth: Service, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return auth.login(data)


@router.get("/auth/me")
def me(caller: Caller) -> User:
    return caller.user


@router.post("/auth/logout")
def logout(caller: Caller, auth: Service):
    with auth.db.write_transaction() as conn:
        SessionRepository(conn).revoke(caller.session_id, timestamp(auth.clock.now()))
    return {"message": "Session revoked"}


@router.post("/users/{user_id}/wallets", status_code=201)
def create_wallet(
    user_id: UUID, data: WalletRequest, caller: Caller, auth: Service
) -> Wallet:
    owner = caller.user.user_id
    if str(user_id) != owner:
        raise Forbidden("Wallet creation requires the caller's own user ID")
    with auth.db.write_transaction() as conn:
        wallets = WalletRepository(conn)
        if wallets.get_for_user(owner, data.currency):
            raise WalletExists("Wallet already exists for this currency")
        account_id = auth.ids.new_id()
        wallet_id = auth.ids.new_id()
        created = timestamp(auth.clock.now())
        AccountRepository(conn).create(account_id, "WALLET", data.currency, created)
        wallets.create(wallet_id, owner, account_id, data.currency, created)
        return Wallet(**dict(wallets.get(wallet_id)))


@router.get("/users/me/wallets")
def list_wallets(caller: Caller, auth: Service) -> list[Wallet]:
    with auth.db.connection() as conn:
        rows = WalletRepository(conn).list_for_user(caller.user.user_id)
        return [Wallet(**dict(row)) for row in rows]


@router.get("/wallets/{wallet_id}")
def get_wallet(wallet_id: UUID, caller: Caller, auth: Service) -> Wallet:
    with auth.db.connection() as conn:
        row = WalletRepository(conn).get(str(wallet_id))
        if row["user_id"] != caller.user.user_id and caller.user.role != "ADMIN":
            raise NotFoundError("wallet not found")
        return Wallet(**dict(row))
