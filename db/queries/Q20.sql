-- ============================================================================
-- Query ID: Q20
-- Problem Statement: Materialized View: stock by category per district with refresh statement
-- Concepts Tested: CREATE MATERIALIZED VIEW, REFRESH MATERIALIZED VIEW CONCURRENTLY
-- Expected Output Columns: district, category, total_quantity_on_hand
-- ============================================================================
-- Hint 1: Create a materialized view named mv_district_category_stock aggregating camp_stock by district and category.
-- Hint 2: Include the REFRESH MATERIALIZED VIEW statement to demonstrate how it is updated.

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_district_category_stock AS
SELECT c.district, i.category, SUM(cs.quantity_on_hand) AS total_quantity_on_hand
FROM camp_stock cs
JOIN relief_camp c USING (camp_id)
JOIN supply_item i USING (item_id)
GROUP BY c.district, i.category;

-- A unique index permits concurrent refresh after the initial population.
CREATE UNIQUE INDEX IF NOT EXISTS ix_district_category_stock
    ON mv_district_category_stock (district, category);
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_district_category_stock;

SELECT * FROM mv_district_category_stock ORDER BY district, category;
