import unittest
from datetime import datetime

from src.views import get_greeting


class TestViews(unittest.TestCase):
    def test_get_greeting(self):
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 8, 0)), "Доброе утро")
        self.assertEqual(get_greeting(datetime(2023, 10, 1, 14, 0)), "Добрый день")
