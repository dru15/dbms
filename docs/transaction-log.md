# Transaction Concurrency & Isolation Experiments Log

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
