-- ============================================================================
-- Query ID: Q17
-- Problem Statement: Items that were requested or shipped but not both
-- Concepts Tested: Symmetric Difference, FULL OUTER JOIN / UNION / EXCEPT
-- Expected Output Columns: item_id, item_name, activity_type
-- ============================================================================
-- Hint 1: Find items in request_line and items in shipment_line.
-- Hint 2: Return items that appear in one set but not both, labeling their activity status.

WITH requested_only AS (
    SELECT item_id FROM request_line
    EXCEPT
    SELECT item_id FROM shipment_line
), shipped_only AS (
    SELECT item_id FROM shipment_line
    EXCEPT
    SELECT item_id FROM request_line
), activity AS (
    SELECT item_id, 'requested_only' AS activity_type FROM requested_only
    UNION ALL
    SELECT item_id, 'shipped_only' AS activity_type FROM shipped_only
)
SELECT i.item_id, i.item_name, a.activity_type
FROM activity a
JOIN supply_item i USING (item_id)
ORDER BY i.item_id;
