#!/usr/bin/env python3
"""
generate_transaction_stubs.py: Generates transaction scenario stubs (scenario_01 to scenario_07)
and docs/transaction-log.md template.
"""

import os

scenarios = [
    {
        "id": "scenario_01_lost_update",
        "title": "Scenario 1: Lost Update on camp_stock",
        "isolation": "READ COMMITTED",
        "desc": "Two concurrent sessions attempt to decrement stock for the same item at the same camp without locking.",
        "steps": [
            "Session 1: Read stock for Camp 1, Item 1 (e.g. quantity = 150).",
            "Session 2: Read stock for Camp 1, Item 1 (also reads 150).",
            "Session 1: Update stock to (150 - 20 = 130) and commit.",
            "Session 2: Update stock to (150 - 30 = 120) and commit.",
            "Outcome to observe: Session 1's decrement is completely lost (final stock is 120 instead of 100).",
            "Remedy to test: Use SELECT ... FOR UPDATE to eliminate lost update."
        ]
    },
    {
        "id": "scenario_02_non_repeatable_read",
        "title": "Scenario 2: Non-Repeatable Read",
        "isolation": "READ COMMITTED vs REPEATABLE READ",
        "desc": "Session 1 reads the same row twice within a single transaction, while Session 2 modifies it in between.",
        "steps": [
            "Session 1: BEGIN ISOLATION LEVEL READ COMMITTED; SELECT capacity FROM relief_camp WHERE camp_id = 1;",
            "Session 2: BEGIN; UPDATE relief_camp SET capacity = capacity + 20 WHERE camp_id = 1; COMMIT;",
            "Session 1: Re-execute SELECT capacity FROM relief_camp WHERE camp_id = 1; (Observe value changed mid-transaction).",
            "Repeat under REPEATABLE READ: Observe snapshot isolation preserving the original value."
        ]
    },
    {
        "id": "scenario_03_phantom_read",
        "title": "Scenario 3: Phantom Read Prevention under REPEATABLE READ",
        "isolation": "REPEATABLE READ",
        "desc": "Session 1 runs a range query, Session 2 inserts a new row matching the range and commits, Session 1 re-runs the range query.",
        "steps": [
            "Session 1: BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ; SELECT COUNT(*) FROM family_member WHERE family_id = 1;",
            "Session 2: INSERT INTO family_member VALUES (1, 99, 'Phantom Member', 25, NULL); COMMIT;",
            "Session 1: Re-run SELECT COUNT(*) FROM family_member WHERE family_id = 1;",
            "Outcome in PostgreSQL: Phantom read is PREVENTED by MVCC snapshot (unlike standard SQL 1992 anomaly rules)."
        ]
    },
    {
        "id": "scenario_04_serialization_failure",
        "title": "Scenario 4: Serialization Failure under SERIALIZABLE with Client Retry",
        "isolation": "SERIALIZABLE",
        "desc": "Two transactions produce a write skew / cycle that cannot be scheduled serially.",
        "steps": [
            "Session 1: BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE; SELECT SUM(quantity_on_hand) FROM camp_stock WHERE camp_id = 1;",
            "Session 2: BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE; SELECT SUM(quantity_on_hand) FROM camp_stock WHERE camp_id = 1;",
            "Session 1: UPDATE camp_stock SET quantity_on_hand = quantity_on_hand - 10 WHERE camp_id = 1 AND item_id = 1;",
            "Session 2: UPDATE camp_stock SET quantity_on_hand = quantity_on_hand - 10 WHERE camp_id = 1 AND item_id = 2;",
            "Session 1: COMMIT;",
            "Session 2: COMMIT; -> Observe ERROR 40001: could not serialize access due to read/write dependencies among transactions.",
            "Client action: Catch 40001 and execute automatic retry."
        ]
    },
    {
        "id": "scenario_05_deadlock",
        "title": "Scenario 5: Deadlock between Two Stock Transfers",
        "isolation": "READ COMMITTED",
        "desc": "Session 1 locks row A then requests row B; Session 2 locks row B then requests row A.",
        "steps": [
            "Session 1: BEGIN; UPDATE camp_stock SET quantity_on_hand = quantity_on_hand - 5 WHERE camp_id = 1 AND item_id = 1;",
            "Session 2: BEGIN; UPDATE camp_stock SET quantity_on_hand = quantity_on_hand - 5 WHERE camp_id = 1 AND item_id = 2;",
            "Session 1: UPDATE camp_stock SET quantity_on_hand = quantity_on_hand + 5 WHERE camp_id = 1 AND item_id = 2; (Waits for Session 2)",
            "Session 2: UPDATE camp_stock SET quantity_on_hand = quantity_on_hand + 5 WHERE camp_id = 1 AND item_id = 1; (Deadlock!)",
            "Outcome to observe: PostgreSQL deadlock detector triggers after deadlock_timeout (1s), aborting one session with ERROR 40P01."
        ]
    },
    {
        "id": "scenario_06_savepoint_rollback",
        "title": "Scenario 6: Partial Rollback using SAVEPOINT",
        "isolation": "READ COMMITTED",
        "desc": "Demonstrate graceful recovery inside a long multi-step transaction without aborting previous valid statements.",
        "steps": [
            "Session 1: BEGIN;",
            "Session 1: INSERT INTO supply_request (request_date, urgency, camp_id) VALUES ('2026-09-01', 'medium', 1);",
            "Session 1: SAVEPOINT sp_before_bad_insert;",
            "Session 1: INSERT INTO family_member VALUES (1, 1, 'Duplicate Key Error', 30, NULL); -- Intentionally fails PK",
            "Session 1: ROLLBACK TO SAVEPOINT sp_before_bad_insert;",
            "Session 1: COMMIT; -- The request insert persists while error is isolated."
        ]
    },
    {
        "id": "scenario_07_skip_locked",
        "title": "Scenario 7: Work Queue Concurrency using SELECT FOR UPDATE SKIP LOCKED",
        "isolation": "READ COMMITTED",
        "desc": "Multiple worker sessions process pending supply requests without blocking or contention.",
        "steps": [
            "Session 1: BEGIN; SELECT request_id FROM supply_request WHERE urgency = 'critical' ORDER BY request_id LIMIT 1 FOR UPDATE SKIP LOCKED;",
            "Session 2: BEGIN; SELECT request_id FROM supply_request WHERE urgency = 'critical' ORDER BY request_id LIMIT 1 FOR UPDATE SKIP LOCKED;",
            "Outcome: Session 2 immediately gets the next available critical request without waiting for Session 1 to commit!"
        ]
    }
]

for sc in scenarios:
    steps_txt = "\n".join([f"-- Step {i+1}: {st}" for i, st in enumerate(sc["steps"])])
    content = f"""-- ============================================================================
-- {sc["title"]}
-- Isolation Level: {sc["isolation"]}
-- Description: {sc["desc"]}
-- ============================================================================
-- Guided Scenario Steps:
{steps_txt}
-- ============================================================================

-- SESSION 1 SCRIPT STUB:
-- Open psql session 1 and execute step-by-step:
/*
-- TODO: Paste Session 1 commands here
*/

-- SESSION 2 SCRIPT STUB:
-- Open psql session 2 and execute step-by-step:
/*
-- TODO: Paste Session 2 commands here
*/
"""
    with open(os.path.join("db", "transactions", f"{sc['id']}.sql"), "w", encoding="utf-8") as f:
        f.write(content)

# Template file docs/transaction-log.md
log_md = """# Transaction Concurrency & Isolation Experiments Log

**Student Name:** [Your Name]  
**Course:** DBMS Laboratory  
**Database Engine:** PostgreSQL 16  

---

## Experiment Summary Table

| Scenario ID | Isolation Level | Anomaly / Behavior Tested | Outcome Observed | Prevented By / Resolution |
|-------------|-----------------|---------------------------|------------------|---------------------------|
| Scenario 1  | READ COMMITTED  | Lost Update               | [Pending test]   | `SELECT ... FOR UPDATE`   |
| Scenario 2  | READ COMMITTED vs REPEATABLE READ | Non-Repeatable Read | [Pending test] | Snapshot Isolation / MVCC |
| Scenario 3  | REPEATABLE READ | Phantom Read              | [Pending test]   | PostgreSQL MVCC Predicate |
| Scenario 4  | SERIALIZABLE    | Serialization Failure (40001) | [Pending test] | Automatic Client Retry    |
| Scenario 5  | READ COMMITTED  | Deadlock (40P01)          | [Pending test]   | Lock ordering / Detector  |
| Scenario 6  | READ COMMITTED  | Partial Rollback          | [Pending test]   | `SAVEPOINT`               |
| Scenario 7  | READ COMMITTED  | Work Queue Lock Contention | [Pending test]  | `FOR UPDATE SKIP LOCKED`  |

---

## Detailed Observation Logs

### Scenario 1: Lost Update on camp_stock
- **Commands Executed (Session 1):**
  ```sql
  -- Paste your exact commands here
  ```
- **Commands Executed (Session 2):**
  ```sql
  -- Paste your exact commands here
  ```
- **Observed Result & Explanation:**
  *(Explain in viva language: how read-committed allowed both sessions to read stale stock before write)*

---

### Scenario 2: Non-Repeatable Read
- **Commands & Observations:**
  *(Explain snapshot isolation behavior between READ COMMITTED and REPEATABLE READ)*

---

### Scenario 3: Phantom Read under REPEATABLE READ
- **Commands & Observations:**
  *(Explain how PostgreSQL REPEATABLE READ prevents phantoms without table-level locks)*

---

### Scenario 4: Serialization Failure & Retry
- **Commands & Observations:**
  *(Document the exact error 40001 message and the retry loop)*

---

### Scenario 5: Deadlock between Two Transfers
- **Commands & Observations:**
  *(Document the 40P01 error message and deadlock detection graph)*

---

### Scenario 6: SAVEPOINT Partial Rollback
- **Commands & Observations:**
  *(Document the successful recovery from intentional constraint violation)*

---

### Scenario 7: Work Queue with SKIP LOCKED
- **Commands & Observations:**
  *(Document non-blocking concurrent queue consumer reads)*
"""

with open(os.path.join("docs", "transaction-log.md"), "w", encoding="utf-8") as f:
    f.write(log_md)

print("Generated transaction stubs and docs/transaction-log.md.")
