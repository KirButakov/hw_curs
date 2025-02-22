import json
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.utils import (
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    get_transactions,
    load_user_settings,
    process_cards,
)


# Тест для функции get_greeting
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


# Тест для функции process_cards
def test_process_cards():
    """Проверяет корректность обработки карт (сумма, кешбэк, последние 4 цифры)."""
    transactions = [
        {"Номер карты": "1234567812345814", "Сумма операции": 100},
        {"Номер карты": "1234567812345814", "Сумма операции": 200},
        {"Номер карты": "1234567812347512", "Сумма операции": 50},
    ]

    result = process_cards(transactions)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["last_digits"] == "5814"
    assert result[0]["total_spent"] == 300
    assert result[0]["cashback"] == 3.00  # 1% от 300


# Тест для функции get_top_transactions
@patch("pandas.read_excel")
def test_get_top_transactions(mock_read_excel):
    """Проверяет, что get_top_transactions возвращает топ-5 транзакций."""
    mock_read_excel.return_value = pd.DataFrame(
        {
            "Сумма операции": [100, 200, 300, 400, 500, 600],
            "Номер карты": [
                "1234567812345814",
                "1234567812345814",
                "1234567812347512",
                "1234567812345814",
                "1234567812347512",
                "1234567812345814",
            ],
        }
    )

    result = get_top_transactions()

    assert isinstance(result, list)
    assert len(result) == 5
    assert all(isinstance(txn, dict) for txn in result)
    assert all("Сумма операции" in txn for txn in result)


# Тест для функции load_user_settings
def test_load_user_settings():
    """Проверяет загрузку пользовательских настроек."""
    mock_settings = '{"preferred_currency": "USD", "stocks": ["AAPL", "AMZN"]}'
    with patch("builtins.open", mock_open(read_data=mock_settings)):
        settings = load_user_settings()
        assert settings == {"preferred_currency": "USD", "stocks": ["AAPL", "AMZN"]}


# Тест для функции get_currency_rates
@patch("requests.get")
def test_get_currency_rates(mock_get):
    """Проверяет обработку API валют, включая ошибочные ситуации."""
    mock_get.return_value.json.return_value = {"rates": {"RUB": 92.5, "EUR": 0.9}}

    result = get_currency_rates()

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == {"currency": "USD", "rate": 92.5}
    assert result[1] == {"currency": "EUR", "rate": pytest.approx(102.78, 0.1)}


@patch("requests.get")
def test_get_currency_rates_error(mock_get):
    """Проверяет, что при ошибке API возвращается пустой список."""
    mock_get.side_effect = Exception("Ошибка сети")

    result = get_currency_rates()

    assert result == []


# Тест для функции get_stock_prices
@patch("requests.get")
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


@patch("requests.get")
def test_get_stock_prices_error(mock_get):
    """Проверяет, что при ошибке API возвращается пустой список."""
    mock_get.side_effect = Exception("Ошибка сети")

    result = get_stock_prices()

    assert result == []
