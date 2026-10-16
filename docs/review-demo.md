# ReliefDB: project review demo

## Start the demo

From the project root:

```powershell
cd ui/client
npm ci
npm run dev
```

Open the localhost address printed in the terminal (normally port 5173). Wait for **Browser database ready**. The frontend creates an in-memory PostgreSQL engine, installs the actual project schema, and loads the original seed SQL. It opens **Project overview** and automatically checks Q01 in the background.

Before the review, click **Verify all queries** and confirm **20/20**. Keep the terminal running. No Docker or Express server is needed for this browser demo.

## Suggested opening

“Our project is a relational database for disaster-relief logistics. It connects relief camps, families, volunteers, donors, shipments, supply requests, and inventory. The interface is a database presentation workspace: we can inspect the model, execute SQL, explain the result, and demonstrate integrity constraints.”

## Show the full database first, about one minute

Turn on **Presentation mode** in the top bar for larger SQL and result text. On **Project overview**, show the live totals: 15 tables, 2,580 seed records, 12 camps, and 200 shipments. The constraint panel reads PostgreSQL's catalog and shows 15 primary keys, 16 foreign keys, 13 CHECK constraints, and one separate UNIQUE constraint.

Click **shipment_line** under **Show what is inside**. In **Columns & keys**, explain the composite primary key and the two foreign keys. The named relationship definitions include `ON DELETE CASCADE` for the owning shipment and `ON DELETE RESTRICT` for the supply item. **Open shipment** follows that relationship to the parent table.

Switch to **Browse data** to show all 666 shipment lines, ordered by their primary key. Pagination changes only the displayed rows; the complete result is available for filtering, sorting, and CSV export. Choose 25 or 50 rows per page if useful. Switch to **CREATE TABLE** to show the original SQL definition from `db/01_schema.sql`, including CHECK constraints. Search the table list to find any of the 15 tables. `request_audit` is defined but empty because the audit trigger is a separate, unfinished exercise.

Then open **ER diagram** for the big picture, or return to **Project overview** and start the guided walkthrough below.

## A six-step review, about five to seven minutes

Click **Start review walkthrough**. Each step includes a talking point and a practice viva answer.

1. **Relational model.** Show `shipment_line` in Schema explorer. Explain the composite primary key `(shipment_id, line_no)`, the owner foreign key, and why it is a weak entity. Show **Columns & keys**, **Browse data**, and **CREATE TABLE**. Open ER diagram and use zoom controls if needed. Explain how separating shipment headers from lines avoids duplicated header attributes and partial dependencies.

2. **Joins and aggregation — Q01.** Click **Run query**. The seed result identifies Meppadi High School Relief Camp with 92 registered members, capacity 100, and 92% occupancy. Explain the three-table join, grouping by camp, and why `HAVING` filters an aggregate instead of `WHERE`.

3. **Anti-join — Q08.** Run the query to find the four camps without an assigned medical-skilled volunteer. Explain the correlated `NOT EXISTS`, and why it avoids duplicate camp rows and the NULL pitfalls of `NOT IN`.

4. **Window ranking — Q05.** Run the query and show 18 result rows. Point to `DENSE_RANK() OVER (PARTITION BY category ...)`. Explain that each category gets its own ranking and tied quantities share a rank. Use filtering, sortable result columns, or pagination to inspect a category.

5. **Time-series SQL — Q12.** Run the query. The nine monthly rows use `DATE_TRUNC` and `LAG` to compare months. Open **Execution plan** to show a real `EXPLAIN (ANALYZE, BUFFERS)`. Explain that a sequential scan can be reasonable for a small seed table; do not promise that an index is always faster.

6. **Materialized view — Q20.** Run the multi-statement query. It creates a stored stock summary, adds a unique index, refreshes it concurrently, and returns 47 district–category rows. Explain how a materialized view differs from a normal view such as Q19. Finish with **Verify all queries** to show the independent reference checks.

## One UPDATE that changes the database, about one minute

Open **Change data** in the sidebar. Camp 1 starts with a capacity of **100**. Show the SQL, then click **Apply UPDATE**:

```sql
UPDATE relief_camp
SET capacity = 120
WHERE camp_id = 1
RETURNING camp_id, camp_name, capacity;
```

The current-value card and an independent SELECT show **120**. Click **Open relief_camp table** to see the stored value in **Browse data**. The row count is unchanged: this modifies one existing row. Return to **Change data** and click **Restore original value** to return to 100 before verifying the seed answers. The change is committed in the browser database for the current session; reloading or resetting the seed recreates the original data.

Say: “SELECT reads rows; UPDATE changes stored data. WHERE limits this change to camp 1. RETURNING reports the affected row, and opening the table independently confirms the change.”

## Optional integrity demonstration, about one minute

Open **Data integrity** and test any of the three examples:

- **CHECK:** negative inventory is rejected with SQLSTATE `23514`.
- **FOREIGN KEY:** a shipment referencing a missing donor is rejected with SQLSTATE `23503`.
- **PRIMARY KEY:** a duplicate shelter identity is rejected with SQLSTATE `23505`.

These are actual database exceptions. Each attempt is wrapped in a transaction and rolled back so it cannot corrupt the demonstration seed data.

## Useful controls

- Search query titles or concepts; filter by joins, subqueries, window functions, or views.
- **Edit SQL** opens a temporary browser editor. Ctrl+Enter runs it. **Restore query** returns to the project example.
- **Expand SQL editor** helps present long queries. Escape closes the focused view.
- Result tables support filtering, sorting, pagination, and CSV export.
- **Project overview** connects the logistics workflow to real tables and example queries. Its record totals update after query execution.
- **Presentation mode** enlarges SQL, table data, and talking points without changing the database.
- In Schema explorer, use the **Columns & keys**, **Browse data**, and **CREATE TABLE** tabs. Arrow keys move between tabs. Foreign-key buttons open the referenced table.
- **Execution plan** explains the final SELECT/CTE statement. View exercises install their definitions before that SELECT is explained.
- **Reset seed database** restores the original browser database and clears verification status.
- Reference checks compare column names and complete row multisets; numeric values use the coursework's two-decimal tolerance. A successful custom query may return different data and is labeled **Custom output**.

## Be precise about what is demonstrated

This demo executes PostgreSQL through PGlite in one browser session. It is not connected to the Docker PostgreSQL 16 server, and timings are local browser timings. A full page reload recreates the database. Use Docker and two separate psql sessions for concurrent transaction experiments.

All 20 analytical examples are implemented and verified. Triggers, stored routines, permission grants, and the original concurrency scenarios remain separate coursework tasks; the UI does not claim they are complete. The audit table is therefore empty in the base seed. Q07 deliberately uses 30 September 2026 as its reference date. Q10 measures first matching shipment response, not complete delivery of a requested quantity. Q19's `open_requests` count includes all requests because the current schema has no closed-request status.

## Validation and production preview

```powershell
npm run test:demo
npm run build
npm run preview -- --host 127.0.0.1
```

The automated checks execute all 20 SQL files against the real schema and seed, compare their outputs with the committed CSV references, rerun both view exercises, test CHECK/FK/PK enforcement, and verify a real execution plan. The browser walkthrough was also checked for ranking results, schema keys, ER rendering, and constraint rejection.

Build assets include the PostgreSQL WebAssembly runtime; first load is larger than an ordinary UI. After installing dependencies and building, the core demo uses local assets. External Google Fonts are optional; system font fallbacks keep the UI usable without them.
