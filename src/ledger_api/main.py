from fastapi import FastAPI

app = FastAPI(title="Financial Ledger and Digital Wallet API")


@app.get("/health")
def health():
    return {"status": "ok"}