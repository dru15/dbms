-- ============================================================================
-- Query ID: Q13
-- Problem Statement: Items requested but never shipped anywhere
-- Concepts Tested: Set Difference, LEFT JOIN ... WHERE ... IS NULL or NOT IN
-- Expected Output Columns: item_id, item_name, category
-- ============================================================================
-- Hint 1: Identify items present in request_line that have zero appearances in shipment_line.
-- Hint 2: A LEFT JOIN from supply_item with an IS NULL condition or NOT EXISTS works cleanly.

SELECT i.item_id, i.item_name, i.category
FROM supply_item i
WHERE EXISTS (SELECT 1 FROM request_line rl WHERE rl.item_id = i.item_id)
  AND NOT EXISTS (SELECT 1 FROM shipment_line sl WHERE sl.item_id = i.item_id)
ORDER BY i.item_id;
