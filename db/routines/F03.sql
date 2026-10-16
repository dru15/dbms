-- ============================================================================
-- Routine ID: F03
-- Routine Signature: camp_summary(p_camp_id INT) RETURNS TABLE(camp_name TEXT, district TEXT, capacity INT, total_families INT, total_members INT, total_volunteers INT, total_stock_items INT)
-- ============================================================================
-- Behavior Specification:
-- Returns a single-row composite summary table for the specified camp.
-- Computes live counts of registered families, registered members, assigned volunteers, and distinct stocked items.
-- ============================================================================
-- Hint 1: Define function using RETURNS TABLE(...).
-- Hint 2: Use scalar subqueries or CTEs to gather aggregate metrics for p_camp_id without Cartesian multiplication.

-- Stub: Replace with your CREATE OR REPLACE FUNCTION / PROCEDURE
CREATE OR REPLACE FUNCTION camp_summary()
RETURNS TEXT AS $$
BEGIN
    RETURN 'TODO: Routine F03 not implemented yet';
END;
$$ LANGUAGE plpgsql;
