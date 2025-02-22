import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Union

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    filename="cashback.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def analyze_cashback_categories(
    data: Union[List[Dict[str, Any]], pd.DataFrame], year: int, month: int
) -> str:
    """Анализирует категории кешбэка за заданный месяц и год."""
    try:
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")

        if not isinstance(data, list) or not all(
            isinstance(item, dict) for item in data
        ):
            raise ValueError("Некорректный формат данных: должен быть список словарей")

        cashback_summary: Dict[str, float] = defaultdict(float)

        logging.info(
            f"Начат анализ кешбэка за {year}-{month}. Всего записей: {len(data)}"
        )
        print(f"\n🔍 Анализ кешбэка за {year}-{month:02d}")

        formatted_month = f"{month:02d}"  # Преобразуем месяц в строку с ведущим нулем

        for transaction in data:
            try:
                date = transaction["Дата операции"]

                if date.year == year and f"{date.month:02d}" == formatted_month:
                    category = transaction.get("Категория", "Неизвестно")
                    cashback = pd.to_numeric(
                        transaction.get("Кэшбэк", 0), errors="coerce"
                    )
                    cashback_summary[category] += cashback if pd.notna(cashback) else 0
            except (ValueError, KeyError) as e:
                logging.warning(
                    f"Ошибка обработки транзакции: {transaction}, Ошибка: {e}"
                )

        result = json.dumps(dict(cashback_summary), indent=4, ensure_ascii=False)
        logging.info(f"Кешбэк-анализ успешно выполнен для {year}-{month}")
        return result

    except Exception as e:
        logging.error(f"Ошибка в analyze_cashback_categories: {e}")
        return json.dumps(
            {"error": "Ошибка обработки данных"}, indent=4, ensure_ascii=False
        )
