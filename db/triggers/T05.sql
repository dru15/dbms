-- ============================================================================
-- Trigger ID: T05
-- Trigger Name: trg_enforce_medical_volunteer_certification
-- Target Table: assignment
-- Event: BEFORE INSERT OR UPDATE ON assignment
-- ============================================================================
-- Behavior Specification:
-- Reject any volunteer assignment where role = 'medical' or contains 'medical' / 'doctor' / 'nurse'
-- unless the assigned volunteer holds at least one valid, non-expired certification
-- in volunteer_certification (expiry_date >= CURRENT_DATE).
-- ============================================================================
-- Hint 1: Check if NEW.role ILIKE '%medical%' or '%doctor%' or '%nurse%'.
-- Hint 2: Query volunteer_certification where volunteer_id = NEW.volunteer_id AND expiry_date >= CURRENT_DATE.
-- Hint 3: Raise an EXCEPTION if no such certification is found.

-- Stub: Replace with your CREATE OR REPLACE FUNCTION and CREATE TRIGGER statements
DO $$
BEGIN
    RAISE NOTICE 'Trigger T05 (trg_enforce_medical_volunteer_certification) is a stub and has not been implemented yet.';
END
$$;
