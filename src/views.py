import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logger.error("API_KEY не задано в переменных окружения!")

CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
if not CURRENCY_API_KEY:
    logger.error("CURRENCY_API_KEY не задано в переменных окружения!")

STOCK_API_KEY = os.getenv("STOCK_API_KEY")
if not STOCK_API_KEY:
    logger.error("STOCK_API_KEY не задано в переменных окружения!")


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


def get_currency_rates() -> List[Dict[str, Any]]:
    if not API_KEY:
        logger.error("API_KEY отсутствует, невозможно запросить курсы валют.")
        return []

    with open("user_settings.json", "r") as f:
        settings = json.load(f)
        currencies = ",".join(settings["user_currencies"])

    url = "https://api.currencyapi.com/v3/latest"
    params = {"apikey": API_KEY, "currencies": currencies}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Получены курсы валют: {data}")
        return [{"currency": k, "rate": v["value"]} for k, v in data["data"].items()]
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса курсов валют: {e}")
        return []


def get_stock_prices() -> List[Dict[str, float]]:
    if not STOCK_API_KEY:
        logger.error("STOCK_API_KEY отсутствует, невозможно запросить цены акций.")
        return []

    with open("user_settings.json", "r") as f:
        settings = json.load(f)
        stocks = ",".join(settings["user_stocks"])

    url = "https://api.stockdata.org/v1/data/quote"
    params = {"api_token": STOCK_API_KEY, "symbols": stocks}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Получены цены акций: {data}")
        return [
            {"stock": item["symbol"], "price": item["price"]} for item in data["data"]
        ]
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса цен акций: {e}")
        return []


def main_page(date_time: str) -> str:
    try:
        time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logger.error(f"Ошибка преобразования времени: {e}")
        return json.dumps(
            {"error": "Неверный формат времени"}, ensure_ascii=False, indent=4
        )

    greeting = get_greeting(time)

    # Чтение настроек
    with open("user_settings.json", "r") as f:
        settings = json.load(f)
        currencies = ",".join(settings["user_currencies"])
        stocks = ",".join(settings["user_stocks"])

    # Чтение Excel файла
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "../data/operations.xlsx")

    try:
        transactions = pd.read_excel(file_path)
    except Exception as e:
        logger.error(f"Ошибка при чтении файла Excel: {e}")
        return json.dumps(
            {"error": "Не удалось загрузить данные транзакций"},
            ensure_ascii=False,
            indent=4,
        )

    top_transactions = transactions.nlargest(5, "Сумма операции").to_dict("records")

    currency_rates = get_currency_rates()
    stock_prices = get_stock_prices()

    cards_data = transactions[
        ["Номер карты", "Сумма операции", "Бонусы (включая кэшбэк)"]
    ]
    cards_data.loc[:, "last_digits"] = cards_data["Номер карты"].astype(str).str[-4:]
    cards_data.loc[:, "total_spent"] = cards_data["Сумма операции"]
    cards_data.loc[:, "cashback"] = cards_data["Бонусы (включая кэшбэк)"].fillna(0)

    cards = (
        cards_data[["last_digits", "total_spent", "cashback"]]
        .drop_duplicates()
        .to_dict("records")
    )

    return json.dumps(
        {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        },
        ensure_ascii=False,
        indent=4,
    )
