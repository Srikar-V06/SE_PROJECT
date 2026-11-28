export function toMinorUnits(value) {
    if (typeof value !== "string" || !/^\d+(?:\.\d{1,2})?$/.test(value) || value.trim() !== value) {
        throw new Error("Enter a decimal amount with at most two decimal places.");
    }
    const [whole, fraction = ""] = value.split(".");
    const minor = BigInt(whole) * 100n + BigInt(fraction.padEnd(2, "0"));
    if (minor < 1n || minor > 1000000000000n) {
        throw new Error("Enter an amount between 0.01 and 10000000000.00.");
    }
    return Number(minor);
}
