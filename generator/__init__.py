"""Генератор DAG'ов для Airflow.

Пакет содержит:
- parsers  — разбор .py/.sql исходников в DagSpec
- render   — рендер DagSpec в текст DAG-файла через Jinja2
- generator — обход папки scripts/ и запись готовых DAG'ов в dags/
"""

from .generator import generate_all, generate_one
from .parsers import DagSpec, parse_python, parse_sql

__all__ = [
    "generate_all",
    "generate_one",
    "DagSpec",
    "parse_python",
    "parse_sql",
]