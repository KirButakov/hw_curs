from src.reports import profitable_cashback_categories, report_decorator


def test_report_decorator(mocker):
    mock_func = mocker.Mock(return_value="test_result")
    mock_func.__name__ = "mock_function"

    decorated_func = report_decorator("test.log")(mock_func)
    result = decorated_func()

    assert result == "test_result"


def test_profitable_cashback_categories():
    data = [
        {
            "Дата операции": "01.01.2018 12:00:00",
            "Категория": "Продукты",
            "Сумма операции": 1000,
        },
        {
            "Дата операции": "01.01.2018 12:00:00",
            "Категория": "Транспорт",
            "Сумма операции": -500,
        },
    ]
    result = profitable_cashback_categories(data, 2018, 1)
    assert result == {"Продукты": 10.0, "Транспорт": 0}
