"""Auto-generated DAG: orders_agg. Do not edit manually.

Source: orders_agg.sql
Generated: 2026-09-10T19:15:54+00:00
"""
import importlib
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


with DAG(
    dag_id="orders_agg",
    description="\u0410\u0433\u0440\u0435\u0433\u0430\u0446\u0438\u044f \u0437\u0430\u043a\u0430\u0437\u043e\u0432 \u0437\u0430 \u0434\u0435\u043d\u044c",
    schedule="0 6 * * *",
    start_date=datetime.strptime("2026-09-10 06:00:00", "%Y-%m-%d %H:%M:%S"),
    catchup=False,
    default_args={
        "owner": "generator",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["generated", "sql"],
) as dag:
    t_sql_00_create = SQLExecuteQueryOperator(
        task_id="sql_00_create",
        conn_id="pg_extra_conn",
        sql=r"""
        CREATE TABLE IF NOT EXISTS orders_daily (
            order_date date PRIMARY KEY,
            cnt        int,
            total_sum  numeric(14,2)
        )
        """,
    )
    t_sql_01_create = SQLExecuteQueryOperator(
        task_id="sql_01_create",
        conn_id="pg_extra_conn",
        sql=r"""
        CREATE TABLE IF NOT EXISTS orders (
            id          serial PRIMARY KEY,
            amount      numeric(14,2),
            created_at  timestamp NOT NULL DEFAULT now()
        )
        """,
    )
    t_sql_02_delete = SQLExecuteQueryOperator(
        task_id="sql_02_delete",
        conn_id="pg_extra_conn",
        sql=r"""
        DELETE FROM orders_daily
        WHERE order_date = CURRENT_DATE
        """,
    )
    t_sql_03_insert = SQLExecuteQueryOperator(
        task_id="sql_03_insert",
        conn_id="pg_extra_conn",
        sql=r"""
        INSERT INTO orders_daily (order_date, cnt, total_sum)
        SELECT CURRENT_DATE, COUNT(*), COALESCE(SUM(amount), 0)
        FROM orders
        WHERE created_at::date = CURRENT_DATE
        """,
    )
    t_sql_04_select = SQLExecuteQueryOperator(
        task_id="sql_04_select",
        conn_id="pg_extra_conn",
        sql=r"""
        SELECT order_date, cnt, total_sum
        FROM orders_daily
        WHERE order_date = CURRENT_DATE;
        """,
    )
t_sql_00_create >> t_sql_01_create
t_sql_01_create >> t_sql_02_delete
t_sql_02_delete >> t_sql_03_insert
t_sql_03_insert >> t_sql_04_select
