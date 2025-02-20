import json
import logging
from datetime import datetime

from src.utils import (
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    get_transactions,
    process_cards,
)

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False


def home(date_str: str) -> None:
    print(f"DEBUG: Получена дата - {date_str}")

    if not validate_date(date_str):
        logging.error(f"Некорректный формат даты: {date_str}")
        print("⚠ Ошибка: Некорректный формат даты. Используйте YYYY-MM-DD HH:MM:SS")
        return

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        greeting = get_greeting(date)
        transactions = get_transactions(date)
        cards = process_cards(transactions)
        top_transactions = get_top_transactions(transactions)
        currency_rates = get_currency_rates()
        stock_prices = get_stock_prices()

        response = {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        print("\n🏠 Главная страница:")
        print(json.dumps(response, indent=4, ensure_ascii=False))

    except Exception as e:
        logging.error(f"Ошибка обработки запроса: {e}")
        print(f"⚠ Ошибка: {e}")
