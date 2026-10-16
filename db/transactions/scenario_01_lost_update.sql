-- ============================================================================
-- Scenario 1: Lost Update on camp_stock
-- Isolation Level: READ COMMITTED
-- Description: Two concurrent sessions attempt to decrement stock for the same item at the same camp without locking.
-- ============================================================================
-- Guided Scenario Steps:
-- Step 1: Session 1: Read stock for Camp 1, Item 1 (e.g. quantity = 150).
-- Step 2: Session 2: Read stock for Camp 1, Item 1 (also reads 150).
-- Step 3: Session 1: Update stock to (150 - 20 = 130) and commit.
-- Step 4: Session 2: Update stock to (150 - 30 = 120) and commit.
-- Step 5: Outcome to observe: Session 1's decrement is completely lost (final stock is 120 instead of 100).
-- Step 6: Remedy to test: Use SELECT ... FOR UPDATE to eliminate lost update.
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
