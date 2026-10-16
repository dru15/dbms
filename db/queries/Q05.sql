-- ============================================================================
-- Query ID: Q05
-- Problem Statement: Top 3 donors per item category by total quantity delivered
-- Concepts Tested: Window Functions (DENSE_RANK / RANK), PARTITION BY, Common Table Expression (CTE)
-- Expected Output Columns: category, donor_id, donor_name, total_quantity, category_rank
-- ============================================================================
-- Hint 1: First aggregate the total delivered quantity per category and donor in a CTE.
-- Hint 2: Apply DENSE_RANK() OVER (PARTITION BY category ORDER BY total_quantity DESC) and filter rank <= 3.

WITH donor_totals AS (
    SELECT i.category, d.donor_id, d.donor_name,
           SUM(sl.quantity_sent) AS total_quantity
    FROM shipment s
    JOIN shipment_line sl ON sl.shipment_id = s.shipment_id
    JOIN supply_item i ON i.item_id = sl.item_id
    JOIN donor d ON d.donor_id = s.donor_id
    WHERE s.status = 'delivered'
    GROUP BY i.category, d.donor_id, d.donor_name
), ranked AS (
    SELECT *, DENSE_RANK() OVER (
        PARTITION BY category ORDER BY total_quantity DESC
    ) AS category_rank
    FROM donor_totals
)
SELECT category, donor_id, donor_name, total_quantity, category_rank
FROM ranked
WHERE category_rank <= 3
ORDER BY category, category_rank, donor_id;
