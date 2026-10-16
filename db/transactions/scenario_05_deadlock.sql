-- ============================================================================
-- Scenario 5: Deadlock between Two Stock Transfers
-- Isolation Level: READ COMMITTED
-- Description: Session 1 locks row A then requests row B; Session 2 locks row B then requests row A.
-- ============================================================================
-- Guided Scenario Steps:
-- Step 1: Session 1: BEGIN; UPDATE camp_stock SET quantity_on_hand = quantity_on_hand - 5 WHERE camp_id = 1 AND item_id = 1;
-- Step 2: Session 2: BEGIN; UPDATE camp_stock SET quantity_on_hand = quantity_on_hand - 5 WHERE camp_id = 1 AND item_id = 2;
-- Step 3: Session 1: UPDATE camp_stock SET quantity_on_hand = quantity_on_hand + 5 WHERE camp_id = 1 AND item_id = 2; (Waits for Session 2)
-- Step 4: Session 2: UPDATE camp_stock SET quantity_on_hand = quantity_on_hand + 5 WHERE camp_id = 1 AND item_id = 1; (Deadlock!)
-- Step 5: Outcome to observe: PostgreSQL deadlock detector triggers after deadlock_timeout (1s), aborting one session with ERROR 40P01.
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
