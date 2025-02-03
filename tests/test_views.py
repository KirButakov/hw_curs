import os
import sys
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.views import get_currency_rates, get_greeting, get_stock_prices, main_page


class TestViews(unittest.TestCase):

    def test_get_greeting(self):
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 8, 0)), "Доброе утро")
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 14, 0)), "Добрый день")
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 20, 0)), "Добрый вечер")
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 2, 0)), "Доброй ночи")

    @patch("requests.get")
    def test_get_currency_rates(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"USD": {"value": 1.0}, "EUR": {"value": 0.85}}
        }
        mock_get.return_value = mock_response

        result = get_currency_rates("fake_api_key")
        self.assertEqual(
            result,
            [{"currency": "USD", "rate": 1.0}, {"currency": "EUR", "rate": 0.85}],
        )

    @patch("requests.get")
    def test_get_stock_prices(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"symbol": "AAPL", "price": 150.0},
                {"symbol": "AMZN", "price": 3400.0},
            ]
        }
        mock_get.return_value = mock_response

        result = get_stock_prices("fake_api_key")
        self.assertEqual(
            result,
            [{"stock": "AAPL", "price": 150.0}, {"stock": "AMZN", "price": 3400.0}],
        )

    @patch("pandas.read_excel")
    @patch("src.views.get_currency_rates")
    @patch("src.views.get_stock_prices")
    def test_main_page(self, mock_stock_prices, mock_currency_rates, mock_read_excel):
        mock_read_excel.return_value = pd.DataFrame(
            {"Сумма операции": [100, 200, 300], "Другая колонка": [1, 2, 3]}
        )

        mock_currency_rates.return_value = [{"currency": "USD", "rate": 1.0}]
        mock_stock_prices.return_value = [{"stock": "AAPL", "price": 150.0}]

        result = main_page("2023-10-01 12:00:00")

        self.assertEqual(result["greeting"], "Добрый день")
        self.assertEqual(len(result["top_transactions"]), 3)
        self.assertEqual(result["currency_rates"], [{"currency": "USD", "rate": 1.0}])
        self.assertEqual(result["stock_prices"], [{"stock": "AAPL", "price": 150.0}])


if __name__ == "__main__":
    unittest.main()
