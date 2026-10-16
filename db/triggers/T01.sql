-- ============================================================================
-- Trigger ID: T01
-- Trigger Name: trg_shipment_delivery_stock_upsert
-- Target Table: shipment
-- Event: AFTER UPDATE OF status ON shipment
-- ============================================================================
-- Behavior Specification:
-- When a shipment's status transitions to 'delivered', automatically add each of its
-- shipment lines to camp_stock for that camp.
-- If an entry for (camp_id, item_id) already exists in camp_stock, increment quantity_on_hand.
-- If it does not exist, insert a new record with the delivered quantity.
-- ============================================================================
-- Hint 1: Write a trigger function returning TRIGGER.
-- Hint 2: Check condition: NEW.status = 'delivered' AND OLD.status != 'delivered'.
-- Hint 3: Loop over shipment_line or use INSERT ... ON CONFLICT (camp_id, item_id) DO UPDATE SET quantity_on_hand = camp_stock.quantity_on_hand + EXCLUDED.quantity_on_hand.

-- Stub: Replace with your CREATE OR REPLACE FUNCTION and CREATE TRIGGER statements
DO $$
BEGIN
    RAISE NOTICE 'Trigger T01 (trg_shipment_delivery_stock_upsert) is a stub and has not been implemented yet.';
END
$$;
