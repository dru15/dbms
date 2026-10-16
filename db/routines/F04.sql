-- ============================================================================
-- Routine ID: F04
-- Routine Signature: escalate_stale_requests(p_days INT) RETURNS INT
-- ============================================================================
-- Behavior Specification:
-- Finds unfulfilled supply requests older than p_days and escalates their urgency by one level:
-- 'low' -> 'medium', 'medium' -> 'high', 'high' -> 'critical'.
-- Must use an explicit CURSOR loop in PL/pgSQL.
-- Returns the total number of requests escalated.
-- ============================================================================
-- Hint 1: Declare a cursor FOR SELECT request_id, urgency FROM supply_request WHERE ... FOR UPDATE.
-- Hint 2: Iterate using FETCH / LOOP, calculate next urgency, and UPDATE supply_request WHERE CURRENT OF.

-- Stub: Replace with your CREATE OR REPLACE FUNCTION / PROCEDURE
CREATE OR REPLACE FUNCTION escalate_stale_requests()
RETURNS TEXT AS $$
BEGIN
    RETURN 'TODO: Routine F04 not implemented yet';
END;
$$ LANGUAGE plpgsql;
