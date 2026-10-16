# Indexing & Query Optimization Study

**Student Name:** [Your Name]  
**Course:** DBMS Laboratory (PostgreSQL 16)  
**Dataset Scale:** ~1,000,000 `shipment_line` rows loaded via `make seed-bulk`  

---

## 1. Experimental Methodology
For each benchmark query:
1. Run query without user-defined secondary indexes (Baseline: sequential scan).
2. Record `EXPLAIN (ANALYZE, BUFFERS)` execution plan, total runtime, and shared buffer hits/reads.
3. Apply targeted index strategy (Single-column B-tree, Composite, Partial, Covering with `INCLUDE`, or `BRIN`).
4. Re-run `EXPLAIN (ANALYZE, BUFFERS)` and record the optimized plan, runtime, and buffer reads.
5. Record index disk footprint using `pg_relation_size()`.

---

## 2. Benchmark Summary Table

| Query ID | Description | Index Strategy Evaluated | Execution Plan (Before) | Execution Plan (After) | Runtime Before (ms) | Runtime After (ms) | Buffers (Before / After) | Index Size | Speedup Factor |
|---|---|---|---|---|---|---|---|---|---|
| **Query 1** | Q02 Aggregation per camp & item | Covering Index with `INCLUDE` | Sequential Scan + Hash Aggregate | Index Only Scan / Bitmap Heap | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **Query 2** | Temporal Range Filter on Date | BRIN vs B-Tree | Sequential Scan | Bitmap Index Scan (BRIN) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **Query 3** | Delivered Shipments Filter | Partial B-Tree (`WHERE status='delivered'`) | Seq Scan with Filter | Bitmap Index Scan | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| **Query 4** | Subquery Anti-Join (Q03) | Composite Foreign Key Index | Hash Anti-Join + Seq Scan | Nested Loop / Index Scan | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

---

## 3. Detailed Query Worksheets

### Query 1: Camp & Item Aggregation (`db/indexing/slow_query_01.sql`)
- **Index Applied:**
  ```sql
  CREATE INDEX ix_shipment_line_covering ON shipment_line(shipment_id, item_id) INCLUDE (quantity_sent);
  ```
- **Plan Before:**
  ```text
  [Paste EXPLAIN (ANALYZE, BUFFERS) output here]
  ```
- **Plan After:**
  ```text
  [Paste EXPLAIN (ANALYZE, BUFFERS) output here]
  ```
- **Analysis & Conclusion:**
  *(Explain in student viva language: why INCLUDE avoids table heap lookups via Index-Only Scan)*

---

### Query 2: Date Range Scan (`db/indexing/slow_query_02.sql`)
- **Indexes Applied:**
  ```sql
  CREATE INDEX ix_shipment_date_btree ON shipment(shipment_date);
  CREATE INDEX ix_shipment_date_brin ON shipment USING BRIN(shipment_date);
  ```
- **Plan Before:**
  ```text
  [Paste EXPLAIN output here]
  ```
- **Plan After (B-Tree):**
  ```text
  [Paste EXPLAIN output here]
  ```
- **Plan After (BRIN):**
  ```text
  [Paste EXPLAIN output here]
  ```
- **Analysis & Conclusion:**
  *(Compare BRIN block ranges vs B-tree disk footprint and cache utilization)*

---

### Query 3: Partial Index on Status (`db/indexing/slow_query_03.sql`)
- **Index Applied:**
  ```sql
  CREATE INDEX ix_shipment_delivered_partial ON shipment(camp_id, shipment_id) WHERE status = 'delivered';
  ```
- **Plan Before:**
  ```text
  [Paste EXPLAIN output here]
  ```
- **Plan After:**
  ```text
  [Paste EXPLAIN output here]
  ```
- **Analysis & Conclusion:**
  *(Explain how predicate filtering reduces index size and write overhead)*

---

### Query 4: Anti-Join Correlated Subquery (`db/indexing/slow_query_04.sql`)
- **Index Applied:**
  ```sql
  CREATE INDEX ix_shipment_camp_date ON shipment(camp_id, shipment_date);
  CREATE INDEX ix_shipment_line_item ON shipment_line(item_id, shipment_id);
  ```
- **Plan Before:**
  ```text
  [Paste EXPLAIN output here]
  ```
- **Plan After:**
  ```text
  [Paste EXPLAIN output here]
  ```
- **Analysis & Conclusion:**
  *(Explain index probe behavior during anti-join hash and nested loop joins)*
