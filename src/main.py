import logging

import pandas as pd

from reports import profitable_cashback_categories

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

        # Удаляем строки с пустыми или NaN значениями в столбце "Категория"
        transactions = transactions.dropna(subset=["Категория"])

        # Преобразуем данные в список словарей и передаем в функцию
        result = profitable_cashback_categories(
            transactions.to_dict("records"), 2018, 1
        )

        # Выводим результат
        logging.info(
            f"Функция profitable_cashback_categories завершена с результатом {result}"
        )
        print(result)

    except Exception as e:
        logging.error(f"Ошибка при загрузке данных: {e}")
