"""Auto-generated DAG: my_etl. Do not edit manually.

Source: my_etl.py
Generated: 2026-09-10T19:15:54+00:00
"""
import importlib
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


with DAG(
    dag_id="my_etl",
    description="Generated from my_etl.py",
    schedule="@daily",
    start_date=datetime.strptime("2026-09-10 00:00:00", "%Y-%m-%d %H:%M:%S"),
    catchup=False,
    default_args={
        "owner": "generator",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["generated", "python"],
) as dag:
    t_extract = PythonOperator(
        task_id="extract",
        python_callable=getattr(importlib.import_module("scripts.my_etl"), "extract"),
    )
    t_transform = PythonOperator(
        task_id="transform",
        python_callable=getattr(importlib.import_module("scripts.my_etl"), "transform"),
    )
    t_load = PythonOperator(
        task_id="load",
        python_callable=getattr(importlib.import_module("scripts.my_etl"), "load"),
    )
t_extract >> t_transform
t_transform >> t_load
