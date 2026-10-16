-- ============================================================================
-- Trigger ID: T02
-- Trigger Name: trg_prevent_negative_camp_stock
-- Target Table: camp_stock
-- Event: BEFORE UPDATE OR INSERT ON camp_stock
-- ============================================================================
-- Behavior Specification:
-- Reject any transaction that would cause quantity_on_hand in camp_stock to fall below zero.
-- Raise an EXCEPTION with an informative student-friendly error message if NEW.quantity_on_hand < 0.
-- ============================================================================
-- Hint 1: Although camp_stock has a CHECK constraint, this trigger demonstrates active procedural enforcement.
-- Hint 2: Raise an exception using: RAISE EXCEPTION 'Camp stock cannot be negative: camp %, item %', NEW.camp_id, NEW.item_id.

-- Stub: Replace with your CREATE OR REPLACE FUNCTION and CREATE TRIGGER statements
DO $$
BEGIN
    RAISE NOTICE 'Trigger T02 (trg_prevent_negative_camp_stock) is a stub and has not been implemented yet.';
END
$$;
