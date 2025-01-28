import json
import logging
from datetime import datetime
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)


def profitable_cashback_categories(
    data: List[Dict[str, Any]], year: int, month: int
) -> Dict[str, float]:
    result: Dict[str, float] = {}
    for transaction in data:
        date = datetime.strptime(transaction["date"], "%Y-%m-%d")
        if date.year == year and date.month == month:
            category = transaction["category"]
            amount = transaction["amount"]
            cashback = amount * 0.01
            result[category] = result.get(category, 0) + cashback
    return result
