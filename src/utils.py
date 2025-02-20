import json
import logging
from datetime import datetime
from typing import Any, Dict, List, cast

import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# 1. Приветствие
def get_greeting(date: datetime) -> str:
    hour = date.hour
    if 6 <= hour < 12:
        return "Доброе утро!"
    elif 12 <= hour < 18:
        return "Добрый день!"
    elif 18 <= hour < 23:
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


# 2. Получение транзакций
def get_transactions(date: datetime) -> List[Dict[str, Any]]:
    """Имитация получения списка транзакций"""
    transactions = [
        {
            "date": date.strftime("%Y-%m-%d"),
            "card": "1234567812345814",
            "amount": 1200,
            "category": "Супермаркеты",
        },
        {
            "date": date.strftime("%Y-%m-%d"),
            "card": "1234567812347512",
            "amount": 300,
            "category": "Транспорт",
        },
        {
            "date": date.strftime("%Y-%m-%d"),
            "card": "1234567812345814",
            "amount": 62,
            "category": "Фастфуд",
        },
        {
            "date": date.strftime("%Y-%m-%d"),
            "card": "1234567812347512",
            "amount": 7.94,
            "category": "Кино",
        },
    ]
    return transactions


# 3. Расчет данных по картам (последние 4 цифры, сумма, кешбэк)
def process_cards(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    df = pd.DataFrame(transactions)

    # Добавляем столбец с последними 4 цифрами карты
    df["last_digits"] = df["card"].str[-4:]

    # Группируем по карте, считаем сумму расходов и кешбэк
    grouped = df.groupby("last_digits").agg(total_spent=("amount", "sum")).reset_index()
    grouped["cashback"] = (grouped["total_spent"] * 0.01).round(2)  # 1% кешбэк

    return cast(List[Dict[str, Any]], grouped.to_dict(orient="records"))


# 4. Получение топ-5 транзакций
def get_top_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    df = pd.DataFrame(transactions)
    return cast(
        List[Dict[str, Any]], df.nlargest(5, "amount").to_dict(orient="records")
    )


# 5. Курсы валют (реальное API)
def get_currency_rates() -> List[Dict[str, Any]]:
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        data = response.json()
        return [
            {"currency": "USD", "rate": round(data["rates"]["RUB"], 2)},
            {
                "currency": "EUR",
                "rate": round(data["rates"]["RUB"] / data["rates"]["EUR"], 2),
            },
        ]
    except Exception as e:
        logging.error(f"Ошибка загрузки валют: {e}")
        return []


# 6. Стоимость акций из S&P500
def get_stock_prices() -> List[Dict[str, Any]]:
    stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    try:
        response = requests.get(
            f"https://finnhub.io/api/v1/quote?symbol={','.join(stocks)}&token=YOUR_API_KEY"
        )
        data = response.json()
        return [
            {"stock": stock, "price": round(data.get(stock, {}).get("c", 0), 2)}
            for stock in stocks
        ]
    except Exception as e:
        logging.error(f"Ошибка загрузки акций: {e}")
        return []
