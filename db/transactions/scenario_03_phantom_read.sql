-- ============================================================================
-- Scenario 3: Phantom Read Prevention under REPEATABLE READ
-- Isolation Level: REPEATABLE READ
-- Description: Session 1 runs a range query, Session 2 inserts a new row matching the range and commits, Session 1 re-runs the range query.
-- ============================================================================
-- Guided Scenario Steps:
-- Step 1: Session 1: BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ; SELECT COUNT(*) FROM family_member WHERE family_id = 1;
-- Step 2: Session 2: INSERT INTO family_member VALUES (1, 99, 'Phantom Member', 25, NULL); COMMIT;
-- Step 3: Session 1: Re-run SELECT COUNT(*) FROM family_member WHERE family_id = 1;
-- Step 4: Outcome in PostgreSQL: Phantom read is PREVENTED by MVCC snapshot (unlike standard SQL 1992 anomaly rules).
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
