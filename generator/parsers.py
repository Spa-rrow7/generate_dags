"""Парсеры исходников: .py → DagSpec, .sql → DagSpec.

Формат метаданных в исходнике (символ комментария — # или --):

    # DAG_META: name=my_etl
    # DAG_META: schedule=@daily
    # DAG_META: start_time=2026-09-10 03:00:00
    # DAG_META: conn_id=pg_extra_conn
    # DAG_META: description=...

Поля:
    name        — dag_id (по умолчанию — имя файла без расширения)
    schedule    — cron или пресет (@daily, @hourly, ...)
    start_time  — YYYY-MM-DD HH:MM:SS (по умолчанию — сегодня 00:00:00)
    conn_id     — Airflow Connection id (опционально)
    description — описание DAG'а
"""

import ast
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# Принимает и "# DAG_META: key=value", и "-- DAG_META: key=value"
META_RE = re.compile(r"^\s*(?:#|--)\s*DAG_META:\s*(\w+)\s*=\s*(.+?)\s*$")

# Режем SQL по ";" в конце строки
SQL_SPLIT_RE = re.compile(r";\s*\n")


@dataclass
class DagSpec:
    """Описание одного DAG'а, извлечённое из исходника."""

    name: str
    schedule: str
    start_time: str
    conn_id: str = ""
    description: str = ""
    kind: str = "python"                                  # 'python' | 'sql'
    module: str = ""                                      # для python-исходников
    tasks: list[dict[str, Any]] = field(default_factory=list)
    depends_on: dict[str, list[str]] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Общее
# --------------------------------------------------------------------------

def parse_meta(text: str) -> dict[str, str]:
    """Собирает все DAG_META-строки в словарь."""
    meta: dict[str, str] = {}
    for line in text.splitlines():
        m = META_RE.match(line)
        if m:
            meta[m.group(1)] = m.group(2)
    return meta


def _default_start_time() -> str:
    """Дата старта по умолчанию — день генерации, 00:00:00."""
    return datetime.now().strftime("%Y-%m-%d 00:00:00")


# --------------------------------------------------------------------------
# Python
# --------------------------------------------------------------------------

def parse_python(path: Path) -> DagSpec:
    """Парсит Python-исходник: каждая def → отдельная таска.

    Зависимости строятся по порядку определения функций:
    каждая следующая зависит от предыдущей.
    """
    src = path.read_text(encoding="utf-8")
    meta = parse_meta(src)

    tree = ast.parse(src)
    funcs: list[str] = [
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    ]

    if not funcs:
        raise ValueError(f"{path}: не найдено ни одной функции (def)")

    depends_on: dict[str, list[str]] = {
        funcs[i + 1]: [funcs[i]] for i in range(len(funcs) - 1)
    }

    return DagSpec(
        name=meta.get("name", path.stem),
        schedule=meta.get("schedule", "@daily"),
        start_time=meta.get("start_time", _default_start_time()),
        conn_id=meta.get("conn_id", ""),
        description=meta.get("description", f"Generated from {path.name}"),
        kind="python",
        module=path.stem,
        tasks=[{"id": f, "func": f} for f in funcs],
        depends_on=depends_on,
    )


# --------------------------------------------------------------------------
# SQL
# --------------------------------------------------------------------------

def parse_sql(path: Path) -> DagSpec:
    """Парсит SQL-исходник: каждая команда (до ';' в конце строки) → таска.

    Зависимости — линейная цепочка в порядке появления команд.
    """
    src = path.read_text(encoding="utf-8")
    meta = parse_meta(src)

    # Убираем мета-строки и пустые строки в начале
    body = "\n".join(
        line for line in src.splitlines() if not META_RE.match(line)
    ).strip()

    statements = [s.strip() for s in SQL_SPLIT_RE.split(body) if s.strip()]
    if not statements:
        raise ValueError(f"{path}: не найдено ни одной SQL-команды")

    tasks: list[dict[str, Any]] = []
    depends_on: dict[str, list[str]] = {}
    prev_id: str | None = None

    for i, stmt in enumerate(statements):
        first_word = stmt.split(None, 1)[0].upper() if stmt.split() else "SQL"
        task_id = f"sql_{i:02d}_{first_word.lower()}"
        tasks.append({"id": task_id, "sql": stmt})
        if prev_id:
            depends_on[task_id] = [prev_id]
        prev_id = task_id

    return DagSpec(
        name=meta.get("name", path.stem),
        schedule=meta.get("schedule", "@daily"),
        start_time=meta.get("start_time", _default_start_time()),
        conn_id=meta.get("conn_id", ""),
        description=meta.get("description", f"Generated from {path.name}"),
        kind="sql",
        tasks=tasks,
        depends_on=depends_on,
    )