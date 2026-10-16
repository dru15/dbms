-- ============================================================================
-- Query ID: Q12
-- Problem Statement: Month-over-month change in shipment volume
-- Concepts Tested: Time-series aggregation, Window Function LAG() OVER (ORDER BY ...)
-- Expected Output Columns: shipment_month, monthly_shipments, previous_month_shipments, mom_change
-- ============================================================================
-- Hint 1: Truncate shipment_date to month using DATE_TRUNC('month', ...) and count shipments.
-- Hint 2: Use LAG() to access the previous month count and calculate the difference.

WITH monthly AS (
    SELECT DATE_TRUNC('month', shipment_date)::date AS shipment_month,
           COUNT(*) AS monthly_shipments
    FROM shipment
    GROUP BY DATE_TRUNC('month', shipment_date)::date
)
SELECT shipment_month, monthly_shipments,
       LAG(monthly_shipments) OVER (ORDER BY shipment_month)
           AS previous_month_shipments,
       monthly_shipments - LAG(monthly_shipments) OVER (ORDER BY shipment_month)
           AS mom_change
FROM monthly
ORDER BY shipment_month;
