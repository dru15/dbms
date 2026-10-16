-- ============================================================================
-- Indexing Experiment Query 4: Multi-Column Filter and Join on Critical Requests (Q03 benchmark)
-- Objective: Benchmark anti-join subquery search over large volume of shipments.
-- Index Type to Test: Composite Index on Foreign Keys
-- ============================================================================

-- Benchmark Command:
-- EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    r.request_id,
    r.request_date,
    r.camp_id,
    rl.item_id
FROM supply_request r
JOIN request_line rl ON r.request_id = rl.request_id
WHERE r.urgency = 'critical'
  AND NOT EXISTS (
      SELECT 1 
      FROM shipment s
      JOIN shipment_line sl ON s.shipment_id = sl.shipment_id
      WHERE s.camp_id = r.camp_id
        AND sl.item_id = rl.item_id
        AND s.shipment_date >= r.request_date
  );

-- Suggested Indexes to Evaluate:
-- 1. CREATE INDEX ix_shipment_camp_date ON shipment(camp_id, shipment_date);
-- 2. CREATE INDEX ix_shipment_line_item ON shipment_line(item_id, shipment_id);
