-- ============================================================================
-- Query ID: Q16
-- Problem Statement: Camps whose total received supply quantity is above the cross-camp average
-- Concepts Tested: Subquery in HAVING, Scalar Aggregate comparison
-- Expected Output Columns: camp_id, camp_name, total_received_quantity
-- ============================================================================
-- Hint 1: Group delivered shipment quantities by camp.
-- Hint 2: Filter groups using HAVING total > (SELECT AVG(camp_total) FROM ...).

WITH camp_totals AS (
    SELECT c.camp_id, c.camp_name,
           COALESCE(SUM(sl.quantity_sent), 0) AS total_received_quantity
    FROM relief_camp c
    LEFT JOIN shipment s ON s.camp_id = c.camp_id AND s.status = 'delivered'
    LEFT JOIN shipment_line sl USING (shipment_id)
    GROUP BY c.camp_id, c.camp_name
)
SELECT camp_id, camp_name, total_received_quantity
FROM camp_totals
WHERE total_received_quantity > (SELECT AVG(total_received_quantity) FROM camp_totals)
ORDER BY camp_id;
