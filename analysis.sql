-- SQLite dialect. `facts` is created by analysis.py / analysis.ipynb after validation.
-- Each query starts with a "-- name:" line and ends with a semicolon.

-- name: supplier_kpis
SELECT supplier,
       COUNT(*) AS orders,
       100.0*AVG(otif) AS otif_pct,
       100.0*SUM(delivered_units)/SUM(ordered_units) AS fill_rate_pct,
       SUM(CASE WHEN coverage_days < 7 THEN 1 ELSE 0 END) AS low_coverage_snapshots,
       AVG(late_days) AS mean_late_days
FROM facts
GROUP BY supplier
ORDER BY supplier;

-- name: failure_modes
SELECT supplier,
       SUM(CASE WHEN actual_days > promised_days THEN 1 ELSE 0 END) AS late_orders,
       SUM(CASE WHEN delivered_units < ordered_units THEN 1 ELSE 0 END) AS short_orders,
       SUM(CASE WHEN actual_days > promised_days AND delivered_units < ordered_units THEN 1 ELSE 0 END) AS late_and_short
FROM facts
GROUP BY supplier
ORDER BY supplier;

-- name: monthly_otif
SELECT substr(date, 1, 7) AS month,
       COUNT(*) AS orders,
       ROUND(100.0*AVG(otif), 2) AS otif_pct
FROM facts
GROUP BY month
ORDER BY month;

-- name: lowest_coverage_orders
SELECT po_id, supplier, stock_units, daily_demand,
       ROUND(1.0*stock_units/daily_demand, 2) AS coverage_days
FROM facts
ORDER BY coverage_days, po_id
LIMIT 10;
