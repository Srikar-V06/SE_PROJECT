import assert from "node:assert/strict";
import test from "node:test";
import { toMinorUnits } from "../src/ledger_api/static/money.js";

test("converts decimal text to integer minor units exactly", () => {
    for (const [input, expected] of [
        ["100.50", 10050], ["0.29", 29], ["0.01", 1], ["1.2", 120],
        ["42", 4200], ["10000000000.00", 1000000000000]
    ]) {
        assert.equal(toMinorUnits(input), expected);
    }
});

test("rejects invalid notation, excess precision and amounts outside the API limit", () => {
    for (const input of ["1e3", "10.555", "letters", "", "-1", "0.00", "1\n", "10000000000.01"]) {
        assert.throws(() => toMinorUnits(input));
    }
});
