import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO)


def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    end_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=90)

    transactions["date"] = pd.to_datetime(transactions["date"], format="%Y-%m-%d")

    start_of_month = datetime(end_date.year, end_date.month, 1)
    end_of_month = datetime(end_date.year, end_date.month, 1) + timedelta(days=30)

    filtered = transactions[
        (transactions["date"] >= start_of_month)
        & (transactions["date"] <= end_of_month)
        & (transactions["category"] == category)
    ]
    return filtered
