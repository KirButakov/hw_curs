from datetime import datetime
from unittest.mock import patch

import pytest

from src.utils import (
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    get_transactions,
    process_cards,
)


@pytest.mark.parametrize(
    "hour, expected",
    [
        (7, "Доброе утро!"),
        (12, "Добрый день!"),
        (17, "Добрый день!"),
        (19, "Добрый вечер!"),
        (23, "Доброй ночи!"),
        (3, "Доброй ночи!"),
    ],
)
def test_get_greeting(hour, expected):
    """Проверяет корректность приветствия в зависимости от времени."""
    date = datetime(2024, 2, 20, hour, 0, 0)
    assert get_greeting(date) == expected


def test_get_transactions():
    """Проверяет, что get_transactions возвращает список транзакций."""
    date = datetime(2024, 2, 20)
    transactions = get_transactions(date)

    assert isinstance(transactions, list)
    assert len(transactions) == 4
    assert all(isinstance(txn, dict) for txn in transactions)
    assert all("date" in txn and "amount" in txn for txn in transactions)


def test_process_cards():
    """Проверяет корректность обработки карт (сумма, кешбэк, последние 4 цифры)."""
    transactions = [
        {"card": "1234567812345814", "amount": 100},
        {"card": "1234567812345814", "amount": 200},
        {"card": "1234567812347512", "amount": 50},
    ]

    result = process_cards(transactions)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["last_digits"] == "5814"
    assert result[0]["total_spent"] == 300
    assert result[0]["cashback"] == 3.00  # 1% от 300


@patch("src.utils.requests.get")
def test_get_currency_rates(mock_get):
    """Проверяет обработку API валют, включая ошибочные ситуации."""
    mock_get.return_value.json.return_value = {"rates": {"RUB": 92.5, "EUR": 1.1}}

    result = get_currency_rates()

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == {"currency": "USD", "rate": 92.5}
    assert result[1] == {"currency": "EUR", "rate": pytest.approx(84.09, 0.1)}


@patch("src.utils.requests.get")
def test_get_currency_rates_error(mock_get):
    """Проверяет, что при ошибке API возвращается пустой список."""
    mock_get.side_effect = Exception("Ошибка сети")

    result = get_currency_rates()

    assert result == []


@patch("src.utils.requests.get")
def test_get_stock_prices(mock_get):
    """Проверяет обработку API акций."""
    mock_get.return_value.json.return_value = {
        "AAPL": {"c": 150.0},
        "AMZN": {"c": 3200.5},
    }

    result = get_stock_prices()

    assert isinstance(result, list)
    assert len(result) > 0
    assert any(stock["stock"] == "AAPL" and stock["price"] == 150.0 for stock in result)


@patch("src.utils.requests.get")
def test_get_stock_prices_error(mock_get):
    """Проверяет, что при ошибке API возвращается пустой список."""
    mock_get.side_effect = Exception("Ошибка сети")

    result = get_stock_prices()

    assert result == []
