import json
import logging
import os
from datetime import datetime

import pandas as pd
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


def main_page(date_time: str) -> str:
    try:
        time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logger.error(f"Ошибка преобразования времени: {e}")
        return json.dumps(
            {"error": "Неверный формат времени"}, ensure_ascii=False, indent=4
        )

    greeting = get_greeting(time)

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

    return json.dumps(
        {
            "greeting": greeting,
            "top_transactions": top_transactions,
        },
        ensure_ascii=False,
        indent=4,
    )
