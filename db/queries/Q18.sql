-- ============================================================================
-- Query ID: Q18
-- Problem Statement: Donors with shipments in every month of the operational seed period
-- Concepts Tested: Relational Division, COUNT(DISTINCT DATE_TRUNC('month', ...))
-- Expected Output Columns: donor_id, donor_name, distinct_months_count
-- ============================================================================
-- Hint 1: Extract distinct months from shipment_date per donor.
-- Hint 2: Use HAVING COUNT(DISTINCT month) = 9 (the total number of operational months).

SELECT d.donor_id, d.donor_name,
       COUNT(DISTINCT DATE_TRUNC('month', s.shipment_date)) AS distinct_months_count
FROM donor d
JOIN shipment s USING (donor_id)
GROUP BY d.donor_id, d.donor_name
HAVING COUNT(DISTINCT DATE_TRUNC('month', s.shipment_date)) = 9
ORDER BY d.donor_id;
