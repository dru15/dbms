#!/usr/bin/env python3
"""
generate_trigger_routine_stubs.py: Generates trigger stubs T01-T05 and routine stubs F01-F04.
Pure stubs with behavior specifications and high-level guidance. No SQL solutions.
"""

import os

triggers = [
    {
        "id": "T01",
        "name": "trg_shipment_delivery_stock_upsert",
        "table": "shipment",
        "event": "AFTER UPDATE OF status ON shipment",
        "spec": (
            "When a shipment's status transitions to 'delivered', automatically add each of its\n"
            "-- shipment lines to camp_stock for that camp.\n"
            "-- If an entry for (camp_id, item_id) already exists in camp_stock, increment quantity_on_hand.\n"
            "-- If it does not exist, insert a new record with the delivered quantity."
        ),
        "hints": [
            "Write a trigger function returning TRIGGER.",
            "Check condition: NEW.status = 'delivered' AND OLD.status != 'delivered'.",
            "Loop over shipment_line or use INSERT ... ON CONFLICT (camp_id, item_id) DO UPDATE SET quantity_on_hand = camp_stock.quantity_on_hand + EXCLUDED.quantity_on_hand."
        ]
    },
    {
        "id": "T02",
        "name": "trg_prevent_negative_camp_stock",
        "table": "camp_stock",
        "event": "BEFORE UPDATE OR INSERT ON camp_stock",
        "spec": (
            "Reject any transaction that would cause quantity_on_hand in camp_stock to fall below zero.\n"
            "-- Raise an EXCEPTION with an informative student-friendly error message if NEW.quantity_on_hand < 0."
        ),
        "hints": [
            "Although camp_stock has a CHECK constraint, this trigger demonstrates active procedural enforcement.",
            "Raise an exception using: RAISE EXCEPTION 'Camp stock cannot be negative: camp %, item %', NEW.camp_id, NEW.item_id."
        ]
    },
    {
        "id": "T03",
        "name": "trg_enforce_camp_capacity_on_family_member",
        "table": "family_member",
        "event": "BEFORE INSERT ON family_member",
        "spec": (
            "Reject any family_member insert that would push the camp's total registered members\n"
            "-- strictly over its declared camp capacity.\n"
            "-- Identify the camp_id from registered_family for NEW.family_id.\n"
            "-- If current members count + 1 > capacity, raise an EXCEPTION."
        ),
        "hints": [
            "Query registered_family to find the camp_id of the family.",
            "Query relief_camp for capacity and compare against (current members in that camp + 1)."
        ]
    },
    {
        "id": "T04",
        "name": "trg_audit_request_urgency_changes",
        "table": "supply_request",
        "event": "AFTER UPDATE OF urgency ON supply_request",
        "spec": (
            "Log every change in request urgency into request_audit.\n"
            "-- Records: request_id, OLD.urgency, NEW.urgency, and changed_at timestamp."
        ),
        "hints": [
            "Check condition: OLD.urgency IS DISTINCT FROM NEW.urgency.",
            "Insert a row into request_audit(request_id, old_urgency, new_urgency, changed_at)."
        ]
    },
    {
        "id": "T05",
        "name": "trg_enforce_medical_volunteer_certification",
        "table": "assignment",
        "event": "BEFORE INSERT OR UPDATE ON assignment",
        "spec": (
            "Reject any volunteer assignment where role = 'medical' or contains 'medical' / 'doctor' / 'nurse'\n"
            "-- unless the assigned volunteer holds at least one valid, non-expired certification\n"
            "-- in volunteer_certification (expiry_date >= CURRENT_DATE)."
        ),
        "hints": [
            "Check if NEW.role ILIKE '%medical%' or '%doctor%' or '%nurse%'.",
            "Query volunteer_certification where volunteer_id = NEW.volunteer_id AND expiry_date >= CURRENT_DATE.",
            "Raise an EXCEPTION if no such certification is found."
        ]
    }
]

for t in triggers:
    hints_str = "\n".join([f"-- Hint {i+1}: {h}" for i, h in enumerate(t["hints"])])
    content = f"""-- ============================================================================
-- Trigger ID: {t["id"]}
-- Trigger Name: {t["name"]}
-- Target Table: {t["table"]}
-- Event: {t["event"]}
-- ============================================================================
-- Behavior Specification:
-- {t["spec"]}
-- ============================================================================
{hints_str}

-- Stub: Replace with your CREATE OR REPLACE FUNCTION and CREATE TRIGGER statements
DO $$
BEGIN
    RAISE NOTICE 'Trigger {t["id"]} ({t["name"]}) is a stub and has not been implemented yet.';
END
$$;
"""
    with open(os.path.join("db", "triggers", f"{t['id']}.sql"), "w", encoding="utf-8") as f:
        f.write(content)

routines = [
    {
        "id": "F01",
        "name": "issue_stock",
        "signature": "issue_stock(p_camp_id INT, p_item_id INT, p_qty INT) RETURNS INT",
        "spec": (
            "Deducts p_qty from camp_stock for the given camp and item under concurrent execution.\n"
            "-- Must acquire row-level lock (SELECT ... FOR UPDATE) to prevent lost updates.\n"
            "-- If stock is insufficient, raise EXCEPTION.\n"
            "-- Returns the new remaining quantity_on_hand."
        ),
        "hints": [
            "Use SELECT quantity_on_hand INTO v_current FROM camp_stock WHERE camp_id = p_camp_id AND item_id = p_item_id FOR UPDATE.",
            "Verify v_current >= p_qty, perform UPDATE, and RETURN new quantity."
        ]
    },
    {
        "id": "F02",
        "name": "dispatch_shipment",
        "signature": "dispatch_shipment(p_donor_id INT, p_camp_id INT, p_items JSONB) RETURNS INT",
        "spec": (
            "Creates a new shipment and its corresponding shipment_line records atomically.\n"
            "-- Accepts p_items as JSONB array of objects (e.g. '[{\"item_id\": 1, \"quantity\": 50}]').\n"
            "-- Inserts into shipment with status 'dispatched', then parses JSON array to insert lines.\n"
            "-- Returns the generated shipment_id."
        ),
        "hints": [
            "Use INSERT INTO shipment (...) VALUES (...) RETURNING shipment_id INTO v_shipment_id.",
            "Iterate or unpack JSONB using jsonb_to_recordset() to insert into shipment_line."
        ]
    },
    {
        "id": "F03",
        "name": "camp_summary",
        "signature": "camp_summary(p_camp_id INT) RETURNS TABLE(camp_name TEXT, district TEXT, capacity INT, total_families INT, total_members INT, total_volunteers INT, total_stock_items INT)",
        "spec": (
            "Returns a single-row composite summary table for the specified camp.\n"
            "-- Computes live counts of registered families, registered members, assigned volunteers, and distinct stocked items."
        ),
        "hints": [
            "Define function using RETURNS TABLE(...).",
            "Use scalar subqueries or CTEs to gather aggregate metrics for p_camp_id without Cartesian multiplication."
        ]
    },
    {
        "id": "F04",
        "name": "escalate_stale_requests",
        "signature": "escalate_stale_requests(p_days INT) RETURNS INT",
        "spec": (
            "Finds unfulfilled supply requests older than p_days and escalates their urgency by one level:\n"
            "-- 'low' -> 'medium', 'medium' -> 'high', 'high' -> 'critical'.\n"
            "-- Must use an explicit CURSOR loop in PL/pgSQL.\n"
            "-- Returns the total number of requests escalated."
        ),
        "hints": [
            "Declare a cursor FOR SELECT request_id, urgency FROM supply_request WHERE ... FOR UPDATE.",
            "Iterate using FETCH / LOOP, calculate next urgency, and UPDATE supply_request WHERE CURRENT OF."
        ]
    }
]

for r in routines:
    hints_str = "\n".join([f"-- Hint {i+1}: {h}" for i, h in enumerate(r["hints"])])
    content = f"""-- ============================================================================
-- Routine ID: {r["id"]}
-- Routine Signature: {r["signature"]}
-- ============================================================================
-- Behavior Specification:
-- {r["spec"]}
-- ============================================================================
{hints_str}

-- Stub: Replace with your CREATE OR REPLACE FUNCTION / PROCEDURE
CREATE OR REPLACE FUNCTION {r["name"]}()
RETURNS TEXT AS $$
BEGIN
    RETURN 'TODO: Routine {r["id"]} not implemented yet';
END;
$$ LANGUAGE plpgsql;
"""
    with open(os.path.join("db", "routines", f"{r['id']}.sql"), "w", encoding="utf-8") as f:
        f.write(content)

print("Generated triggers and routines stubs.")
