-- ============================================================================
-- Query ID: Q06
-- Problem Statement: Unmet demand per camp and item: requested minus delivered, only positive
-- Concepts Tested: Common Table Expressions (CTEs), FULL OUTER JOIN / COALESCE, Arithmetic difference
-- Expected Output Columns: camp_id, camp_name, item_id, item_name, qty_requested, qty_delivered, unmet_quantity
-- ============================================================================
-- Hint 1: Calculate total requested quantity and total delivered quantity in separate CTEs.
-- Hint 2: Join the CTEs and compute (qty_requested - qty_delivered), keeping only rows where the difference is strictly positive.

WITH requested AS (
    SELECT r.camp_id, rl.item_id, SUM(rl.qty_requested) AS qty_requested
    FROM supply_request r
    JOIN request_line rl ON rl.request_id = r.request_id
    GROUP BY r.camp_id, rl.item_id
), delivered AS (
    SELECT s.camp_id, sl.item_id, SUM(sl.quantity_sent) AS qty_delivered
    FROM shipment s
    JOIN shipment_line sl ON sl.shipment_id = s.shipment_id
    WHERE s.status = 'delivered'
    GROUP BY s.camp_id, sl.item_id
), demand AS (
    SELECT COALESCE(r.camp_id, d.camp_id) AS camp_id,
           COALESCE(r.item_id, d.item_id) AS item_id,
           COALESCE(r.qty_requested, 0) AS qty_requested,
           COALESCE(d.qty_delivered, 0) AS qty_delivered
    FROM requested r
    FULL OUTER JOIN delivered d USING (camp_id, item_id)
)
SELECT c.camp_id, c.camp_name, i.item_id, i.item_name,
       x.qty_requested, x.qty_delivered,
       x.qty_requested - x.qty_delivered AS unmet_quantity
FROM demand x
JOIN relief_camp c USING (camp_id)
JOIN supply_item i USING (item_id)
WHERE x.qty_requested > x.qty_delivered
ORDER BY c.camp_id, i.item_id;
