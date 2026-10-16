-- ============================================================================
-- Query ID: Q04
-- Problem Statement: Donors who have shipped to every camp
-- Concepts Tested: Relational Division, GROUP BY, HAVING COUNT(DISTINCT ...)
-- Expected Output Columns: donor_id, donor_name
-- ============================================================================
-- Hint 1: Compare the number of distinct camps each donor has shipped to against the total number of camps.
-- Hint 2: Relational division can be expressed using GROUP BY donor and a subquery in HAVING.

SELECT d.donor_id, d.donor_name
FROM donor d
JOIN shipment s ON s.donor_id = d.donor_id
GROUP BY d.donor_id, d.donor_name
HAVING COUNT(DISTINCT s.camp_id) = (SELECT COUNT(*) FROM relief_camp)
ORDER BY d.donor_id;
