import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO)


def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """Фильтрует траты по заданной категории за текущий месяц."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        logging.error(f"Некорректный формат даты: {date}")
        return pd.DataFrame()

    start_of_month = datetime(end_date.year, end_date.month, 1)
    end_of_month = datetime(end_date.year, end_date.month, 1) + timedelta(days=30)

    # Преобразуем колонку с датами
    transactions["date"] = pd.to_datetime(
        transactions["date"], format="%Y-%m-%d", errors="coerce"
    )

    # Фильтрация по диапазону дат и категории
    filtered = transactions[
        (transactions["date"] >= start_of_month)
        & (transactions["date"] <= end_of_month)
        & (transactions["category"] == category)
    ]
    return filtered
