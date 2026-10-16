-- ============================================================================
-- Query ID: Q08
-- Problem Statement: Camps with no medical-skilled volunteer currently assigned
-- Concepts Tested: Anti-join using NOT EXISTS or NOT IN with subquery
-- Expected Output Columns: camp_id, camp_name, district
-- ============================================================================
-- Hint 1: Find camps that do not exist in the set of camps currently assigned to volunteers with skill = 'medical'.
-- Hint 2: Use NOT EXISTS or EXCEPT to isolate the understaffed camps.

SELECT c.camp_id, c.camp_name, c.district
FROM relief_camp c
WHERE NOT EXISTS (
    SELECT 1 FROM assignment a
    JOIN volunteer v USING (volunteer_id)
    WHERE a.camp_id = c.camp_id AND v.skill = 'medical'
)
ORDER BY c.camp_id;
