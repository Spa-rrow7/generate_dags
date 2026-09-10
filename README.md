# Генератор DAG'ов для Airflow

## Что это
Локальный генератор, который превращает .py и .sql-скрипты из папки `scripts/`
в готовые Airflow DAG'и в папке `dags/`.

## Как работает
1. Кладём исходник в `scripts/` с шапкой `DAG_META`.
2. Запускаем `python generate_dags.py`.
3. Airflow подхватывает DAG'и из `dags/`.

## Ключевые решения
- **Декларативность:** метаданные DAG'а (name, schedule, start_time, conn_id)
  задаются прямо в исходнике.
- **Авто-деление на таски:** каждая `def` → PythonOperator,
  каждая SQL-команда → SQLExecuteQueryOperator.
- **Безопасность:** параметры подключений — в Airflow Connections,
  в DAG'е только `conn_id`.
- **Шаблоны Jinja2:** структура DAG'а описана в шаблонах,
  генератор не «склеивает строки».
- **Идемпотентность:** повторный запуск полностью пересобирает `dags/`.

## Запуск
1. Создать виртуальное окружение
Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```
2. Установить зависимости генератора

Виртуальное окружение используется только для локального запуска generate_dags.py.

Установить необходимые зависимости генератора:
```bash
pip install jinja2
```
3. Сгенерировать DAG
```
python generate_dags.py
```
4. Запустить Airflow
```
docker compose up -d
```
**При сборке Docker-окружения зависимости из ```requirements.txt``` устанавливаются в контейнер Airflow.**
# http://localhost:8080 (airflow/airflow)