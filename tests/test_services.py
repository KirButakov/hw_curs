from datetime import datetime

import pytest

from src.services import profitable_cashback_categories


@pytest.fixture
def sample_transactions():
    return [
        {"date": "2024-07-01", "category": "Еда", "amount": 1000},
        {"date": "2024-07-01", "category": "Одежда", "amount": 2000},
        {"date": "2024-07-02", "category": "Еда", "amount": 500},
        {"date": "2024-06-30", "category": "Транспорт", "amount": 300},
    ]


def test_profitable_cashback_categories(sample_transactions):
    result = profitable_cashback_categories(sample_transactions, 2024, 7)
    assert result == {"Еда": 15.0, "Одежда": 20.0}  # 1% от суммы
