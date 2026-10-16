-- ============================================================================
-- Query ID: Q15
-- Problem Statement: Pairs of volunteers with the same skill assigned to the same camp
-- Concepts Tested: Self-Join on assignment and volunteer, deduplication using inequality (<)
-- Expected Output Columns: camp_id, camp_name, skill, volunteer_1_id, volunteer_1_name, volunteer_2_id, volunteer_2_name
-- ============================================================================
-- Hint 1: Self-join the assignment table on camp_id where v1.volunteer_id < v2.volunteer_id.
-- Hint 2: Join volunteer tables twice to compare and ensure matching skills.

SELECT c.camp_id, c.camp_name, v1.skill,
       v1.volunteer_id AS volunteer_1_id, v1.volunteer_name AS volunteer_1_name,
       v2.volunteer_id AS volunteer_2_id, v2.volunteer_name AS volunteer_2_name
FROM assignment a1
JOIN assignment a2 ON a2.camp_id = a1.camp_id
                  AND a1.volunteer_id < a2.volunteer_id
JOIN volunteer v1 ON v1.volunteer_id = a1.volunteer_id
JOIN volunteer v2 ON v2.volunteer_id = a2.volunteer_id AND v2.skill = v1.skill
JOIN relief_camp c ON c.camp_id = a1.camp_id
ORDER BY c.camp_id, v1.skill, v1.volunteer_id, v2.volunteer_id;
