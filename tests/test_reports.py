import json
import os
from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.reports import save_report, spending_by_category


@pytest.fixture
def sample_transactions():
    """Создает тестовый DataFrame с транзакциями."""
    return pd.DataFrame(
        {
            "Дата операции": [
                (datetime.today() - timedelta(days=i)).strftime("%d.%m.%Y")
                for i in range(5, 100, 10)
            ],
            "Сумма операции": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
            "Категория": ["Продукты"] * 5 + ["Развлечения"] * 5,
        }
    )


def test_spending_by_category_valid(sample_transactions):
    """Тестирует корректный расчет расходов по категории."""
    result = spending_by_category(sample_transactions, "Продукты")

    assert "category" in result
    assert "total_spent" in result
    assert result["category"] == "Продукты"
    assert result["total_spent"] == 1500  # 100 + 200 + 300 + 400 + 500


def test_spending_by_category_no_category(sample_transactions):
    """Тестирует случай, когда указанной категории нет в данных."""
    result = spending_by_category(sample_transactions, "Такси")

    assert result["total_spent"] == 0


def test_spending_by_category_invalid_columns():
    """Тестирует обработку отсутствия нужных колонок."""
    df = pd.DataFrame({"Wrong Column": [1, 2, 3]})
    result = spending_by_category(df, "Продукты")

    assert "error" in result
