-- ============================================================================
-- Query ID: Q01
-- Problem Statement: Camps where registered members exceed 90% of capacity
-- Concepts Tested: INNER JOIN, GROUP BY, Aggregate functions (COUNT), HAVING filter
-- Expected Output Columns: camp_id, camp_name, capacity, registered_members, occupancy_pct
-- ============================================================================
-- Hint 1: Join relief_camp with registered_family and family_member to aggregate members per camp.
-- Hint 2: Use the HAVING clause to filter groups where the count of members divided by camp capacity exceeds 0.90.

SELECT c.camp_id, c.camp_name, c.capacity,
       COUNT(m.member_no) AS registered_members,
       ROUND(100.0 * COUNT(m.member_no) / c.capacity, 1) AS occupancy_pct
FROM relief_camp c
JOIN registered_family f ON f.camp_id = c.camp_id
JOIN family_member m ON m.family_id = f.family_id
GROUP BY c.camp_id, c.camp_name, c.capacity
HAVING COUNT(m.member_no) > 0.90 * c.capacity
ORDER BY c.camp_id;
