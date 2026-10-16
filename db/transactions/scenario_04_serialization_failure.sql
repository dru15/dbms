-- ============================================================================
-- Scenario 4: Serialization Failure under SERIALIZABLE with Client Retry
-- Isolation Level: SERIALIZABLE
-- Description: Two transactions produce a write skew / cycle that cannot be scheduled serially.
-- ============================================================================
-- Guided Scenario Steps:
-- Step 1: Session 1: BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE; SELECT SUM(quantity_on_hand) FROM camp_stock WHERE camp_id = 1;
-- Step 2: Session 2: BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE; SELECT SUM(quantity_on_hand) FROM camp_stock WHERE camp_id = 1;
-- Step 3: Session 1: UPDATE camp_stock SET quantity_on_hand = quantity_on_hand - 10 WHERE camp_id = 1 AND item_id = 1;
-- Step 4: Session 2: UPDATE camp_stock SET quantity_on_hand = quantity_on_hand - 10 WHERE camp_id = 1 AND item_id = 2;
-- Step 5: Session 1: COMMIT;
-- Step 6: Session 2: COMMIT; -> Observe ERROR 40001: could not serialize access due to read/write dependencies among transactions.
-- Step 7: Client action: Catch 40001 and execute automatic retry.
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
