import json
from datetime import datetime

import pandas as pd
import pytest

from src.views import get_greeting, main_page


@pytest.mark.parametrize(
    "input_time, expected_greeting",
    [
        (datetime(2025, 2, 8, 6, 0, 0), "Доброе утро"),
        (datetime(2025, 2, 8, 13, 0, 0), "Добрый день"),
        (datetime(2025, 2, 8, 19, 0, 0), "Добрый вечер"),
        (datetime(2025, 2, 8, 2, 0, 0), "Доброй ночи"),
    ],
)
def test_get_greeting(input_time, expected_greeting):
    assert get_greeting(input_time) == expected_greeting


def test_main_page_valid_time(mocker):

    mock_transactions = pd.DataFrame({"Сумма операции": [100, 200, 300, 400, 500]})

    mocker.patch("src.views.pd.read_excel", return_value=mock_transactions)

    response = json.loads(main_page("2025-02-08 10:30:00"))

    assert "greeting" in response
    assert "top_transactions" in response
    assert isinstance(response["top_transactions"], list)  # Проверяем, что это список
    assert len(response["top_transactions"]) > 0  # Проверяем, что есть данные


def test_main_page_invalid_time():
    response = json.loads(main_page("INVALID_DATE"))
    assert response == {"error": "Неверный формат времени"}
