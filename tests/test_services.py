import json
from datetime import datetime

import pandas as pd
import pytest

from src.services import analyze_cashback_categories


@pytest.fixture
def sample_data():
    """Создает тестовые данные для кешбэк-анализа."""
    return [
        {"Дата операции": datetime(2024, 2, 10), "Категория": "Продукты", "Кэшбэк": 50},
        {"Дата операции": datetime(2024, 2, 15), "Категория": "Продукты", "Кэшбэк": 30},
        {"Дата операции": datetime(2024, 2, 20), "Категория": "Такси", "Кэшбэк": 20},
        {
            "Дата операции": datetime(2024, 1, 25),
            "Категория": "Продукты",
            "Кэшбэк": 40,
        },  # Должно быть пропущено
        {
            "Дата операции": datetime(2024, 2, 5),
            "Категория": "Развлечения",
            "Кэшбэк": None,
        },  # None кешбэк
        {
            "Дата операции": datetime(2024, 2, 28),
            "Категория": "Кафе",
            "Кэшбэк": "10",
        },  # Кэшбэк строкой
    ]


def test_analyze_cashback_categories_dataframe(sample_data):
    """Тестирует передачу данных в виде DataFrame."""
    df = pd.DataFrame(sample_data)
    result = analyze_cashback_categories(df, 2024, 2)
    parsed_result = json.loads(result)

    assert parsed_result["Продукты"] == 80
    assert parsed_result["Такси"] == 20


def test_analyze_cashback_categories_empty():
    """Тестирует обработку пустого списка."""
    result = analyze_cashback_categories([], 2024, 2)
    assert json.loads(result) == {}


def test_analyze_cashback_categories_invalid_data():
    """Тестирует обработку некорректных данных."""
    result = analyze_cashback_categories("невалидные данные", 2024, 2)
    parsed_result = json.loads(result)

    assert "error" in parsed_result
