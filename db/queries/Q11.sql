-- ============================================================================
-- Query ID: Q11
-- Problem Statement: Per camp: count of vulnerable children under 5 and elders over 60
-- Concepts Tested: Conditional Aggregation using FILTER (WHERE ...) or CASE WHEN
-- Expected Output Columns: camp_id, camp_name, children_under_5, elders_over_60
-- ============================================================================
-- Hint 1: Join relief_camp with registered_family and family_member.
-- Hint 2: Use COUNT(*) FILTER (WHERE age < 5) and COUNT(*) FILTER (WHERE age > 60) grouped by camp.

SELECT c.camp_id, c.camp_name,
       COUNT(m.member_no) FILTER (WHERE m.age < 5) AS children_under_5,
       COUNT(m.member_no) FILTER (WHERE m.age > 60) AS elders_over_60
FROM relief_camp c
LEFT JOIN registered_family f USING (camp_id)
LEFT JOIN family_member m USING (family_id)
GROUP BY c.camp_id, c.camp_name
ORDER BY c.camp_id;
