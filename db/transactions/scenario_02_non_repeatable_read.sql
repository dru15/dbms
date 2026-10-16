-- ============================================================================
-- Scenario 2: Non-Repeatable Read
-- Isolation Level: READ COMMITTED vs REPEATABLE READ
-- Description: Session 1 reads the same row twice within a single transaction, while Session 2 modifies it in between.
-- ============================================================================
-- Guided Scenario Steps:
-- Step 1: Session 1: BEGIN ISOLATION LEVEL READ COMMITTED; SELECT capacity FROM relief_camp WHERE camp_id = 1;
-- Step 2: Session 2: BEGIN; UPDATE relief_camp SET capacity = capacity + 20 WHERE camp_id = 1; COMMIT;
-- Step 3: Session 1: Re-execute SELECT capacity FROM relief_camp WHERE camp_id = 1; (Observe value changed mid-transaction).
-- Step 4: Repeat under REPEATABLE READ: Observe snapshot isolation preserving the original value.
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
