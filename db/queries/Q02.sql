-- ============================================================================
-- Query ID: Q02
-- Problem Statement: Total quantity of each item sent to each camp
-- Concepts Tested: Multi-table JOIN (shipment, shipment_line, relief_camp, supply_item), GROUP BY, SUM
-- Expected Output Columns: camp_id, camp_name, item_id, item_name, total_quantity_sent
-- ============================================================================
-- Hint 1: Join relief_camp to shipment, shipment_line, and supply_item.
-- Hint 2: Group by camp and item identifiers, calculating the total sum of quantity_sent.

SELECT c.camp_id, c.camp_name, i.item_id, i.item_name,
       SUM(sl.quantity_sent) AS total_quantity_sent
FROM shipment s
JOIN shipment_line sl ON sl.shipment_id = s.shipment_id
JOIN relief_camp c ON c.camp_id = s.camp_id
JOIN supply_item i ON i.item_id = sl.item_id
GROUP BY c.camp_id, c.camp_name, i.item_id, i.item_name
ORDER BY c.camp_id, i.item_id;
