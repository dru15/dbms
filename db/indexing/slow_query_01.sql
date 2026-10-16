-- ============================================================================
-- Indexing Experiment Query 1: Total Quantity Sent Per Camp and Item (Q02 benchmark)
-- Objective: Benchmark aggregations over ~1,000,000 shipment_line rows.
-- Index Type to Test: Composite B-tree vs Covering Index (INCLUDE)
-- ============================================================================

-- Benchmark Command:
-- EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    s.camp_id,
    c.camp_name,
    sl.item_id,
    i.item_name,
    SUM(sl.quantity_sent) AS total_quantity_sent
FROM relief_camp c
JOIN shipment s ON c.camp_id = s.camp_id
JOIN shipment_line sl ON s.shipment_id = sl.shipment_id
JOIN supply_item i ON sl.item_id = i.item_id
GROUP BY s.camp_id, c.camp_name, sl.item_id, i.item_name;

-- Suggested Indexes to Evaluate:
-- 1. CREATE INDEX ix_shipment_camp ON shipment(camp_id);
-- 2. CREATE INDEX ix_shipment_line_covering ON shipment_line(shipment_id, item_id) INCLUDE (quantity_sent);
