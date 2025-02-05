from datetime import datetime
from unittest.mock import patch

import pandas as pd


from src.views import get_currency_rates, get_greeting, get_stock_prices, main_page


def test_get_greeting():
    # Тестируем утро
    assert get_greeting(datetime(2024, 1, 1, 6, 0)) == "Доброе утро"
    # Тестируем день
    assert get_greeting(datetime(2024, 1, 1, 14, 0)) == "Добрый день"
    # Тестируем вечер
    assert get_greeting(datetime(2024, 1, 1, 20, 0)) == "Добрый вечер"
    # Тестируем ночь
    assert get_greeting(datetime(2024, 1, 1, 2, 0)) == "Доброй ночи"


def test_get_currency_rates(requests_mock):
    # Мокируем API для курсов валют
    api_key = "test_api_key"
    mock_response = {
        "data": {
            "USD": {"value": 75.0},
            "EUR": {"value": 85.0},
        }
    }
    requests_mock.get(
        "https://api.currencyapi.com/v3/latest",
        json=mock_response,
        status_code=200,
    )

    # Тестируем функцию
    with patch.dict("os.environ", {"API_KEY": api_key}):
        result = get_currency_rates()
        assert result == [
            {"currency": "USD", "rate": 75.0},
            {"currency": "EUR", "rate": 85.0},
        ]


def test_get_stock_prices(requests_mock):
    # Мокируем API для цен акций
    api_key = "test_api_key"
    mock_response = {
        "data": [
            {"symbol": "AAPL", "price": 150.0},
            {"symbol": "GOOGL", "price": 2800.0},
        ]
    }
    requests_mock.get(
        "https://api.stockdata.org/v1/data/quote",
        json=mock_response,
        status_code=200,
    )

    # Тестируем функцию
    with patch.dict("os.environ", {"API_KEY": api_key}):
        result = get_stock_prices()
        assert result == [
            {"stock": "AAPL", "price": 150.0},
            {"stock": "GOOGL", "price": 2800.0},
        ]


def test_main_page():
    # Мокируем данные из Excel
    mock_data = pd.DataFrame(
        {
            "Номер карты": ["*7197", "*1234"],
            "Сумма операции": [100.0, 200.0],
            "Бонусы (включая кэшбэк)": [1.0, 2.0],
            "Сумма операции": [100.0, 200.0],  # Для top_transactions
        }
    )

    with patch("pandas.read_excel", return_value=mock_data):
        result = main_page("2024-01-01 12:00:00")

        # Проверяем структуру результата
        assert "greeting" in result
        assert "cards" in result
        assert "top_transactions" in result
        assert "currency_rates" in result
        assert "stock_prices" in result

        # Проверяем данные для карточек
        assert result["cards"] == [
            {"last_digits": "*7197", "total_spent": 100.0, "cashback": 1.0},
            {"last_digits": "*1234", "total_spent": 200.0, "cashback": 2.0},
        ]
