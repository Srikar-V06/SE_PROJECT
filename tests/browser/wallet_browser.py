"""Live UI contract, invoked explicitly by the browser CI job."""
import os
import secrets
import socket
import threading

import pytest
import uvicorn
from playwright.sync_api import expect, sync_playwright

from ledger_api.main import app
from ledger_api.repositories.users import UserRepository


@pytest.fixture
def live_api(tmp_path, monkeypatch):
    monkeypatch.setenv("LEDGER_DB_PATH", str(tmp_path / "browser.sqlite3"))
    ready = threading.Event()

    class Server(uvicorn.Server):
        async def startup(self, sockets=None):
            await super().startup(sockets)
            ready.set()

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        server = Server(uvicorn.Config(app, log_level="warning"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        try:
            assert ready.wait(15) and server.started
            yield f"http://127.0.0.1:{listener.getsockname()[1]}/app/"
        finally:
            server.should_exit = True
            thread.join(10)


@pytest.mark.parametrize("width", [1280, 360])
def test_wallet_journey(live_api, width):
    password = secrets.token_urlsafe(24)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=os.getenv("BROWSER_CHANNEL"))
        page = browser.new_page(viewport={"width": width, "height": 850})
        page.goto(live_api)

        def register_wallet(email, admin=False):
            page.click("#show-register")
            page.fill("#register-name", "Browser user")
            page.fill("#register-email", email)
            page.fill("#register-password", password)
            page.click("#register-form button")
            expect(page.locator("#login-email")).to_have_value(email)
            if admin:
                with app.state.auth.db.write_transaction() as conn:
                    UserRepository(conn).grant_admin(email)
            page.fill("#login-password", password)
            page.click("#login-form button")
            page.click("#wallet-form button")
            wallet = page.locator("#sender option[value]:not([value=''])")
            expect(wallet).to_have_count(1)
            return wallet.get_attribute("value")

        dest = register_wallet("recipient@example.org")
        expect(page.locator("#admin-panel")).to_be_hidden()
        page.click("#logout-button")
        source = register_wallet("admin@example.org", admin=True)
        page.fill("#fund-wallet", source)
        page.fill("#fund-amount", "10.00")
        page.click("#fund-form button")
        expect(page.locator("#receipt")).to_contain_text("FUNDING")

        attempts = []

        def lose_first_response(route):
            attempts.append((route.request.headers["idempotency-key"], route.request.post_data))
            response = route.fetch()
            assert response.status == 201
            if len(attempts) == 1:
                assert page.locator("#transfer-form button").is_disabled()
                page.locator("#transfer-form").evaluate("(form) => form.requestSubmit()")
                route.abort()
            else:
                assert response.headers.get("idempotent-replayed") == "true"
                route.fulfill(response=response)

        page.route("**/transfers", lose_first_response)
        page.fill("#recipient", dest)
        page.fill("#transfer-amount", "2.50")
        page.click("#transfer-form button")
        page.get_by_role("button", name="Retry same request").click()
        expect(page.locator("#receipt")).to_contain_text("TRANSFER")
        assert len(attempts) == 2 and attempts[0] == attempts[1]
        tx = page.locator("#receipt-details p").first.inner_text().split(" · ")[1]
        page.click("#history-form button")
        page.get_by_role("button", name=f"View transaction {tx}").click()
        page.fill("#reverse-id", tx)
        page.click("#reverse-form button")
        expect(page.locator("#receipt")).to_contain_text("Reversal of " + tx)
        page.click("#reconcile")
        expect(page.locator("#report")).to_contain_text("PASS")
        expect(page.locator("#report")).to_contain_text("3 transactions, 2 wallets and 6 entries")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.click("#logout-button")
        expect(page.locator("#login-form")).to_be_visible()
        expect(page.locator("#dashboard-view")).to_be_hidden()
        browser.close()
