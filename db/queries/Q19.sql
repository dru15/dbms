-- ============================================================================
-- Query ID: Q19
-- Problem Statement: View: camp_status_dashboard
-- Concepts Tested: Database Views (CREATE OR REPLACE VIEW), Multi-table metrics summary
-- Expected Output Columns: camp_id, camp_name, capacity, registered_members, open_requests, assigned_volunteers
-- ============================================================================
-- Hint 1: Create a view named camp_status_dashboard summarizing camp demographics and operations.
-- Hint 2: Aggregate registered family members, pending requests, and assigned volunteers using CTEs or scalar subqueries.

CREATE OR REPLACE VIEW camp_status_dashboard AS
WITH members AS (
    SELECT f.camp_id, COUNT(m.member_no) AS registered_members
    FROM registered_family f
    JOIN family_member m USING (family_id)
    GROUP BY f.camp_id
), requests AS (
    SELECT camp_id, COUNT(*) AS open_requests
    FROM supply_request GROUP BY camp_id
), volunteers AS (
    SELECT camp_id, COUNT(*) AS assigned_volunteers
    FROM assignment GROUP BY camp_id
)
SELECT c.camp_id, c.camp_name, c.capacity,
       COALESCE(m.registered_members, 0) AS registered_members,
       COALESCE(r.open_requests, 0) AS open_requests,
       COALESCE(v.assigned_volunteers, 0) AS assigned_volunteers
FROM relief_camp c
LEFT JOIN members m USING (camp_id)
LEFT JOIN requests r USING (camp_id)
LEFT JOIN volunteers v USING (camp_id);

SELECT * FROM camp_status_dashboard ORDER BY camp_id;
