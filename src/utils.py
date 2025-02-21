import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, cast

import finnhub
import pandas as pd
import requests
from dotenv import load_dotenv

# Загрузка переменных окружения
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

api_key = os.getenv("EXCHANGE_API_KEY") or os.getenv("API_KEY")
finnhub_api_key = os.getenv("FINNHUB_API_KEY")


if not api_key or not finnhub_api_key:
    logging.error("Один из API-ключей не найден! Проверь .env файл.")
    raise ValueError("API-ключи не загружены")

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
    """Получает транзакции из файла operations.xlsx за период с начала месяца до указанной даты."""
    try:
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "operations.xlsx"
        )
        print(f"Загружаем файл: {file_path}")  # Отладка пути

        df = pd.read_excel(file_path)

        if "Дата операции" not in df.columns:
            raise ValueError(
                "Столбец 'Дата операции' не найден в файле operations.xlsx"
            )

        # Преобразуем даты
        df["Дата операции"] = pd.to_datetime(
            df["Дата операции"], dayfirst=True, errors="coerce"
        )

        start_of_month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        filtered_df = df[
            (df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= date)
        ]

        return cast(List[Dict[str, Any]], filtered_df.to_dict(orient="records"))
    except Exception as e:
        logging.error(f"Ошибка загрузки транзакций: {e}", exc_info=True)
        return []


# 3. Расчет данных по картам (последние 4 цифры, сумма, кешбэк)
def process_cards(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    df = pd.DataFrame(transactions)

    print("Колонки в DataFrame:", df.columns.tolist())  # Отладка

    if "Номер карты" not in df.columns:
        raise ValueError("Столбец 'Номер карты' не найден!")

    df["last_digits"] = df["Номер карты"].astype(str).str[-4:]

    grouped = (
        df.groupby("last_digits")
        .agg(total_spent=("Сумма операции", "sum"))
        .reset_index()
    )
    grouped["cashback"] = (grouped["total_spent"] * 0.01).round(2)  # 1% кешбэк

    return cast(List[Dict[str, Any]], grouped.to_dict(orient="records"))


# 4. Получение топ-5 транзакций
def get_top_transactions() -> List[Dict[str, Any]]:
    """Загружает транзакции из operations.xlsx и возвращает топ-5 по сумме."""
    try:
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "operations.xlsx"
        )
        print(f"Загружаем файл: {file_path}")  # Отладка пути

        df = pd.read_excel(file_path)

        print("Колонки в DataFrame:", df.columns.tolist())  # Отладка

        if "Сумма операции" not in df.columns:
            raise ValueError(
                "Столбец 'Сумма операции' не найден в файле operations.xlsx"
            )

        df["Сумма операции"] = pd.to_numeric(df["Сумма операции"], errors="coerce")
        return cast(
            List[Dict[str, Any]],
            df.nlargest(5, "Сумма операции").to_dict(orient="records"),
        )

    except Exception as e:
        logging.error(f"Ошибка загрузки топ-5 транзакций: {e}", exc_info=True)
        return []


# Загрузка настроек из файла user_settings.json
def load_user_settings() -> Dict[str, Any]:
    try:
        with open("user_settings.json", "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Ошибка загрузки настроек: {e}")
        return {}


# 5. Курсы валют
def get_currency_rates() -> List[Dict[str, Any]]:
    settings = load_user_settings()
    preferred_currency = settings.get("preferred_currency", "USD")

    try:
        response = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{preferred_currency}"
        )
        data = response.json()
        return [
            {"currency": preferred_currency, "rate": round(data["rates"]["RUB"], 2)},
            {
                "currency": "EUR",
                "rate": round(data["rates"]["RUB"] / data["rates"]["EUR"], 2),
            },
        ]
    except Exception as e:
        logging.error(f"Ошибка загрузки валют: {e}")
        return []


# 6. Стоимость акций
def get_stock_prices() -> List[Dict[str, Any]]:
    settings = load_user_settings()
    stocks = settings.get("stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
    api_key = os.getenv("FINNHUB_API_KEY")

    if not api_key:
        logging.error("API ключ для Finnhub не найден в переменных окружения")
        return []

    try:
        response = requests.get(
            f"https://finnhub.io/api/v1/quote?symbol={','.join(stocks)}&token={api_key}"
        )
        data = response.json()
        return [
            {"stock": stock, "price": round(data.get(stock, {}).get("c", 0), 2)}
            for stock in stocks
        ]
    except Exception as e:
        logging.error(f"Ошибка загрузки акций: {e}")
        return []
