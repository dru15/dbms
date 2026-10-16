-- ============================================================================
-- Indexing Experiment Query 3: Status-Filtered Join (Q06/Q09 benchmark)
-- Objective: Benchmark partial index vs full table scan on status = 'delivered'.
-- Index Type to Test: Partial B-tree Index (WHERE status = 'delivered')
-- ============================================================================

-- Benchmark Command:
-- EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    s.camp_id,
    sl.item_id,
    SUM(sl.quantity_sent) AS delivered_qty
FROM shipment s
JOIN shipment_line sl ON s.shipment_id = sl.shipment_id
WHERE s.status = 'delivered'
GROUP BY s.camp_id, sl.item_id;

-- Suggested Indexes to Evaluate:
-- 1. CREATE INDEX ix_shipment_delivered_partial ON shipment(camp_id, shipment_id) WHERE status = 'delivered';
