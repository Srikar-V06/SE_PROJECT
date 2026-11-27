from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from ledger_api.auth import configured_service
from ledger_api.domain.errors import LedgerError
from ledger_api.routes import router


@asynccontextmanager
async def lifespan(app):
    app.state.auth = configured_service()
    yield


app = FastAPI(title="Financial Ledger and Digital Wallet API", lifespan=lifespan)
app.include_router(router)
app.mount(
    "/app",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="ui",
)


def error(status, code, message, headers=None):
    return JSONResponse(
        {"code": code, "message": message}, status_code=status, headers=headers
    )


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return error(400, "VALIDATION_ERROR", "Invalid request")


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    code = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(
        exc.status_code, "HTTP_ERROR"
    )
    return error(exc.status_code, code, exc.detail, exc.headers)


@app.exception_handler(LedgerError)
async def domain_error(request, exc):
    statuses = {
        "VALIDATION_ERROR": 400,
        "UNAUTHENTICATED": 401,
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "DUPLICATE_EMAIL": 409,
        "WALLET_EXISTS": 409,
        "IDEMPOTENCY_KEY_REUSED": 409,
        "INSUFFICIENT_FUNDS": 422,
        "CURRENCY_MISMATCH": 422,
        "DB_BUSY": 503,
        "ALREADY_REVERSED": 409,
        "REVERSAL_OF_REVERSAL": 409,
        "REVERSAL_OVERDRAW": 422,
    }
    status = statuses.get(exc.code)
    if status is None:
        return await internal_error(request, exc)
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    return error(status, exc.code, str(exc), headers)


@app.exception_handler(Exception)
async def internal_error(request, exc):
    return error(500, "INTERNAL_ERROR", "Internal server error")


@app.get("/health")
def health():
    return {"status": "ok"}
