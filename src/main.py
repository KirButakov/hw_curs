import logging

import pandas as pd

from reports import profitable_cashback_categories
from services import get_currency_rates, get_stock_prices
from views import main_page

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        # Загрузка данных
        transactions = pd.read_excel("../data/operations.xlsx")

        # Преобразуем "Дата операции" в datetime, с проверкой на ошибки
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
        )

        # Проверяем на некорректные даты
        invalid_dates = transactions[transactions["Дата операции"].isna()]
        if not invalid_dates.empty:
            logging.warning(f"Некорректные строки с датами:\n{invalid_dates}")

        # Удаляем строки с пустыми значениями в столбце "Категория"
        transactions = transactions.dropna(subset=["Категория"])

        # Преобразуем данные в список словарей и передаем в функцию
        result = profitable_cashback_categories(
            transactions.to_dict("records"), 2018, 1
        )

        # Вызов функций "Веб страницы" и "Сервисы"
        print(main_page("2025-02-08 10:30:00"))
        print(get_currency_rates())
        print(get_stock_prices())

        # Вывод результата
        logging.info(
            f"Функция profitable_cashback_categories завершена с результатом {result}"
        )
        print(result)

    except Exception as e:
        logging.error(f"Ошибка при загрузке данных: {e}")
