from datetime import datetime

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def transactions_df():
    return pd.DataFrame(
        [
            {"date": "2024-07-01", "category": "Еда", "amount": 1000},
            {"date": "2024-07-02", "category": "Одежда", "amount": 2000},
            {"date": "2024-06-30", "category": "Транспорт", "amount": 300},
            {"date": "2024-07-03", "category": "Еда", "amount": 500},
        ]
    )


def test_spending_by_category(transactions_df):
    filtered = spending_by_category(transactions_df, "Еда", "2024-07-10")
    assert len(filtered) == 2
    assert filtered["amount"].sum() == 1500
