-- ============================================================================
-- Routine ID: F02
-- Routine Signature: dispatch_shipment(p_donor_id INT, p_camp_id INT, p_items JSONB) RETURNS INT
-- ============================================================================
-- Behavior Specification:
-- Creates a new shipment and its corresponding shipment_line records atomically.
-- Accepts p_items as JSONB array of objects (e.g. '[{"item_id": 1, "quantity": 50}]').
-- Inserts into shipment with status 'dispatched', then parses JSON array to insert lines.
-- Returns the generated shipment_id.
-- ============================================================================
-- Hint 1: Use INSERT INTO shipment (...) VALUES (...) RETURNING shipment_id INTO v_shipment_id.
-- Hint 2: Iterate or unpack JSONB using jsonb_to_recordset() to insert into shipment_line.

-- Stub: Replace with your CREATE OR REPLACE FUNCTION / PROCEDURE
CREATE OR REPLACE FUNCTION dispatch_shipment()
RETURNS TEXT AS $$
BEGIN
    RETURN 'TODO: Routine F02 not implemented yet';
END;
$$ LANGUAGE plpgsql;
