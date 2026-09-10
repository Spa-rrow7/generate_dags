-- DAG_META: name=orders_agg
-- DAG_META: schedule=0 6 * * *
-- DAG_META: start_time=2026-09-10 06:00:00
-- DAG_META: conn_id=pg_extra_conn
-- DAG_META: description=Агрегация заказов за день

CREATE TABLE IF NOT EXISTS orders_daily (
    order_date date PRIMARY KEY,
    cnt        int,
    total_sum  numeric(14,2)
);

CREATE TABLE IF NOT EXISTS orders (
    id          serial PRIMARY KEY,
    amount      numeric(14,2),
    created_at  timestamp NOT NULL DEFAULT now()
);

DELETE FROM orders_daily
WHERE order_date = CURRENT_DATE;

INSERT INTO orders_daily (order_date, cnt, total_sum)
SELECT CURRENT_DATE, COUNT(*), COALESCE(SUM(amount), 0)
FROM orders
WHERE created_at::date = CURRENT_DATE;

SELECT order_date, cnt, total_sum
FROM orders_daily
WHERE order_date = CURRENT_DATE;