-- ============================================================================
-- Trigger ID: T03
-- Trigger Name: trg_enforce_camp_capacity_on_family_member
-- Target Table: family_member
-- Event: BEFORE INSERT ON family_member
-- ============================================================================
-- Behavior Specification:
-- Reject any family_member insert that would push the camp's total registered members
-- strictly over its declared camp capacity.
-- Identify the camp_id from registered_family for NEW.family_id.
-- If current members count + 1 > capacity, raise an EXCEPTION.
-- ============================================================================
-- Hint 1: Query registered_family to find the camp_id of the family.
-- Hint 2: Query relief_camp for capacity and compare against (current members in that camp + 1).

-- Stub: Replace with your CREATE OR REPLACE FUNCTION and CREATE TRIGGER statements
DO $$
BEGIN
    RAISE NOTICE 'Trigger T03 (trg_enforce_camp_capacity_on_family_member) is a stub and has not been implemented yet.';
END
$$;
