import logging
from datetime import datetime
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)


def profitable_cashback_categories(
    data: List[Dict[str, Any]], year: int, month: int
) -> Dict[str, float]:
    """Вычисляет сумму кэшбэка по категориям за указанный месяц и год."""
    result: Dict[str, float] = {}
    for transaction in data:
        try:
            date = datetime.strptime(transaction["date"], "%Y-%m-%d")
            if date.year == year and date.month == month:
                category = transaction["category"]
                amount = transaction["amount"]
                cashback = amount * 0.01  # 1% кэшбэка
                result[category] = result.get(category, 0) + cashback
        except (KeyError, ValueError) as e:
            logging.warning(f"Ошибка в данных транзакции: {transaction} - {e}")
    return result
