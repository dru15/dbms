#!/usr/bin/env python3
"""
generate_stubs.py: Generates educational stubs for Q01-Q20, triggers T01-T05,
routines F01-F04, transactions, and indexing studies.
Adheres strictly to the no-solutions rule.
"""

import os

queries_spec = [
    {
        "id": "Q01",
        "title": "Camps where registered members exceed 90% of capacity",
        "concepts": "INNER JOIN, GROUP BY, Aggregate functions (COUNT), HAVING filter",
        "columns": ["camp_id", "camp_name", "capacity", "registered_members", "occupancy_pct"],
        "hints": [
            "Join relief_camp with registered_family and family_member to aggregate members per camp.",
            "Use the HAVING clause to filter groups where the count of members divided by camp capacity exceeds 0.90."
        ]
    },
    {
        "id": "Q02",
        "title": "Total quantity of each item sent to each camp",
        "concepts": "Multi-table JOIN (shipment, shipment_line, relief_camp, supply_item), GROUP BY, SUM",
        "columns": ["camp_id", "camp_name", "item_id", "item_name", "total_quantity_sent"],
        "hints": [
            "Join relief_camp to shipment, shipment_line, and supply_item.",
            "Group by camp and item identifiers, calculating the total sum of quantity_sent."
        ]
    },
    {
        "id": "Q03",
        "title": "Pending critical requests with no later shipment of the same item to that camp",
        "concepts": "Anti-join / Correlated Subquery with NOT EXISTS, Date comparison",
        "columns": ["request_id", "request_date", "camp_id", "camp_name", "item_id", "item_name", "urgency"],
        "hints": [
            "Filter supply_request for urgency = 'critical'.",
            "Use NOT EXISTS to verify there are no matching shipments to the same camp on or after the request date."
        ]
    },
    {
        "id": "Q04",
        "title": "Donors who have shipped to every camp",
        "concepts": "Relational Division, GROUP BY, HAVING COUNT(DISTINCT ...)",
        "columns": ["donor_id", "donor_name"],
        "hints": [
            "Compare the number of distinct camps each donor has shipped to against the total number of camps.",
            "Relational division can be expressed using GROUP BY donor and a subquery in HAVING."
        ]
    },
    {
        "id": "Q05",
        "title": "Top 3 donors per item category by total quantity delivered",
        "concepts": "Window Functions (DENSE_RANK / RANK), PARTITION BY, Common Table Expression (CTE)",
        "columns": ["category", "donor_id", "donor_name", "total_quantity", "category_rank"],
        "hints": [
            "First aggregate the total delivered quantity per category and donor in a CTE.",
            "Apply DENSE_RANK() OVER (PARTITION BY category ORDER BY total_quantity DESC) and filter rank <= 3."
        ]
    },
    {
        "id": "Q06",
        "title": "Unmet demand per camp and item: requested minus delivered, only positive",
        "concepts": "Common Table Expressions (CTEs), FULL OUTER JOIN / COALESCE, Arithmetic difference",
        "columns": ["camp_id", "camp_name", "item_id", "item_name", "qty_requested", "qty_delivered", "unmet_quantity"],
        "hints": [
            "Calculate total requested quantity and total delivered quantity in separate CTEs.",
            "Join the CTEs and compute (qty_requested - qty_delivered), keeping only rows where the difference is strictly positive."
        ]
    },
    {
        "id": "Q07",
        "title": "Volunteers with expired certifications currently assigned to a camp",
        "concepts": "INNER JOIN across volunteer, volunteer_certification, assignment, Date comparison",
        "columns": ["volunteer_id", "volunteer_name", "cert_name", "expiry_date", "camp_id", "camp_name"],
        "hints": [
            "Join active volunteer assignments with their certifications.",
            "Compare certification expiry_date against the current active operational period."
        ]
    },
    {
        "id": "Q08",
        "title": "Camps with no medical-skilled volunteer currently assigned",
        "concepts": "Anti-join using NOT EXISTS or NOT IN with subquery",
        "columns": ["camp_id", "camp_name", "district"],
        "hints": [
            "Find camps that do not exist in the set of camps currently assigned to volunteers with skill = 'medical'.",
            "Use NOT EXISTS or EXCEPT to isolate the understaffed camps."
        ]
    },
    {
        "id": "Q09",
        "title": "Running total of delivered quantity per camp over time",
        "concepts": "Window Function SUM(...) OVER (PARTITION BY ... ORDER BY ...)",
        "columns": ["camp_id", "camp_name", "shipment_id", "shipment_date", "quantity_sent", "running_total_quantity"],
        "hints": [
            "Join relief_camp, shipment, and shipment_line filtering for delivered shipments.",
            "Use SUM(quantity_sent) OVER (PARTITION BY camp_id ORDER BY shipment_date, shipment_id) for cumulative progression."
        ]
    },
    {
        "id": "Q10",
        "title": "Average days from request to first fulfilling shipment",
        "concepts": "CTE, MIN aggregate with date arithmetic, AVG function",
        "columns": ["avg_days_to_fulfillment"],
        "hints": [
            "For each request_line, determine the minimum shipment_date matching camp and item on or after request_date.",
            "Calculate the day difference for fulfilled requests, and compute the average across all pairs."
        ]
    },
    {
        "id": "Q11",
        "title": "Per camp: count of vulnerable children under 5 and elders over 60",
        "concepts": "Conditional Aggregation using FILTER (WHERE ...) or CASE WHEN",
        "columns": ["camp_id", "camp_name", "children_under_5", "elders_over_60"],
        "hints": [
            "Join relief_camp with registered_family and family_member.",
            "Use COUNT(*) FILTER (WHERE age < 5) and COUNT(*) FILTER (WHERE age > 60) grouped by camp."
        ]
    },
    {
        "id": "Q12",
        "title": "Month-over-month change in shipment volume",
        "concepts": "Time-series aggregation, Window Function LAG() OVER (ORDER BY ...)",
        "columns": ["shipment_month", "monthly_shipments", "previous_month_shipments", "mom_change"],
        "hints": [
            "Truncate shipment_date to month using DATE_TRUNC('month', ...) and count shipments.",
            "Use LAG() to access the previous month count and calculate the difference."
        ]
    },
    {
        "id": "Q13",
        "title": "Items requested but never shipped anywhere",
        "concepts": "Set Difference, LEFT JOIN ... WHERE ... IS NULL or NOT IN",
        "columns": ["item_id", "item_name", "category"],
        "hints": [
            "Identify items present in request_line that have zero appearances in shipment_line.",
            "A LEFT JOIN from supply_item with an IS NULL condition or NOT EXISTS works cleanly."
        ]
    },
    {
        "id": "Q14",
        "title": "Total shelter capacity vs registered members per camp",
        "concepts": "Aggregating multiple 1:N dimensions independently via CTEs before joining",
        "columns": ["camp_id", "camp_name", "total_shelter_capacity", "total_registered_members", "capacity_difference"],
        "hints": [
            "Avoid Cartesian fanout: compute SUM(unit_capacity) in one CTE and COUNT(member_no) in a separate CTE.",
            "Join both CTEs back to relief_camp to calculate the net difference."
        ]
    },
    {
        "id": "Q15",
        "title": "Pairs of volunteers with the same skill assigned to the same camp",
        "concepts": "Self-Join on assignment and volunteer, deduplication using inequality (<)",
        "columns": ["camp_id", "camp_name", "skill", "volunteer_1_id", "volunteer_1_name", "volunteer_2_id", "volunteer_2_name"],
        "hints": [
            "Self-join the assignment table on camp_id where v1.volunteer_id < v2.volunteer_id.",
            "Join volunteer tables twice to compare and ensure matching skills."
        ]
    },
    {
        "id": "Q16",
        "title": "Camps whose total received supply quantity is above the cross-camp average",
        "concepts": "Subquery in HAVING, Scalar Aggregate comparison",
        "columns": ["camp_id", "camp_name", "total_received_quantity"],
        "hints": [
            "Group delivered shipment quantities by camp.",
            "Filter groups using HAVING total > (SELECT AVG(camp_total) FROM ...)."
        ]
    },
    {
        "id": "Q17",
        "title": "Items that were requested or shipped but not both",
        "concepts": "Symmetric Difference, FULL OUTER JOIN / UNION / EXCEPT",
        "columns": ["item_id", "item_name", "activity_type"],
        "hints": [
            "Find items in request_line and items in shipment_line.",
            "Return items that appear in one set but not both, labeling their activity status."
        ]
    },
    {
        "id": "Q18",
        "title": "Donors with shipments in every month of the operational seed period",
        "concepts": "Relational Division, COUNT(DISTINCT DATE_TRUNC('month', ...))",
        "columns": ["donor_id", "donor_name", "distinct_months_count"],
        "hints": [
            "Extract distinct months from shipment_date per donor.",
            "Use HAVING COUNT(DISTINCT month) = 9 (the total number of operational months)."
        ]
    },
    {
        "id": "Q19",
        "title": "View: camp_status_dashboard",
        "concepts": "Database Views (CREATE OR REPLACE VIEW), Multi-table metrics summary",
        "columns": ["camp_id", "camp_name", "capacity", "registered_members", "open_requests", "assigned_volunteers"],
        "hints": [
            "Create a view named camp_status_dashboard summarizing camp demographics and operations.",
            "Aggregate registered family members, pending requests, and assigned volunteers using CTEs or scalar subqueries."
        ]
    },
    {
        "id": "Q20",
        "title": "Materialized View: stock by category per district with refresh statement",
        "concepts": "CREATE MATERIALIZED VIEW, REFRESH MATERIALIZED VIEW CONCURRENTLY",
        "columns": ["district", "category", "total_quantity_on_hand"],
        "hints": [
            "Create a materialized view named mv_district_category_stock aggregating camp_stock by district and category.",
            "Include the REFRESH MATERIALIZED VIEW statement to demonstrate how it is updated."
        ]
    }
]

def make_query_stub(q):
    cols_str = ", ".join(q["columns"])
    hints_str = "\n".join([f"-- Hint {i+1}: {h}" for i, h in enumerate(q["hints"])])
    content = f"""-- ============================================================================
-- Query ID: {q["id"]}
-- Problem Statement: {q["title"]}
-- Concepts Tested: {q["concepts"]}
-- Expected Output Columns: {cols_str}
-- ============================================================================
{hints_str}

-- Stub: Replace with your analytical query solution
SELECT 'TODO' AS not_attempted;
"""
    return content

for q in queries_spec:
    path = os.path.join("db", "queries", f"{q['id']}.sql")
    with open(path, "w", encoding="utf-8") as f:
        f.write(make_query_stub(q))
print("Generated 20 query stubs.")
