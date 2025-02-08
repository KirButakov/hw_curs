import logging
import os
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

logging.basicConfig(level=logging.INFO)


def report_decorator(file_path: Optional[str] = None) -> Callable[..., Any]:
    """
    Декоратор для логирования выполнения функции с возможностью записи в файл.


    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logging.info(
                f"Запуск функции {func.__name__} с аргументами {args} и {kwargs}"
            )
            result = func(*args, **kwargs)
            logging.info(f"Функция {func.__name__} завершена с результатом {result}")

            # Используем путь к файлу, если он передан, иначе создаем файл по умолчанию
            log_file = file_path or f"report_{func.__name__}.log"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"Функция {func.__name__} выполнена. Результат: {result}\n")

            return result

        return wrapper

    return decorator


@report_decorator()  # Использует файл по умолчанию
def profitable_cashback_categories(
    data: List[Dict[str, Any]], year: int, month: int
) -> Dict[str, float]:
    """Вычисляет сумму кэшбэка по категориям за указанный месяц и год."""
    result: Dict[str, float] = {}

    for transaction in data:
        try:
            date = pd.to_datetime(
                transaction["Дата операции"],
                format="%d.%m.%Y %H:%M:%S",
                errors="coerce",
            )
            if pd.isna(date):
                logging.warning(
                    f"Пропущена транзакция с некорректной датой: {transaction}"
                )
                continue

            # Проверяем, что транзакция за указанный год и месяц
            if date.year == year and date.month == month:
                category = transaction["Категория"]
                amount = transaction["Сумма операции"]

                # Кэшбэк только для положительных сумм
                if amount > 0:
                    cashback = amount * 0.01  # 1% кэшбэка
                else:
                    cashback = 0

                # Добавляем кэшбэк в результат
                result[category] = result.get(category, 0) + cashback

        except (KeyError, ValueError) as e:
            logging.warning(f"Ошибка в данных транзакции: {transaction} - {e}")
    return result
