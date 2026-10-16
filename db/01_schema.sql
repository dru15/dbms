-- ============================================================================
-- 01_schema.sql: Authoritative Relational DDL Schema
-- Course Project: Disaster Relief Logistics DB (PostgreSQL 16)
-- ============================================================================

-- Clean up any existing tables in dependency order
DROP TABLE IF EXISTS request_audit CASCADE;
DROP TABLE IF EXISTS camp_stock CASCADE;
DROP TABLE IF EXISTS assignment CASCADE;
DROP TABLE IF EXISTS family_member CASCADE;
DROP TABLE IF EXISTS volunteer_certification CASCADE;
DROP TABLE IF EXISTS request_line CASCADE;
DROP TABLE IF EXISTS shipment_line CASCADE;
DROP TABLE IF EXISTS shelter_unit CASCADE;
DROP TABLE IF EXISTS registered_family CASCADE;
DROP TABLE IF EXISTS volunteer CASCADE;
DROP TABLE IF EXISTS supply_request CASCADE;
DROP TABLE IF EXISTS shipment CASCADE;
DROP TABLE IF EXISTS donor CASCADE;
DROP TABLE IF EXISTS supply_item CASCADE;
DROP TABLE IF EXISTS relief_camp CASCADE;

-- ----------------------------------------------------------------------------
-- STRONG ENTITIES
-- ----------------------------------------------------------------------------

-- 1. relief_camp
CREATE TABLE relief_camp (
    camp_id INTEGER GENERATED ALWAYS AS IDENTITY,
    camp_name TEXT NOT NULL,
    district TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    CONSTRAINT pk_relief_camp PRIMARY KEY (camp_id),
    CONSTRAINT ck_relief_camp_capacity CHECK (capacity > 0),
    CONSTRAINT ck_relief_camp_status CHECK (status IN ('active', 'full', 'closed'))
);

-- 2. supply_item
CREATE TABLE supply_item (
    item_id INTEGER GENERATED ALWAYS AS IDENTITY,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit TEXT NOT NULL,
    CONSTRAINT pk_supply_item PRIMARY KEY (item_id),
    CONSTRAINT uq_supply_item_item_name UNIQUE (item_name),
    CONSTRAINT ck_supply_item_category CHECK (category IN ('food', 'water', 'medical', 'shelter', 'clothing', 'hygiene'))
);

-- 3. donor
CREATE TABLE donor (
    donor_id INTEGER GENERATED ALWAYS AS IDENTITY,
    donor_name TEXT NOT NULL,
    donor_type TEXT NOT NULL,
    phone TEXT,
    CONSTRAINT pk_donor PRIMARY KEY (donor_id),
    CONSTRAINT ck_donor_donor_type CHECK (donor_type IN ('individual', 'ngo', 'corporate', 'government'))
);

-- 4. shipment
CREATE TABLE shipment (
    shipment_id INTEGER GENERATED ALWAYS AS IDENTITY,
    shipment_date DATE NOT NULL,
    vehicle_no TEXT,
    status TEXT NOT NULL DEFAULT 'dispatched',
    donor_id INTEGER NOT NULL,
    camp_id INTEGER NOT NULL,
    CONSTRAINT pk_shipment PRIMARY KEY (shipment_id),
    CONSTRAINT ck_shipment_status CHECK (status IN ('dispatched', 'in_transit', 'delivered', 'cancelled')),
    CONSTRAINT fk_shipment_donor FOREIGN KEY (donor_id) REFERENCES donor(donor_id) ON DELETE RESTRICT,
    CONSTRAINT fk_shipment_camp FOREIGN KEY (camp_id) REFERENCES relief_camp(camp_id) ON DELETE RESTRICT
);

-- 5. supply_request
CREATE TABLE supply_request (
    request_id INTEGER GENERATED ALWAYS AS IDENTITY,
    request_date DATE NOT NULL,
    urgency TEXT NOT NULL,
    camp_id INTEGER NOT NULL,
    CONSTRAINT pk_supply_request PRIMARY KEY (request_id),
    CONSTRAINT ck_supply_request_urgency CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT fk_supply_request_camp FOREIGN KEY (camp_id) REFERENCES relief_camp(camp_id) ON DELETE RESTRICT
);

-- 6. volunteer
CREATE TABLE volunteer (
    volunteer_id INTEGER GENERATED ALWAYS AS IDENTITY,
    volunteer_name TEXT NOT NULL,
    phone TEXT,
    skill TEXT NOT NULL,
    CONSTRAINT pk_volunteer PRIMARY KEY (volunteer_id)
);

-- 7. registered_family
CREATE TABLE registered_family (
    family_id INTEGER GENERATED ALWAYS AS IDENTITY,
    head_name TEXT NOT NULL,
    origin_village TEXT,
    registered_on DATE NOT NULL,
    camp_id INTEGER NOT NULL,
    CONSTRAINT pk_registered_family PRIMARY KEY (family_id),
    CONSTRAINT fk_registered_family_camp FOREIGN KEY (camp_id) REFERENCES relief_camp(camp_id) ON DELETE RESTRICT
);

-- ----------------------------------------------------------------------------
-- WEAK ENTITIES (Identifying relationship: ON DELETE CASCADE from owner)
-- ----------------------------------------------------------------------------

-- 8. shelter_unit (Owner: relief_camp)
CREATE TABLE shelter_unit (
    camp_id INTEGER NOT NULL,
    unit_no INTEGER NOT NULL,
    unit_type TEXT NOT NULL,
    unit_capacity INTEGER NOT NULL,
    CONSTRAINT pk_shelter_unit PRIMARY KEY (camp_id, unit_no),
    CONSTRAINT fk_shelter_unit_camp FOREIGN KEY (camp_id) REFERENCES relief_camp(camp_id) ON DELETE CASCADE,
    CONSTRAINT ck_shelter_unit_unit_type CHECK (unit_type IN ('tent', 'hall', 'prefab')),
    CONSTRAINT ck_shelter_unit_unit_capacity CHECK (unit_capacity > 0)
);

-- 9. shipment_line (Owner: shipment)
CREATE TABLE shipment_line (
    shipment_id INTEGER NOT NULL,
    line_no INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity_sent INTEGER NOT NULL,
    CONSTRAINT pk_shipment_line PRIMARY KEY (shipment_id, line_no),
    CONSTRAINT fk_shipment_line_shipment FOREIGN KEY (shipment_id) REFERENCES shipment(shipment_id) ON DELETE CASCADE,
    CONSTRAINT fk_shipment_line_item FOREIGN KEY (item_id) REFERENCES supply_item(item_id) ON DELETE RESTRICT,
    CONSTRAINT ck_shipment_line_quantity_sent CHECK (quantity_sent > 0)
);

-- 10. request_line (Owner: supply_request)
CREATE TABLE request_line (
    request_id INTEGER NOT NULL,
    line_no INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    qty_requested INTEGER NOT NULL,
    CONSTRAINT pk_request_line PRIMARY KEY (request_id, line_no),
    CONSTRAINT fk_request_line_request FOREIGN KEY (request_id) REFERENCES supply_request(request_id) ON DELETE CASCADE,
    CONSTRAINT fk_request_line_item FOREIGN KEY (item_id) REFERENCES supply_item(item_id) ON DELETE RESTRICT,
    CONSTRAINT ck_request_line_qty_requested CHECK (qty_requested > 0)
);

-- 11. volunteer_certification (Owner: volunteer)
CREATE TABLE volunteer_certification (
    volunteer_id INTEGER NOT NULL,
    cert_no INTEGER NOT NULL,
    cert_name TEXT NOT NULL,
    issued_by TEXT,
    expiry_date DATE,
    CONSTRAINT pk_volunteer_certification PRIMARY KEY (volunteer_id, cert_no),
    CONSTRAINT fk_volunteer_certification_volunteer FOREIGN KEY (volunteer_id) REFERENCES volunteer(volunteer_id) ON DELETE CASCADE
);

-- 12. family_member (Owner: registered_family)
CREATE TABLE family_member (
    family_id INTEGER NOT NULL,
    member_no INTEGER NOT NULL,
    member_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    special_need TEXT,
    CONSTRAINT pk_family_member PRIMARY KEY (family_id, member_no),
    CONSTRAINT fk_family_member_family FOREIGN KEY (family_id) REFERENCES registered_family(family_id) ON DELETE CASCADE,
    CONSTRAINT ck_family_member_age CHECK (age >= 0 AND age <= 120)
);

-- ----------------------------------------------------------------------------
-- ASSOCIATIVE ENTITY (M:N)
-- ----------------------------------------------------------------------------

-- 13. assignment
CREATE TABLE assignment (
    volunteer_id INTEGER NOT NULL,
    camp_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    shift TEXT NOT NULL,
    CONSTRAINT pk_assignment PRIMARY KEY (volunteer_id, camp_id),
    CONSTRAINT fk_assignment_volunteer FOREIGN KEY (volunteer_id) REFERENCES volunteer(volunteer_id) ON DELETE RESTRICT,
    CONSTRAINT fk_assignment_camp FOREIGN KEY (camp_id) REFERENCES relief_camp(camp_id) ON DELETE RESTRICT,
    CONSTRAINT ck_assignment_shift CHECK (shift IN ('morning', 'evening', 'night'))
);

-- ----------------------------------------------------------------------------
-- SUPPORTING TABLES (Triggers, Transactions & Auditing)
-- ----------------------------------------------------------------------------

-- 14. camp_stock
CREATE TABLE camp_stock (
    camp_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity_on_hand INTEGER NOT NULL,
    CONSTRAINT pk_camp_stock PRIMARY KEY (camp_id, item_id),
    CONSTRAINT fk_camp_stock_camp FOREIGN KEY (camp_id) REFERENCES relief_camp(camp_id) ON DELETE RESTRICT,
    CONSTRAINT fk_camp_stock_item FOREIGN KEY (item_id) REFERENCES supply_item(item_id) ON DELETE RESTRICT,
    CONSTRAINT ck_camp_stock_quantity_on_hand CHECK (quantity_on_hand >= 0)
);

-- 15. request_audit
CREATE TABLE request_audit (
    audit_id INTEGER GENERATED ALWAYS AS IDENTITY,
    request_id INTEGER NOT NULL,
    old_urgency TEXT,
    new_urgency TEXT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_request_audit PRIMARY KEY (audit_id),
    CONSTRAINT fk_request_audit_request FOREIGN KEY (request_id) REFERENCES supply_request(request_id) ON DELETE CASCADE
);
