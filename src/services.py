import logging
from datetime import datetime
from typing import Any, Dict, List, Union

logging.basicConfig(level=logging.INFO)


def get_currency_rates() -> List[Dict[str, Any]]:
    """Функция заглушка, которая имитирует получение курсов валют"""
    return [{"currency": "USD", "rate": 90.5}, {"currency": "EUR", "rate": 98.7}]


def get_stock_prices() -> List[Dict[str, Union[str, float]]]:
    """Функция заглушка, которая имитирует получение цен акци"""
    return [{"stock": "AAPL", "price": 150.5}, {"stock": "TSLA", "price": 700.3}]
