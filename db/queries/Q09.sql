-- ============================================================================
-- Query ID: Q09
-- Problem Statement: Running total of delivered quantity per camp over time
-- Concepts Tested: Window Function SUM(...) OVER (PARTITION BY ... ORDER BY ...)
-- Expected Output Columns: camp_id, camp_name, shipment_id, shipment_date, quantity_sent, running_total_quantity
-- ============================================================================
-- Hint 1: Join relief_camp, shipment, and shipment_line filtering for delivered shipments.
-- Hint 2: Use SUM(quantity_sent) OVER (PARTITION BY camp_id ORDER BY shipment_date, shipment_id) for cumulative progression.

WITH deliveries AS (
    SELECT s.camp_id, s.shipment_id, s.shipment_date,
           SUM(sl.quantity_sent) AS quantity_sent
    FROM shipment s
    JOIN shipment_line sl USING (shipment_id)
    WHERE s.status = 'delivered'
    GROUP BY s.camp_id, s.shipment_id, s.shipment_date
)
SELECT c.camp_id, c.camp_name, d.shipment_id, d.shipment_date,
       d.quantity_sent,
       SUM(d.quantity_sent) OVER (
           PARTITION BY d.camp_id
           ORDER BY d.shipment_date, d.shipment_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total_quantity
FROM deliveries d
JOIN relief_camp c USING (camp_id)
ORDER BY c.camp_id, d.shipment_date, d.shipment_id;
