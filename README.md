# Disaster Relief Logistics Database (PostgreSQL 16)

A course project for Database Management Systems (B.Tech CSE), demonstrating relational modelling with weak entities, BCNF normalization, transactional concurrency control, procedural routines, and indexing optimizations.

---

## Review demo — no Docker required

The redesigned **ReliefDB Database Studio** runs the original project schema and seed data in a real, local PostgreSQL engine using PGlite. Its project overview connects the relief workflow to live record counts and database constraints. Browse complete table data, follow foreign-key relationships, and inspect the original CREATE TABLE statements. It includes 20 completed SQL examples, an editable SQL workspace, actual execution plans, integrity demonstrations, and a six-step guided review with presenter notes and viva questions. Presentation mode enlarges SQL and results for classroom screens.

With Node.js installed, run:

```powershell
cd ui/client
npm ci
npm run dev
```

Open the localhost URL printed by Vite, then click **Start review walkthrough**. The database is created in browser memory; changes reset when the page reloads. Query results and timings are executed locally, not simulated. Browser-engine timings are not PostgreSQL 16 server benchmarks, and this single-session demo does not demonstrate concurrent database sessions.

```powershell
npm run test:demo  # Execute all 20 queries and verify reference results and constraints
npm run build     # Build the standalone UI, including database assets
npm run preview   # Preview the production build
```

The bundle regenerates from `db/01_schema.sql`, `db/02_seed.sql`, `db/queries/`, and `tests/expected/` before each development/build run. Browser edits are temporary and do not modify SQL files on disk. The Docker workflow below remains available for server-based SQL and concurrency work.

See [the presentation guide](docs/review-demo.md) for a suggested review script and limitations.

---

## Quickstart

### Prerequisites
- Docker & Docker Compose
- Make
- Python 3 (standard library only; no extra pip packages required)

### 1. Launch & Reset Database
Start the PostgreSQL 16 container and initialize the schema with deterministic seed data:
```bash
docker compose up -d
make reset
```

### 2. Run Test Suite
Run the automated test runner to check your query implementations against the independent reference oracle:
```bash
make test
```

### 3. Open Interactive psql Session
Connect to the database terminal directly inside the container:
```bash
make psql
```

---

## Makefile Targets

| Target | Description |
|---|---|
| `make up` | Starts the PostgreSQL container and waits until it is ready to accept connections. |
| `make down` | Stops and removes container resources. |
| `make reset` | Drops all tables, applies roles (`00_roles.sql`), creates authoritative schema (`01_schema.sql`), and loads deterministic seed data (`02_seed.sql`). |
| `make seed-bulk` | Generates ~1,000,000 shipment lines for indexing benchmarks. |
| `make test` | Executes the test harness (`python3 tests/runner.py`) comparing queries Q01–Q20 against expected CSVs. |
| `make psql` | Launches an interactive psql session inside the Docker container. |

---

## Directory Structure

```text
supplyCHAIN/
├── Makefile                     # Build, migration, and test targets
├── docker-compose.yml           # PostgreSQL 16 Alpine configuration
├── README.md                    # Project overview and run guide
├── db/
│   ├── 00_roles.sql             # DCL roles (camp_manager, donor_relations, auditor)
│   ├── 01_schema.sql            # Authoritative DDL schema (15 tables)
│   ├── 02_seed.sql              # Deterministic Indian disaster relief seed dataset
│   ├── 03_seed_bulk.sql         # Bulk data generator (~1M rows for indexing)
│   ├── queries/                 # Analytical query stubs Q01.sql to Q20.sql
│   ├── triggers/                # Trigger stubs T01.sql to T05.sql
│   ├── routines/                # Stored function/procedure stubs F01.sql to F04.sql
│   ├── transactions/            # Concurrency scenario scripts (Scenario 1 to 7)
│   └── indexing/                # Benchmark slow queries for index evaluation
├── docs/
│   ├── er-diagram.md            # Mermaid ER diagram & weak entity documentation
│   ├── normalization.md         # 1NF -> 2NF -> 3NF -> BCNF decomposition guide
│   ├── viva-notes.md            # 30 curated viva examination Q&As
│   ├── transaction-log.md       # Student concurrency test observation worksheet
│   └── index-study.md           # EXPLAIN (ANALYZE, BUFFERS) benchmark template
├── scripts/
│   ├── generate_seed.py         # Deterministic seed generator
│   ├── generate_stubs.py        # Query stubs generator
│   └── generate_trigger_routine_stubs.py
└── tests/
    ├── runner.py                # Test harness reporting PASS / FAIL / NOT ATTEMPTED
    ├── generate_expected.py     # Independent Python oracle for reference answers
    └── expected/                # Reference CSV outputs for Q01-Q20
```

---

## Coursework Guidelines for Students

### Analytical Queries (Q01 – Q20)
Each query in `db/queries/Qxx.sql` includes an implemented example with its problem statement, concepts tested, expected column names, and hints.
1. Open `db/queries/Qxx.sql` in your editor.
2. Review the implementation or experiment with an alternative SQL solution.
3. Run `make test` to verify your query against `tests/expected/Qxx.csv`.

### Concurrency & Isolation Scenarios
Read `db/transactions/` and use two separate terminal windows with `make psql` to reproduce lost updates, non-repeatable reads, phantoms, deadlocks, and savepoints. Record your observations in `docs/transaction-log.md`.

### Indexing Study
Load bulk data using `make seed-bulk`, run `EXPLAIN (ANALYZE, BUFFERS)` on `db/indexing/slow_query_0x.sql`, try different indexing strategies, and complete `docs/index-study.md`.
