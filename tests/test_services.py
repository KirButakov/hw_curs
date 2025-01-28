import unittest

from src.services import profitable_cashback_categories


class TestServices(unittest.TestCase):
    def test_profitable_cashback_categories(self):
        data = [
            {"date": "2023-10-01", "category": "Супермаркеты", "amount": 1000},
            {"date": "2023-10-02", "category": "Топливо", "amount": 500},
        ]
        result = profitable_cashback_categories(data, 2023, 10)
        self.assertEqual(result, {"Супермаркеты": 10.0, "Топливо": 5.0})
