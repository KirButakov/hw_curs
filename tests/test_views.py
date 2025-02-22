import json
from datetime import datetime
from unittest.mock import patch

import pytest

from src.views import home, validate_date


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("2024-02-20 15:30:00", True),  # Корректный формат
        ("2024-02-20", False),  # Нет времени
        ("20.02.2024 15:30:00", False),  # Неправильный формат
        ("2024/02/20 15:30:00", False),  # Слеши вместо дефисов
        ("invalid_date", False),  # Полностью неверное значение
    ],
)
def test_validate_date(date_str, expected):
    """Проверяет корректность валидации даты."""
    assert validate_date(date_str) == expected


@patch("src.views.get_greeting", return_value="Добрый день!")
@patch("src.views.get_transactions", return_value=[{"id": 1, "amount": 100}])
@patch("src.views.process_cards", return_value=[{"card": "Visa", "balance": 5000}])
@patch("src.views.get_top_transactions", return_value=[{"id": 1, "amount": 100}])
@patch("src.views.get_currency_rates", return_value={"USD": 92.5})
@patch("src.views.get_stock_prices", return_value={"AAPL": 150.0})
def test_home_valid(
    mock_greeting,
    mock_transactions,
    mock_process_cards,
    mock_top_transactions,
    mock_currency_rates,
    mock_stock_prices,
    capsys,
):
    """Тестирует корректный вывод функции home."""
    home("2024-02-20 15:30:00")
    captured = capsys.readouterr()

    response = json.loads(
        captured.out.split("\n🏠 Главная страница:\n")[1]  # Парсим JSON из вывода
    )

    assert response["greeting"] == "Добрый день!"
    assert response["cards"] == [{"card": "Visa", "balance": 5000}]
    assert response["top_transactions"] == [{"id": 1, "amount": 100}]
    assert response["currency_rates"] == {"USD": 92.5}
    assert response["stock_prices"] == {"AAPL": 150.0}


@patch("src.views.logging.error")
def test_home_invalid_date(mock_logging, capsys):
    """Тестирует обработку некорректного формата даты."""
    home("неправильная дата")
    captured = capsys.readouterr()

    assert "⚠ Ошибка: Некорректный формат даты." in captured.out
    mock_logging.assert_called_once_with("Некорректный формат даты: неправильная дата")


@patch("src.views.get_greeting", side_effect=Exception("Ошибка сервиса"))
@patch("src.views.logging.error")
def test_home_service_failure(mock_logging, mock_greeting, capsys):
    """Тестирует обработку ошибки при вызове внешних сервисов."""
    home("2024-02-20 15:30:00")
    captured = capsys.readouterr()

    assert "⚠ Ошибка: Ошибка сервиса" in captured.out
    mock_logging.assert_called_once_with("Ошибка обработки запроса: Ошибка сервиса")
