-- ============================================================================
-- Routine ID: F01
-- Routine Signature: issue_stock(p_camp_id INT, p_item_id INT, p_qty INT) RETURNS INT
-- ============================================================================
-- Behavior Specification:
-- Deducts p_qty from camp_stock for the given camp and item under concurrent execution.
-- Must acquire row-level lock (SELECT ... FOR UPDATE) to prevent lost updates.
-- If stock is insufficient, raise EXCEPTION.
-- Returns the new remaining quantity_on_hand.
-- ============================================================================
-- Hint 1: Use SELECT quantity_on_hand INTO v_current FROM camp_stock WHERE camp_id = p_camp_id AND item_id = p_item_id FOR UPDATE.
-- Hint 2: Verify v_current >= p_qty, perform UPDATE, and RETURN new quantity.

-- Stub: Replace with your CREATE OR REPLACE FUNCTION / PROCEDURE
CREATE OR REPLACE FUNCTION issue_stock()
RETURNS TEXT AS $$
BEGIN
    RETURN 'TODO: Routine F01 not implemented yet';
END;
$$ LANGUAGE plpgsql;
