import pytest

from ledger_api.domain.errors import ValidationError
from ledger_api.domain.money import Currency, Money


@pytest.mark.parametrize(
    "amount",
    [10.5, 100.0, 1e3, "100", True, False, -1],
)
def test_invalid_minor_units(amount):
    with pytest.raises(ValidationError):
        Money.from_minor(amount, Currency.INR)


def test_integer_minor_units():
    money = Money.from_minor(10050, Currency.INR)

    assert money.minor == 10050
    assert money.currency == Currency.INR


def test_zero_balance():
    money = Money.from_minor(0, Currency.INR)

    assert money.minor == 0


def test_exact_conversion():
    money = Money.from_major("100.50", Currency.INR)

    assert money.minor == 10050
    assert money.to_major_string() == "100.50"


@pytest.mark.parametrize("amount", ["10.555", "-2.00", "invalid"])
def test_invalid_decimal_conversion(amount):
    with pytest.raises(ValidationError):
        Money.from_major(amount, Currency.INR)


def test_money_addition():
    first = Money.from_minor(500, Currency.INR)
    second = Money.from_minor(300, Currency.INR)

    assert (first + second).minor == 800


def test_money_subtraction():
    first = Money.from_minor(500, Currency.INR)
    second = Money.from_minor(300, Currency.INR)

    assert (first - second).minor == 200


def test_negative_result_rejected():
    first = Money.from_minor(100, Currency.INR)
    second = Money.from_minor(200, Currency.INR)

    with pytest.raises(ValidationError):
        first - second


def test_cross_currency_arithmetic_rejected():
    first = Money.from_minor(100, Currency.INR)
    second = Money.from_minor(100, Currency.USD)

    with pytest.raises(ValidationError):
        first + second


def test_unsupported_currency():
    with pytest.raises(ValidationError):
        Money.from_minor(100, "EUR")