import unittest


from src.reports import profitable_cashback_categories, report_decorator


class TestReports(unittest.TestCase):

    def test_profitable_cashback_categories(self):
        data = [
            {
                "Дата операции": "01.10.2023 12:00:00",
                "Категория": "Еда",
                "Сумма операции": 1000,
            },
            {
                "Дата операции": "02.10.2023 12:00:00",
                "Категория": "Транспорт",
                "Сумма операции": 500,
            },
            {
                "Дата операции": "03.10.2023 12:00:00",
                "Категория": "Еда",
                "Сумма операции": 2000,
            },
        ]
        result = profitable_cashback_categories(data, 2023, 10)
        self.assertEqual(result, {"Еда": 30.0, "Транспорт": 5.0})

    def test_report_decorator(self):
        @report_decorator
        def dummy_function(x):
            return x * 2

        with self.assertLogs(level="INFO") as log:
            result = dummy_function(5)
            self.assertEqual(result, 10)
            self.assertIn("Запуск функции dummy_function", log.output[0])
            self.assertIn(
                "Функция dummy_function завершена с результатом 10", log.output[1]
            )


if __name__ == "__main__":
    unittest.main()
