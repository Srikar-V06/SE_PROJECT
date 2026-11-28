import { setupOperations } from "./operations.js";

const loginView = document.getElementById("login-view");
const registerView = document.getElementById("register-view");
const dashboardView = document.getElementById("dashboard-view");

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const walletForm = document.getElementById("wallet-form");

const statusMessage = document.getElementById("status-message");
const walletList = document.getElementById("wallet-list");
const emptyWallets = document.getElementById("empty-wallets");
const welcomeName = document.getElementById("welcome-name");
const userRole = document.getElementById("user-role");

let session = null;
let currentUser = null;
let expiryTimer = null;
let busy = false;

const operations = setupOperations({ api, runAction, showMessage, refreshWallets, formatBalance });


function showMessage(message, type = "") {
    statusMessage.textContent = message;
    statusMessage.className = type;
}


function showView(view) {
    loginView.hidden = view !== "login";
    registerView.hidden = view !== "register";
    dashboardView.hidden = view !== "dashboard";
}


function clearSession(message = "", type = "") {
    session = null;
    currentUser = null;

    if (expiryTimer !== null) {
        window.clearTimeout(expiryTimer);
        expiryTimer = null;
    }

    walletList.replaceChildren();
    operations.clear();
    emptyWallets.hidden = false;
    welcomeName.textContent = "";
    userRole.textContent = "";

    loginForm.reset();
    registerForm.reset();
    walletForm.reset();

    showView("login");
    showMessage(message, type);
}


async function runAction(action) {
    if (busy) {
        return;
    }

    busy = true;

    const buttons = document.querySelectorAll("button");

    for (const button of buttons) {
        button.disabled = true;
    }

    showMessage("Loading…");

    try {
        await action();
    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        busy = false;

        for (const button of buttons) {
            button.disabled = false;
        }
    }
}


async function api(path, options = {}) {
    const {
        method = "GET",
        body,
        authenticated = true,
        idempotencyKey
    } = options;

    const activeSession = session;

    const headers = {
        Accept: "application/json"
    };
    if (idempotencyKey) {
        headers["Idempotency-Key"] = idempotencyKey;
    }

    if (body !== undefined) {
        headers["Content-Type"] = "application/json";
    }

    if (authenticated) {
        if (
            activeSession === null ||
            Date.now() >= activeSession.expiresAt
        ) {
            clearSession("Please sign in again.", "error");
            throw new Error("Your session has ended.");
        }

        headers.Authorization = `Bearer ${activeSession.token}`;
    }

    let response;

    try {
        response = await fetch(path, {
            method,
            headers,
            body: body === undefined ? undefined : JSON.stringify(body),
            credentials: "omit",
            cache: "no-store",
            redirect: "error"
        });
    } catch {
        throw new Error("Unable to contact the server. Please try again.");
    }

    if (authenticated && session !== activeSession) {
        throw new Error("Your session has ended.");
    }

    if (response.status === 401) {
        clearSession("Authentication required.", "error");

        throw new Error(
            authenticated
                ? "Your session has expired or is no longer valid."
                : "Incorrect email address or password."
        );
    }

    let data;

    try {
        const raw = await response.text();

        data = JSON.parse(raw, (key, value, context) => {
            if (
                key === "balance_minor" &&
                typeof value === "number" &&
                context?.source &&
                /^\d+$/.test(context.source)
            ) {
                return BigInt(context.source);
            }

            return value;
        });
    } catch {
        throw new Error("The server returned an invalid response.");
    }

    if (authenticated && session !== activeSession) {
        throw new Error("Your session has ended.");
    }

    if (!response.ok) {
        if (response.status === 503) {
            throw new Error("The database is busy. Please try again.");
        }
        if (response.status >= 500) {
            throw new Error("The server is unavailable. Please try again.");
        }

        const message =
            typeof data?.message === "string"
                ? data.message
                : "The request could not be completed.";

        const error = new Error(message);
        error.definitive = true;
        throw error;
    }

    return data;
}


function formatBalance(amountMinor, currency) {
    let amount;

    if (typeof amountMinor === "bigint") {
        amount = amountMinor;
    } else if (
        Number.isSafeInteger(amountMinor) &&
        amountMinor >= 0
    ) {
        amount = BigInt(amountMinor);
    } else {
        return `${currency} — balance unavailable at this precision`;
    }

    const major = amount / 100n;
    const minor = (amount % 100n).toString().padStart(2, "0");

    return `${currency} ${major}.${minor}`;
}


function renderWallets(wallets) {
    operations.setWallets(wallets);
    walletList.replaceChildren();

    emptyWallets.hidden = wallets.length !== 0;

    for (const wallet of wallets) {
        const card = document.createElement("article");
        card.className = "wallet-card";

        const heading = document.createElement("h3");
        heading.textContent = `${wallet.currency} Wallet`;

        const balance = document.createElement("p");
        balance.className = "wallet-balance";
        balance.textContent = formatBalance(
            wallet.balance_minor,
            wallet.currency
        );

        const identifier = document.createElement("p");
        identifier.className = "wallet-id";
        identifier.textContent = `Wallet ID: ${wallet.wallet_id}`;

        card.append(heading, balance, identifier);
        walletList.append(card);
    }
}


async function refreshWallets() {
    const wallets = await api("/users/me/wallets");

    renderWallets(wallets);
}


async function loadDashboard() {
    const user = await api("/auth/me");

    currentUser = user;

    welcomeName.textContent = `Welcome, ${user.name}`;
    userRole.textContent = user.role;
    document.getElementById("admin-panel").hidden = user.role !== "ADMIN";

    await refreshWallets();

    showView("dashboard");
}


document.getElementById("show-register").addEventListener(
    "click",
    () => {
        loginForm.reset();
        showMessage("");
        showView("register");
    }
);


document.getElementById("show-login").addEventListener(
    "click",
    () => {
        registerForm.reset();
        showMessage("");
        showView("login");
    }
);


registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    await runAction(async () => {
        const name = document.getElementById("register-name").value;
        const email = document.getElementById("register-email").value;
        const password = document.getElementById("register-password").value;

        document.getElementById("register-password").value = "";

        await api("/auth/register", {
            method: "POST",
            authenticated: false,
            body: { name, email, password }
        });

        registerForm.reset();

        showView("login");

        document.getElementById("login-email").value = email;

        showMessage(
            "Account created successfully. Please sign in.",
            "success"
        );
    });
});


loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    await runAction(async () => {
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;

        document.getElementById("login-password").value = "";

        const result = await api("/auth/login", {
            method: "POST",
            authenticated: false,
            body: { email, password }
        });

        session = {
            token: result.token,
            expiresAt: Date.now() + result.expires_in * 1000
        };

        expiryTimer = window.setTimeout(() => {
            clearSession(
                "Your session has expired. Please sign in again.",
                "error"
            );
        }, result.expires_in * 1000);

        loginForm.reset();

        try {
            await loadDashboard();
            showMessage("Signed in successfully.", "success");
        } catch (error) {
            clearSession();
            throw error;
        }
    });
});


walletForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    await runAction(async () => {
        if (currentUser === null) {
            throw new Error("Please sign in first.");
        }

        const currency = document.getElementById("wallet-currency").value;

        await api(`/users/${currentUser.user_id}/wallets`, {
            method: "POST",
            body: { currency }
        });

        await refreshWallets();

        showMessage("Wallet created successfully.", "success");
    });
});


document.getElementById("refresh-wallets").addEventListener(
    "click",
    async () => {
        await runAction(async () => {
            await refreshWallets();
            showMessage("Wallet balances refreshed.", "success");
        });
    }
);


document.getElementById("logout-button").addEventListener(
    "click",
    async () => {
        await runAction(async () => {
            try {
                await api("/auth/logout", {
                    method: "POST"
                });

                clearSession("Signed out successfully.", "success");
            } catch {
                clearSession(
                    "Signed out locally. Server-side revocation could not be confirmed.",
                    "error"
                );
            }
        });
    }
);


window.addEventListener("pagehide", () => {
    clearSession();
});


showView("login");
