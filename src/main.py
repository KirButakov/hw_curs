import json
import logging
import os
from datetime import datetime
from typing import Optional

import pandas as pd

from src.reports import spending_by_category
from src.services import analyze_cashback_categories
from src.views import home, validate_date

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_data() -> Optional[pd.DataFrame]:
    """Загружает данные из файла data/operations.xlsx и приводит к нужному формату."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx")

    try:
        df = pd.read_excel(file_path, dtype=str)

        df["Дата операции"] = pd.to_datetime(
            df["Дата операции"], dayfirst=True, errors="coerce"
        )
        df["Сумма операции"] = pd.to_numeric(df["Сумма операции"], errors="coerce")
        df["Кэшбэк"] = pd.to_numeric(
            df["Кэшбэк"].str.replace(",", "."), errors="coerce"
        )

        # Оставляем нужные колонки
        df = df[["Дата операции", "Категория", "Сумма операции", "Кэшбэк"]].dropna()

        return df
    except FileNotFoundError:
        logging.error(f"Файл не найден: {file_path}")
        print(f"⚠ Ошибка: Файл {file_path} не найден.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла: {e}")
        print(f"⚠ Ошибка при загрузке данных: {e}")

    return None


def main() -> None:
    """Главная функция для запуска сервиса анализа данных."""
    print("📊 Финансовый аналитик: отчеты и кешбэк-категории")

    df = load_data()
    if df is None:
        return  # Прерываем выполнение, если данные не загрузились

    while True:
        print("\nВыберите действие:")
        print("1. Главная страница")
        print("2. Анализ кешбэка по категориям")
        print("3. Траты по категории")
        print("4. Вывести текущую дату и время")
        print("5. Выйти")

        choice = input("Введите номер действия: ").strip()

        if choice == "1":
            date_str = input("Введите дату и время (YYYY-MM-DD HH:MM:SS): ").strip()
            home(date_str)

        elif choice == "2":
            year = int(input("Введите год: "))
            month = int(input("Введите месяц: "))
            result = analyze_cashback_categories(
                df.to_dict(orient="records"), year, month
            )
            print("\n🔹 Анализ кешбэка:\n", result)

        elif choice == "3":
            category = input("Введите категорию: ")
            date = (
                input(
                    "Введите дату (YYYY-MM-DD) или оставьте пустым для текущей: "
                ).strip()
                or None
            )
            result = spending_by_category(df, category, date)
            print(
                "\n🔹 Траты по категории:\n",
                json.dumps(result, indent=4, ensure_ascii=False),
            )

        elif choice == "4":
            print("\n📅 Текущее время:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        elif choice == "5":
            print("🚪 Выход...")
            break

        else:
            print("⚠ Ошибка: выберите корректный номер.")


if __name__ == "__main__":
    main()
