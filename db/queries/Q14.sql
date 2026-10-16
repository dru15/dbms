-- ============================================================================
-- Query ID: Q14
-- Problem Statement: Total shelter capacity vs registered members per camp
-- Concepts Tested: Aggregating multiple 1:N dimensions independently via CTEs before joining
-- Expected Output Columns: camp_id, camp_name, total_shelter_capacity, total_registered_members, capacity_difference
-- ============================================================================
-- Hint 1: Avoid Cartesian fanout: compute SUM(unit_capacity) in one CTE and COUNT(member_no) in a separate CTE.
-- Hint 2: Join both CTEs back to relief_camp to calculate the net difference.

WITH shelters AS (
    SELECT camp_id, SUM(unit_capacity) AS total_shelter_capacity
    FROM shelter_unit GROUP BY camp_id
), members AS (
    SELECT f.camp_id, COUNT(m.member_no) AS total_registered_members
    FROM registered_family f
    JOIN family_member m USING (family_id)
    GROUP BY f.camp_id
)
SELECT c.camp_id, c.camp_name,
       COALESCE(s.total_shelter_capacity, 0) AS total_shelter_capacity,
       COALESCE(m.total_registered_members, 0) AS total_registered_members,
       COALESCE(s.total_shelter_capacity, 0) -
       COALESCE(m.total_registered_members, 0) AS capacity_difference
FROM relief_camp c
LEFT JOIN shelters s USING (camp_id)
LEFT JOIN members m USING (camp_id)
ORDER BY c.camp_id;
