-- ============================================================================
-- 00_roles.sql: Database Roles and Access Control Scaffolding (DCL)
-- Course Project: Disaster Relief Logistics DB (PostgreSQL 16)
-- ============================================================================
-- NOTE: As per project guidelines, roles are created here.
-- Detailed GRANT/REVOKE statements will be authored by the student.

-- Role 1: camp_manager
-- Specification:
-- The camp manager is responsible for day-to-day camp operational logistics.
-- This role should have full read/write access to shelter_unit, registered_family,
-- family_member, camp_stock, and supply_request for their designated camp.
-- They require read-only access to relief_camp metadata, volunteer assignments,
-- and incoming shipments. They must NOT view donor contact numbers, global financial
-- records, or modify system audit tables.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'camp_manager') THEN
        CREATE ROLE camp_manager WITH NOLOGIN;
    END IF;
END
$$;

-- Role 2: donor_relations
-- Specification:
-- The donor relations liaison coordinates contributions and tracks logistics.
-- This role should have SELECT, INSERT, and UPDATE permissions on donor, shipment,
-- and shipment_line tables. They should have read-only access to supply_item and
-- supply_request to match incoming donations against active camp needs.
-- They must NOT access internal camp family registrations, shelter allocations,
-- or volunteer personal information.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'donor_relations') THEN
        CREATE ROLE donor_relations WITH NOLOGIN;
    END IF;
END
$$;

-- Role 3: auditor
-- Specification:
-- The auditor performs compliance, integrity verification, and inventory tracking.
-- This role requires comprehensive SELECT privileges across all tables (relief_camp,
-- supply_item, donor, shipment, supply_request, volunteer, registered_family, camp_stock)
-- and exclusive read access to request_audit. This role must have strictly read-only
-- access across the entire database, with no INSERT, UPDATE, DELETE, or DDL privileges.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'auditor') THEN
        CREATE ROLE auditor WITH NOLOGIN;
    END IF;
END
$$;
