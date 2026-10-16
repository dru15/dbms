-- ============================================================================
-- Query ID: Q03
-- Problem Statement: Pending critical requests with no later shipment of the same item to that camp
-- Concepts Tested: Anti-join / Correlated Subquery with NOT EXISTS, Date comparison
-- Expected Output Columns: request_id, request_date, camp_id, camp_name, item_id, item_name, urgency
-- ============================================================================
-- Hint 1: Filter supply_request for urgency = 'critical'.
-- Hint 2: Use NOT EXISTS to verify there are no matching shipments to the same camp on or after the request date.

SELECT r.request_id, r.request_date, c.camp_id, c.camp_name,
       i.item_id, i.item_name, r.urgency
FROM supply_request r
JOIN request_line rl ON rl.request_id = r.request_id
JOIN relief_camp c ON c.camp_id = r.camp_id
JOIN supply_item i ON i.item_id = rl.item_id
WHERE r.urgency = 'critical'
  AND NOT EXISTS (
      SELECT 1 FROM shipment s
      JOIN shipment_line sl ON sl.shipment_id = s.shipment_id
      WHERE s.camp_id = r.camp_id AND sl.item_id = rl.item_id
        AND s.shipment_date >= r.request_date
  )
ORDER BY r.request_id, i.item_id;
