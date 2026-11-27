"""Application errors that can be handled consistently by API layers."""


class LedgerError(Exception):
    """Base class for expected application failures."""

    code = "LEDGER_ERROR"


class DatabaseBusyError(LedgerError):
    """The SQLite writer lock could not be acquired within the timeout."""

    code = "DB_BUSY"


class NotFoundError(LedgerError):
    """A requested record does not exist or is not visible to the caller."""

    code = "NOT_FOUND"


class ConflictError(LedgerError):
    """A request conflicts with existing state or a uniqueness rule."""

    code = "CONFLICT"


class IdempotencyKeyReused(ConflictError):
    """A user reused a key for a different or already-recorded request."""

    code = "IDEMPOTENCY_KEY_REUSED"


class InsufficientFundsError(LedgerError):
    """A wallet does not have enough available balance for the operation."""

    code = "INSUFFICIENT_FUNDS"


class CurrencyMismatchError(LedgerError):
    """A financial operation attempted to combine different currencies."""

    code = "CURRENCY_MISMATCH"


class ValidationError(LedgerError, ValueError):
    """Input cannot be represented by the domain model."""

    code = "VALIDATION_ERROR"

class AlreadyReversedError(ConflictError):
    code = "ALREADY_REVERSED"


class ReversalOfReversalError(ConflictError):
    code = "REVERSAL_OF_REVERSAL"


class ReversalOverdrawError(InsufficientFundsError):
    code = "REVERSAL_OVERDRAW"