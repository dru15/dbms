-- ============================================================================
-- Query ID: Q10
-- Problem Statement: Average days from request to first fulfilling shipment
-- Concepts Tested: CTE, MIN aggregate with date arithmetic, AVG function
-- Expected Output Columns: avg_days_to_fulfillment
-- ============================================================================
-- Hint 1: For each request_line, determine the minimum shipment_date matching camp and item on or after request_date.
-- Hint 2: Calculate the day difference for fulfilled requests, and compute the average across all pairs.

WITH first_shipments AS (
    SELECT r.request_id, rl.line_no, r.request_date,
           MIN(s.shipment_date) AS first_shipment_date
    FROM supply_request r
    JOIN request_line rl USING (request_id)
    JOIN shipment s ON s.camp_id = r.camp_id
                   AND s.shipment_date >= r.request_date
    JOIN shipment_line sl ON sl.shipment_id = s.shipment_id
                         AND sl.item_id = rl.item_id
    GROUP BY r.request_id, rl.line_no, r.request_date
)
SELECT COALESCE(ROUND(AVG(first_shipment_date - request_date), 2), 0)
       AS avg_days_to_fulfillment
FROM first_shipments;
