from datetime import datetime

import pandas as pd
import pytest

from src.reports import spending_by_category


def test_spending_by_category():

    data = pd.DataFrame(
        {
            "date": ["2023-09-01", "2023-10-01", "2023-11-01"],
            "category": ["Супермаркеты", "Супермаркеты", "Супермаркеты"],
            "amount": [100, 200, 300],
        }
    )

    # Делаем запрос на категорию "Супермаркеты" за октябрь 2023
    result = spending_by_category(data, "Супермаркеты", "2023-10-01")

    # Проверяем, что результат верный
    assert result["amount"].sum() == 200  # Только за октябрь, сумма = 200
