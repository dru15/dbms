-- ============================================================================
-- Indexing Experiment Query 2: Date Range Filter on Shipments (Q09/Q12 benchmark)
-- Objective: Benchmark temporal range scans on naturally ordered shipment dates.
-- Index Type to Test: BRIN Index vs standard B-tree
-- ============================================================================

-- Benchmark Command:
-- EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    s.shipment_id,
    s.shipment_date,
    s.camp_id,
    SUM(sl.quantity_sent) AS total_shipped
FROM shipment s
JOIN shipment_line sl ON s.shipment_id = sl.shipment_id
WHERE s.shipment_date BETWEEN '2026-04-01' AND '2026-06-30'
GROUP BY s.shipment_id, s.shipment_date, s.camp_id;

-- Suggested Indexes to Evaluate:
-- 1. CREATE INDEX ix_shipment_date_btree ON shipment(shipment_date);
-- 2. CREATE INDEX ix_shipment_date_brin ON shipment USING BRIN(shipment_date);
-- Note: Compare index size (\di+) and buffer reads between B-tree and BRIN!
