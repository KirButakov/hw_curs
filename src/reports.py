import json
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, TypeVar, cast

import numpy as np
import pandas as pd

T = TypeVar("T", bound=Callable[..., Any])

# Настройка логирования
logging.basicConfig(
    filename="reports.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def save_report(file_name: Optional[str] = None) -> Callable[[T], T]:
    """
    Декоратор для сохранения отчета в файл.
    """

    def decorator(func: T) -> T:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            # Преобразуем все числа в int для корректного сохранения в JSON
            if isinstance(result, dict):
                result = {
                    key: (
                        int(value)
                        if isinstance(value, (np.integer, np.int64, float))
                        else value
                    )
                    for key, value in result.items()
                }

            file = file_name or "default_report.json"
            with open(file, "w") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            logging.info(f"Отчет сохранен в файл: {file}")
            return result

        return cast(T, wrapper)

    return decorator


@save_report()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> Dict[str, Any]:
    try:
        transactions = transactions.copy()

        # Проверяем, есть ли нужные колонки
        if (
            "Дата операции" not in transactions.columns
            or "Сумма операции" not in transactions.columns
        ):
            return {
                "error": "Файл не содержит нужные колонки ('Дата операции', 'Сумма операции')"
            }

        # Преобразуем дату в формат datetime
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"], format="%d.%m.%Y", errors="coerce"
        )

        # Преобразуем сумму в float
        transactions["Сумма операции"] = pd.to_numeric(
            transactions["Сумма операции"], errors="coerce"
        ).fillna(0)

        # Если дата не задана, используем текущую
        if date is None:
            date = datetime.today().strftime("%Y-%m-%d")

        date_obj = pd.to_datetime(date)
        start_date = date_obj - timedelta(days=90)  # Анализ за последние 90 дней

        # Фильтрация по категории и диапазону дат
        filtered_data = transactions.loc[
            (transactions["Категория"].str.strip() == category.strip())
            & (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= date_obj)
        ]

        total_spent = filtered_data["Сумма операции"].sum()
        result = {
            "category": category,
            "total_spent": total_spent,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": date_obj.strftime("%Y-%m-%d"),
        }

        logging.info(
            f"Отчет по тратам в категории '{category}' с {start_date.strftime('%Y-%m-%d')} "
            f"по {date_obj.strftime('%Y-%m-%d')} успешно сформирован."
        )
        return result

    except Exception as e:
        logging.error(f"Ошибка при формировании отчета: {str(e)}")
        return {"error": str(e)}
