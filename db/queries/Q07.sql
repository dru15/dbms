-- ============================================================================
-- Query ID: Q07
-- Problem Statement: Volunteers with expired certifications currently assigned to a camp
-- Concepts Tested: INNER JOIN across volunteer, volunteer_certification, assignment, Date comparison
-- Expected Output Columns: volunteer_id, volunteer_name, cert_name, expiry_date, camp_id, camp_name
-- ============================================================================
-- Hint 1: Join active volunteer assignments with their certifications.
-- Hint 2: Compare certification expiry_date against the current active operational period.

-- Fixed reference date keeps the review reproducible with the seed oracle.
SELECT v.volunteer_id, v.volunteer_name, vc.cert_name, vc.expiry_date,
       c.camp_id, c.camp_name
FROM volunteer v
JOIN volunteer_certification vc USING (volunteer_id)
JOIN assignment a USING (volunteer_id)
JOIN relief_camp c USING (camp_id)
WHERE vc.expiry_date < DATE '2026-09-30'
ORDER BY v.volunteer_id, vc.cert_name, c.camp_id;
