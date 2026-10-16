-- ============================================================================
-- Scenario 7: Work Queue Concurrency using SELECT FOR UPDATE SKIP LOCKED
-- Isolation Level: READ COMMITTED
-- Description: Multiple worker sessions process pending supply requests without blocking or contention.
-- ============================================================================
-- Guided Scenario Steps:
-- Step 1: Session 1: BEGIN; SELECT request_id FROM supply_request WHERE urgency = 'critical' ORDER BY request_id LIMIT 1 FOR UPDATE SKIP LOCKED;
-- Step 2: Session 2: BEGIN; SELECT request_id FROM supply_request WHERE urgency = 'critical' ORDER BY request_id LIMIT 1 FOR UPDATE SKIP LOCKED;
-- Step 3: Outcome: Session 2 immediately gets the next available critical request without waiting for Session 1 to commit!
-- ============================================================================

-- SESSION 1 SCRIPT STUB:
-- Open psql session 1 and execute step-by-step:
/*
-- TODO: Paste Session 1 commands here
*/

-- SESSION 2 SCRIPT STUB:
-- Open psql session 2 and execute step-by-step:
/*
-- TODO: Paste Session 2 commands here
*/
