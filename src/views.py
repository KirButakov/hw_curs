import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Проверка наличия необходимых переменных окружения
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
    """
    Возвращает приветствие в зависимости от текущего времени.

    :param time: Время для вычисления приветствия.
    :return: Приветствие, зависящее от времени суток.
    """
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
    """
    Запрашивает курсы валют с API.

    :return: Список курсов валют с их значениями.
    """
    if not API_KEY:
        logger.error("API_KEY отсутствует, невозможно запросить курсы валют.")
        return []

    url = "https://api.currencyapi.com/v3/latest"
    params = {"apikey": API_KEY, "currencies": "USD,EUR"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Генерирует исключение для статусов 4xx/5xx
        data = response.json()
        return [{"currency": k, "rate": v["value"]} for k, v in data["data"].items()]
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса курсов валют: {e}")
        return []


def get_stock_prices() -> List[Dict[str, float]]:
    """
    Запрашивает цены акций с API.

    :return: Список акций с их текущими ценами.
    """
    if not STOCK_API_KEY:
        logger.error("STOCK_API_KEY отсутствует, невозможно запросить цены акций.")
        return []

    url = "https://api.stockdata.org/v1/data/quote"
    params = {"api_token": STOCK_API_KEY, "symbols": "AAPL,AMZN,GOOGL,MSFT,TSLA"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Генерирует исключение для статусов 4xx/5xx
        data = response.json()
        return [
            {"stock": item["symbol"], "price": item["price"]} for item in data["data"]
        ]
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса цен акций: {e}")
        return []


def main_page(date_time: str) -> Dict[str, Any]:
    """
    Генерирует данные для главной страницы с приветствием, транзакциями, курсами валют и ценами на акции.

    :param date_time: Время, по которому будет вычислено приветствие.
    :return: Словарь с данными для отображения на главной странице.
    """
    try:
        time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logger.error(f"Ошибка преобразования времени: {e}")
        return {"error": "Неверный формат времени"}

    greeting = get_greeting(time)

    # Загрузка данных из Excel
    try:
        transactions = pd.read_excel("../data/operations.xlsx")
    except Exception as e:
        logger.error(f"Ошибка при чтении файла Excel: {e}")
        return {"error": "Не удалось загрузить данные транзакций"}

    # Пример обработки данных (сортировка по 'Сумма операции')
    top_transactions = transactions.nlargest(5, "Сумма операции").to_dict("records")

    # Получение курсов валют и цен на акции
    currency_rates = get_currency_rates()
    stock_prices = get_stock_prices()

    # Данные для карточек (загружаем из файла operations.xlsx)
    # Используем столбцы: 'Номер карты', 'Сумма операции', 'Бонусы (включая кэшбэк)'
    cards = (
        transactions[["Номер карты", "Сумма операции", "Бонусы (включая кэшбэк)"]]
        .rename(
            columns={
                "Номер карты": "last_digits",
                "Сумма операции": "total_spent",
                "Бонусы (включая кэшбэк)": "cashback",
            }
        )
        .fillna({"cashback": 0})
        .to_dict("records")
    )

    return {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
