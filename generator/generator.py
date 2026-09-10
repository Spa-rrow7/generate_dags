"""Генерация DAG-файлов из исходников в папке scripts/.

Один исходник (.py или .sql) → один DAG-файл в dags/gen_<name>.py.
Python-исходники копируются в dags/scripts/, чтобы их можно было
импортировать через import_callable("scripts.<module>", "<func>").
"""

import shutil
from pathlib import Path

from .parsers import parse_python, parse_sql
from .render import render_dag

SUPPORTED_SUFFIXES = (".py", ".sql")


def generate_one(
    src: Path,
    out_dir: Path,
    src_out_dir: Path,
    sources_root: Path,
) -> Path:
    """Сгенерировать один DAG из одного исходника.

    :param src: путь к исходнику (scripts/foo.py или scripts/bar.sql)
    :param out_dir: куда положить готовый DAG (dags/)
    :param src_out_dir: куда копировать Python-исходники (dags/scripts/)
    :param sources_root: корень исходников (scripts/) — для source_rel
    :return: путь к созданному DAG-файлу
    """
    if src.suffix == ".py":
        spec = parse_python(src)
        # Python-исходник должен быть импортируемым модулем внутри dags/.
        # Airflow добавляет dags/ в sys.path, поэтому import_callable
        # сможет сделать import scripts.<module>.
        src_out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, src_out_dir / src.name)
    elif src.suffix == ".sql":
        spec = parse_sql(src)
    else:
        raise ValueError(f"Unsupported source type: {src}")

    source_rel = str(src.relative_to(sources_root))
    text = render_dag(spec, source_rel=source_rel)

    out_file = out_dir / f"gen_{spec.name}.py"
    out_file.write_text(text, encoding="utf-8")
    return out_file


def generate_all(sources_dir: Path, dags_dir: Path) -> list[Path]:
    """Пройти по всем .py/.sql в sources_dir и сгенерировать DAG'и.

    Старые сгенерированные файлы (dags/gen_*.py) и скопированные
    исходники (dags/scripts/*) удаляются, чтобы не оставалось мусора
    от переименованных/удалённых исходников.
    """
    src_out_dir = dags_dir / "scripts"
    dags_dir.mkdir(parents=True, exist_ok=True)
    src_out_dir.mkdir(parents=True, exist_ok=True)

    # Чистим старые сгенерированные DAG'и
    for old in dags_dir.glob("gen_*.py"):
        old.unlink()

    # Чистим старые скопированные исходники
    for old in src_out_dir.glob("*"):
        if old.is_file():
            old.unlink()

    results: list[Path] = []
    for src in sorted(sources_dir.iterdir()):
        if not src.is_file():
            continue
        if src.suffix not in SUPPORTED_SUFFIXES:
            continue
        results.append(generate_one(src, dags_dir, src_out_dir, sources_dir))

    return results