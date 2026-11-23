"""Protocols for dependencies used by business services."""

from __future__ import annotations

import sqlite3
from contextlib import AbstractContextManager
from datetime import datetime
from typing import Protocol


class DatabaseProvider(Protocol):
    def connection(self) -> AbstractContextManager[sqlite3.Connection]: ...

    def write_transaction(self) -> AbstractContextManager[sqlite3.Connection]: ...


class ClockProvider(Protocol):
    def now(self) -> datetime: ...


class IdProvider(Protocol):
    def new_id(self) -> str: ...


class TokenProvider(Protocol):
    def generate_token(self) -> str: ...
