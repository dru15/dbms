-- ============================================================================
-- 03_seed_bulk.sql: Bulk Data Generator (~1,000,000 shipment_line rows)
-- Designed for Indexing and Query Optimization Benchmarking
-- Deterministic via fixed seed: setseed(0.42)
-- ============================================================================

SELECT setseed(0.42);

DO $$
DECLARE
    v_start_time timestamp := clock_timestamp();
    v_start_shipment_id int;
    v_end_shipment_id int;
    v_num_shipments int := 250000; -- 250,000 shipments * 4 lines = 1,000,000 lines
    v_lines_per_shipment int := 4;
BEGIN
    RAISE NOTICE 'Starting bulk data generation for indexing study...';

    -- 1. Insert 250,000 parent shipments
    RAISE NOTICE 'Generating 250,000 parent shipments...';
    WITH new_shipments AS (
        INSERT INTO shipment (shipment_date, vehicle_no, status, donor_id, camp_id)
        SELECT
            '2026-01-01'::date + (floor(random() * 270))::int AS shipment_date,
            'BULK-' || lpad((g % 9000 + 1000)::text, 4, '0') AS vehicle_no,
            (ARRAY['delivered', 'delivered', 'delivered', 'in_transit', 'dispatched', 'cancelled'])[floor(random() * 6) + 1] AS status,
            (floor(random() * 25) + 1)::int AS donor_id,
            (floor(random() * 12) + 1)::int AS camp_id
        FROM generate_series(1, v_num_shipments) g
        RETURNING shipment_id
    )
    SELECT min(shipment_id), max(shipment_id)
    INTO v_start_shipment_id, v_end_shipment_id
    FROM new_shipments;

    RAISE NOTICE 'Created shipments from ID % to %.', v_start_shipment_id, v_end_shipment_id;

    -- 2. Insert 1,000,000 shipment lines (4 lines per shipment)
    RAISE NOTICE 'Generating 1,000,000 shipment lines...';
    INSERT INTO shipment_line (shipment_id, line_no, item_id, quantity_sent)
    SELECT
        s_id,
        l_no,
        ((s_id * 3 + l_no * 7) % 38 + 1)::int AS item_id,
        (floor(random() * 450) + 10)::int AS quantity_sent
    FROM generate_series(v_start_shipment_id, v_end_shipment_id) s_id
    CROSS JOIN generate_series(1, v_lines_per_shipment) l_no;

    -- Update camp_stock with delivered bulk shipments
    RAISE NOTICE 'Updating camp_stock inventory balances...';
    INSERT INTO camp_stock (camp_id, item_id, quantity_on_hand)
    SELECT
        s.camp_id,
        sl.item_id,
        SUM(sl.quantity_sent)
    FROM shipment s
    JOIN shipment_line sl ON s.shipment_id = sl.shipment_id
    WHERE s.shipment_id >= v_start_shipment_id AND s.status = 'delivered'
    GROUP BY s.camp_id, sl.item_id
    ON CONFLICT (camp_id, item_id)
    DO UPDATE SET quantity_on_hand = camp_stock.quantity_on_hand + EXCLUDED.quantity_on_hand;

    RAISE NOTICE 'Bulk seed successfully generated in % seconds.', 
        EXTRACT(EPOCH FROM (clock_timestamp() - v_start_time));
END
$$;
