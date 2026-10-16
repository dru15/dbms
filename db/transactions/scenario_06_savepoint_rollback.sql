-- ============================================================================
-- Scenario 6: Partial Rollback using SAVEPOINT
-- Isolation Level: READ COMMITTED
-- Description: Demonstrate graceful recovery inside a long multi-step transaction without aborting previous valid statements.
-- ============================================================================
-- Guided Scenario Steps:
-- Step 1: Session 1: BEGIN;
-- Step 2: Session 1: INSERT INTO supply_request (request_date, urgency, camp_id) VALUES ('2026-09-01', 'medium', 1);
-- Step 3: Session 1: SAVEPOINT sp_before_bad_insert;
-- Step 4: Session 1: INSERT INTO family_member VALUES (1, 1, 'Duplicate Key Error', 30, NULL); -- Intentionally fails PK
-- Step 5: Session 1: ROLLBACK TO SAVEPOINT sp_before_bad_insert;
-- Step 6: Session 1: COMMIT; -- The request insert persists while error is isolated.
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
