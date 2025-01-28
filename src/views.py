import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)


def get_greeting(time: datetime) -> str:
    hour = time.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates(api_key: str) -> List[Dict[str, Any]]:
    url = "https://api.currencyapi.com/v3/latest"
    params = {"apikey": api_key, "currencies": "USD,EUR"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [{"currency": k, "rate": v["value"]} for k, v in data["data"].items()]
    return []


def get_stock_prices(api_key: str) -> List[Dict[str, float]]:
    url = "https://api.stockdata.org/v1/data/quote"
    params = {"api_token": api_key, "symbols": "AAPL,AMZN,GOOGL,MSFT,TSLA"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {"stock": item["symbol"], "price": item["price"]} for item in data["data"]
        ]
    return []


def main_page(date_time: str) -> Dict[str, Any]:
    time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    greeting = get_greeting(time)

    # Загрузка данных из Excel
    transactions = pd.read_excel("data/operations.xlsx")

    # Пример обработки данных
    cards = [
        {"last_digits": "5814", "total_spent": 1262.00, "cashback": 12.62},
        {"last_digits": "7512", "total_spent": 7.94, "cashback": 0.08},
    ]

    top_transactions = transactions.nlargest(5, "amount").to_dict("records")

    # Получение курсов валют и цен на акции
    api_key = "your_api_key_here"
    currency_rates = get_currency_rates(api_key)
    stock_prices = get_stock_prices(api_key)

    return {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
