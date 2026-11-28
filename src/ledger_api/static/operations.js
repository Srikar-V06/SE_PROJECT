import { toMinorUnits } from "./money.js";

const byId = id => document.getElementById(id);
const pageSize = 20;

function fieldValue(id, parse) {
    const field = byId(id);
    try {
        return parse(field.value);
    } catch (error) {
        field.setCustomValidity(error.message);
        field.reportValidity();
        throw error;
    }
}

function uuid(value) {
    if (!/^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i.test(value)) {
        throw new Error("Enter a wallet or transaction ID in UUID format.");
    }
    return value.toLowerCase();
}

function line(container, text) {
    const p = document.createElement("p");
    p.textContent = text;
    container.append(p);
}

export function setupOperations({ api, runAction, showMessage, refreshWallets, formatBalance }) {
    let offset = 0;
    const pending = new Map();
    const historyWallet = byId("history-wallet");
    const receipt = byId("receipt");
    const historyList = byId("history-list");

    function resetHistory() {
        offset = 0;
        historyList.replaceChildren();
        byId("previous-page").hidden = true;
        byId("next-page").hidden = true;
    }

    function setWallets(wallets) {
        for (const select of [byId("sender"), historyWallet]) {
            const previous = select.value;
            select.replaceChildren();
            for (const wallet of wallets) {
                const option = document.createElement("option");
                option.value = wallet.wallet_id;
                option.textContent = wallet.currency + " · " + wallet.wallet_id;
                select.append(option);
            }
            if (wallets.some(wallet => wallet.wallet_id === previous)) {
                select.value = previous;
            }
            if (!wallets.length) {
                const option = document.createElement("option");
                option.value = "";
                option.textContent = "Create a wallet first";
                select.append(option);
            }
        }
    }

    function clear() {
        for (const [form, intent] of pending) {
            form.querySelector("fieldset").disabled = false;
            form.querySelector("button").textContent = intent.label;
        }
        pending.clear();
        for (const form of document.querySelectorAll(".operations-panel form")) {
            form.reset();
            for (const input of form.querySelectorAll("input")) input.setCustomValidity("");
        }
        setWallets([]);
        resetHistory();
        byId("admin-panel").hidden = true;
        byId("receipt-details").replaceChildren();
        byId("report").replaceChildren();
        receipt.hidden = true;
    }

    function entryText(entry) {
        return `Entry ${entry.entry_id} · ${entry.created_at} · ${entry.direction} · ${formatBalance(entry.amount_minor, entry.currency)}`;
    }

    function showReceipt(tx) {
        const details = byId("receipt-details");
        details.replaceChildren();
        line(details, tx.type + " · " + tx.transaction_id);
        line(details, tx.created_at);
        if (tx.description) line(details, tx.description);
        if (tx.reversal_of_transaction_id) line(details, "Reversal of " + tx.reversal_of_transaction_id);
        for (const entry of tx.entries) line(details, entryText(entry) + " · Account " + entry.account_id);
        receipt.hidden = false;
        receipt.focus();
    }

    function financialForm(id, buildRequest) {
        const form = byId(id);
        const fields = form.querySelector("fieldset");
        const button = form.querySelector("button");
        form.addEventListener("input", event => event.target.setCustomValidity(""));
        form.addEventListener("submit", event => {
            event.preventDefault();
            runAction(async () => {
                let intent = pending.get(form);
                if (!intent) {
                    intent = { ...buildRequest(), key: window.crypto.randomUUID(), label: button.textContent };
                    pending.set(form, intent);
                }
                fields.disabled = true;
                let tx;
                try {
                    tx = await api(intent.path, {
                        method: "POST", body: intent.body, idempotencyKey: intent.key
                    });
                } catch (error) {
                    if (!pending.has(form)) throw error;
                    if (!error.definitive) {
                        button.textContent = "Retry same request";
                        throw new Error(error.message + " Retry to confirm the original request.");
                    }
                    fields.disabled = false;
                    button.textContent = intent.label;
                    pending.delete(form);
                    throw error;
                }
                fields.disabled = false;
                button.textContent = intent.label;
                pending.delete(form);
                form.reset();
                showReceipt(tx);
                resetHistory();
                try {
                    await refreshWallets();
                } catch (error) {
                    throw new Error("Transaction confirmed. Balance refresh failed. " + error.message);
                }
                showMessage("Transaction confirmed.", "success");
            });
        });
    }

    financialForm("transfer-form", () => ({
        path: "/transfers",
        body: {
            sender_wallet_id: byId("sender").value,
            recipient_wallet_id: fieldValue("recipient", uuid),
            amount_minor: fieldValue("transfer-amount", toMinorUnits),
            description: byId("description").value || null
        }
    }));
    financialForm("fund-form", () => ({
        path: "/wallets/" + fieldValue("fund-wallet", uuid) + "/fund",
        body: { amount_minor: fieldValue("fund-amount", toMinorUnits) }
    }));
    financialForm("reverse-form", () => ({
        path: "/transactions/" + fieldValue("reverse-id", uuid) + "/reverse",
        body: {}
    }));

    async function loadHistory(start) {
        const wallet = historyWallet.value;
        const page = await api(`/ledger-entries?wallet_id=${wallet}&offset=${start}&limit=${pageSize + 1}`);
        if (wallet !== historyWallet.value) {
            showMessage("Select View entries for this wallet.");
            return;
        }
        offset = start;
        historyList.replaceChildren();
        for (const entry of page.entries.slice(0, pageSize)) {
            const card = document.createElement("article");
            line(card, entryText(entry));
            const detail = document.createElement("button");
            detail.type = "button";
            detail.className = "secondary";
            detail.textContent = "View transaction " + entry.transaction_id;
            detail.addEventListener("click", () => runAction(async () => {
                showReceipt(await api("/transactions/" + entry.transaction_id));
                showMessage("Transaction details loaded.");
            }));
            card.append(detail);
            historyList.append(card);
        }
        byId("previous-page").hidden = start === 0;
        byId("next-page").hidden = page.entries.length <= pageSize;
        if (!page.entries.length) line(historyList, "No ledger entries for this wallet.");
        showMessage("History loaded. Page " + (start / pageSize + 1) + ".");
    }
    historyWallet.addEventListener("change", resetHistory);
    byId("history-form").addEventListener("submit", event => {
        event.preventDefault();
        runAction(() => loadHistory(0));
    });
    byId("previous-page").addEventListener("click", () => runAction(() => loadHistory(offset - pageSize)));
    byId("next-page").addEventListener("click", () => runAction(() => loadHistory(offset + pageSize)));
    byId("reconcile").addEventListener("click", () => runAction(async () => {
        const report = byId("report");
        report.replaceChildren();
        const result = await api("/admin/reconciliation");
        line(report, result.overall_status + " · " + result.generated_at);
        line(report, `Checked ${result.checked_transactions} transactions, ${result.checked_wallets} wallets and ${result.checked_entries} entries.`);
        for (const [name, ids] of [
            ["Transactions", result.failing_transaction_ids], ["Wallets", result.failing_wallet_ids],
            ["Entries", result.failing_entry_ids], ["Currencies", result.failing_currencies]
        ]) {
            if (ids.length) line(report, name + " with inconsistencies: " + ids.join(", "));
        }
        showMessage("Reconciliation complete. " + result.overall_status);
    }));
    return { setWallets, clear };
}
