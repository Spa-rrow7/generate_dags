"""Локальный генератор DAG'ов из папки scripts/.

Запуск:  python generate_dags.py
Результат: dags/gen_<name>.py для каждого scripts/*.py и scripts/*.sql
"""

import sys
from pathlib import Path

# Чтобы import generator.* работал без установки пакета
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from generator.generator import generate_all  # noqa: E402

SCRIPTS = ROOT / "scripts"
DAGS = ROOT / "dags"


def main() -> int:
    if not SCRIPTS.exists():
        print(f"[!] Нет папки {SCRIPTS}")
        return 1

    made = generate_all(SCRIPTS, DAGS)
    if not made:
        print("[i] Нет .py/.sql файлов в scripts/")
        return 0

    for f in made:
        print(f"[+] {f.relative_to(ROOT)}")
    print(f"\nВсего DAG'ов: {len(made)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())