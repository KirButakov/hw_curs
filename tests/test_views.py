import json
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


from views import get_currency_rates, get_greeting, get_stock_prices, main_page


class TestViews(unittest.TestCase):

    def test_get_greeting(self):
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 6, 0)), "Доброе утро")
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 13, 0)), "Добрый день")
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 20, 0)), "Добрый вечер")
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 2, 0)), "Доброй ночи")

    @patch("requests.get")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps({"user_currencies": ["USD", "EUR"]}),
    )
    def test_get_currency_rates(self, mock_file, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {
            "data": {"USD": {"value": 1.2}, "EUR": {"value": 0.9}}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_currency_rates()
        self.assertEqual(
            result, [{"currency": "USD", "rate": 1.2}, {"currency": "EUR", "rate": 0.9}]
        )

    @patch("requests.get")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps({"user_stocks": ["AAPL", "GOOGL"]}),
    )
    def test_get_stock_prices(self, mock_file, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {
            "data": [
                {"symbol": "AAPL", "price": 150},
                {"symbol": "GOOGL", "price": 2800},
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_stock_prices()
        self.assertEqual(
            result, [{"stock": "AAPL", "price": 150}, {"stock": "GOOGL", "price": 2800}]
        )

    @patch("pandas.read_excel")
    @patch("views.get_currency_rates")
    @patch("views.get_stock_prices")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}
        ),
    )  # Мокаем чтение user_settings.json
    def test_main_page(
        self, mock_open, mock_stock_prices, mock_currency_rates, mock_read_excel
    ):
        mock_read_excel.return_value = pd.DataFrame(
            {
                "Сумма операции": [100, 200, 300],
                "Номер карты": [
                    "1234567890123456",
                    "1234567890123456",
                    "1234567890123456",
                ],
                "Бонусы (включая кэшбэк)": [1, 2, 3],
            }
        )
        mock_currency_rates.return_value = [{"currency": "USD", "rate": 1.2}]
        mock_stock_prices.return_value = [{"stock": "AAPL", "price": 150}]

        result = main_page("2023-10-01 12:00:00")
        self.assertIn("Добрый день", result)
        self.assertIn("USD", result)
        self.assertIn("AAPL", result)


if __name__ == "__main__":
    unittest.main()
