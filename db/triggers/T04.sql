-- ============================================================================
-- Trigger ID: T04
-- Trigger Name: trg_audit_request_urgency_changes
-- Target Table: supply_request
-- Event: AFTER UPDATE OF urgency ON supply_request
-- ============================================================================
-- Behavior Specification:
-- Log every change in request urgency into request_audit.
-- Records: request_id, OLD.urgency, NEW.urgency, and changed_at timestamp.
-- ============================================================================
-- Hint 1: Check condition: OLD.urgency IS DISTINCT FROM NEW.urgency.
-- Hint 2: Insert a row into request_audit(request_id, old_urgency, new_urgency, changed_at).

-- Stub: Replace with your CREATE OR REPLACE FUNCTION and CREATE TRIGGER statements
DO $$
BEGIN
    RAISE NOTICE 'Trigger T04 (trg_audit_request_urgency_changes) is a stub and has not been implemented yet.';
END
$$;
