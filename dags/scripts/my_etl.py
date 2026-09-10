import logging
import random

log = logging.getLogger(__name__)


def extract():
    """Имитация выгрузки данных из источника."""
    log.info("extract: начало выгрузки")
    rows = [{"id": i, "value": random.randint(1, 100)} for i in range(1, 11)]
    log.info("extract: получено %d строк", len(rows))
    return rows


def transform(rows=None):
    """Нормализация: обнуляем отрицательные значения."""
    log.info("transform: начало преобразования")
    if rows is None:
        rows = []
    cleaned = [{"id": r["id"], "value": max(r["value"], 0)} for r in rows]
    log.info("transform: обработано %d строк", len(cleaned))
    return cleaned


def load(rows=None):
    """Загрузка результата в целевую таблицу."""
    log.info("load: запись %d строк", len(rows or []))