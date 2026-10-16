# DBMS Viva Examination Preparation Notes

**Course Project:** Disaster Relief Logistics DB  
**Audience:** B.Tech CSE 2nd / 3rd Year DBMS Course Viva  
**Coverage:** Relational Theory, ER Modelling, Weak Entities, Normalization, Integrity Constraints, Storage Internals, PostgreSQL 16 Architecture  

---

## Section A: Entity-Relationship & Relational Modelling (Q1 – Q10)

### Q1. What is an entity, and what distinguishes a strong entity from a weak entity?
**Answer:** An entity is a distinguishable real-world object with attributes. A **strong entity** has an independent existence and possesses sufficient attributes to form a unique primary key by itself (e.g., `relief_camp`, `volunteer`). A **weak entity** cannot be identified by its own attributes alone and depends on an identifying owner entity for both existence and identification (e.g., `shelter_unit`, `family_member`).

### Q2. What is a partial key / discriminator in a weak entity?
**Answer:** A partial key (or discriminator) is the attribute within a weak entity that uniquely differentiates tuples *under the same owner entity* (e.g., `line_no` in `shipment_line`, `member_no` in `family_member`). It starts from 1 for each owner with no gaps.

### Q3. How is a weak entity represented in relational schema DDL?
**Answer:** In DDL, a weak entity is represented with a composite primary key consisting of the owner's primary key plus the local discriminator: `PRIMARY KEY (owner_id, discriminator_no)`. The foreign key to the owner entity is marked with `ON DELETE CASCADE`.

### Q4. What is an identifying relationship versus a non-identifying relationship?
**Answer:** In an **identifying relationship**, the child entity cannot exist or be identified without the parent, and the parent's primary key becomes part of the child's primary key (represented by a solid line in ER diagrams). In a **non-identifying relationship**, the child has its own independent primary key and the parent's key is merely a foreign key attribute (e.g., `shipment` referencing `donor`).

### Q5. Why does `assignment` have a composite primary key `(volunteer_id, camp_id)`?
**Answer:** `assignment` is an **associative entity** (or junction table) representing a Many-to-Many ($M:N$) relationship between `volunteer` and `relief_camp`. A volunteer can be assigned to multiple camps over time, and a camp has many volunteers. The composite key guarantees that a volunteer cannot have duplicate concurrent assignments to the exact same camp while storing relationship-specific attributes like `role` and `shift`.

### Q6. Why do strong entities use `GENERATED ALWAYS AS IDENTITY` instead of `SERIAL` in PostgreSQL?
**Answer:** `GENERATED ALWAYS AS IDENTITY` is the ANSI SQL:2003 standard standard compliant syntax. `SERIAL` is a legacy PostgreSQL pseudo-type that creates an independent sequence, allows accidental manual overrides without warning, and can desynchronize identity sequences. `GENERATED ALWAYS` prevents accidental manual insertion of explicit keys unless `OVERRIDING SYSTEM VALUE` is specified.

### Q7. What is the difference between `ON DELETE CASCADE` and `ON DELETE RESTRICT`?
**Answer:**
- `ON DELETE CASCADE`: When the parent tuple is deleted, PostgreSQL automatically deletes all referencing child tuples. Used for weak entities (`shipment_line`, `shelter_unit`) whose existence is tied directly to the parent.
- `ON DELETE RESTRICT`: Rejects the deletion of the parent tuple if any referencing child record exists, raising a foreign key violation error. Used between strong entities (`donor`, `relief_camp`) to prevent accidental loss of historical audit trails.

### Q8. What is the difference between physical data independence and logical data independence?
**Answer:**
- **Physical Data Independence:** The ability to modify physical storage structures, access paths, or indexes (e.g., adding a BRIN or B-tree index) without changing conceptual schemas or application queries.
- **Logical Data Independence:** The ability to alter the logical schema (e.g., splitting a table or adding an attribute) without rewriting external views or user queries.

### Q9. Why is `camp_stock` maintained as a separate table instead of calculating it on the fly?
**Answer:** While stock can theoretically be calculated by summing all delivered shipments and subtracting distributions, doing so for every transaction on millions of rows would cause severe disk I/O bottlenecks. Maintaining `camp_stock` enables $O(1)$ point-lookups and row-level locking (`FOR UPDATE`) for real-time inventory reservation.

### Q10. What is referential integrity, and how does PostgreSQL enforce it?
**Answer:** Referential integrity dictates that every foreign key value in a referencing relation must either match a valid candidate key value in the referenced relation or be NULL. PostgreSQL enforces this using internal system triggers that acquire `FOR KEY SHARE` locks on referenced rows and verify foreign key consistency before transaction commit.

---

## Section B: Functional Dependencies & Normalization (Q11 – Q20)

### Q11. Define Functional Dependency ($X \rightarrow Y$).
**Answer:** Given relation $R$, attribute set $Y$ is functionally dependent on $X$ ($X \rightarrow Y$) if and only if for any two tuples $t_1, t_2 \in R$, whenever $t_1[X] = t_2[X]$, it must also hold that $t_1[Y] = t_2[Y]$. $X$ uniquely determines $Y$.

### Q12. What is a candidate key? How is it computed using attribute closure?
**Answer:** A candidate key is a minimal superkey—a set of attributes whose closure ($K^+$) contains all attributes of the relation, and no proper subset of $K$ has this property.

### Q13. What is a partial functional dependency? Which normal form forbids it?
**Answer:** A partial dependency occurs when a non-prime attribute depends on a *proper subset* of a composite candidate key ($A \subsetneq K$ such that $A \rightarrow Y$). It is forbidden in **Second Normal Form (2NF)**.

### Q14. What is a transitive functional dependency? Which normal form forbids it?
**Answer:** A transitive dependency occurs when a non-prime attribute depends on another non-prime attribute ($X \rightarrow Y$ and $Y \rightarrow Z$, where $Y$ is not a candidate key and $Z$ is not a prime attribute). It is forbidden in **Third Normal Form (3NF)**.

### Q15. What are the three classic anomalies that normalization eliminates?
**Answer:**
1. **Insertion Anomaly:** Inability to record certain facts without adding unrelated attributes or fictitious dummy keys.
2. **Deletion Anomaly:** Accidental loss of unrelated data when deleting a tuple containing a composite entity.
3. **Update Anomaly:** Inconsistent data resulting from updating redundant information in only some rows of a table.

### Q16. What is the difference between 3NF and BCNF?
**Answer:** For every non-trivial dependency $X \rightarrow Y$:
- In **3NF**, either $X$ is a superkey, **OR** $Y$ is a prime attribute (part of a candidate key).
- In **BCNF**, $X$ **must** be a superkey, with no exceptions for prime attributes. Every BCNF relation is in 3NF, but not all 3NF relations are in BCNF.

### Q17. When can a relation be in 3NF but fail BCNF?
**Answer:** When there are multiple overlapping candidate keys with cross-key functional dependencies (e.g., keys $(A, B)$ and $(B, C)$ where $C \rightarrow A$). Here $A$ is prime, satisfying 3NF, but $C$ is not a superkey, violating BCNF.

### Q18. What is the Lossless Join Property, and how do we test for it?
**Answer:** A decomposition of relation $R$ into $R_1$ and $R_2$ is lossless if the natural join $R_1 \bowtie R_2 = R$. The formal test states that the intersection of attributes must determine at least one of the decomposed schemas:
$$(R_1 \cap R_2) \rightarrow R_1 \quad \text{or} \quad (R_1 \cap R_2) \rightarrow R_2$$

### Q19. What is Dependency Preservation, and why is it desirable?
**Answer:** Dependency preservation ensures that all original functional dependencies in $F$ can be enforced by checking constraints within individual decomposed tables without computing costly multi-table joins on write operations.

### Q20. Can a BCNF decomposition always preserve dependencies?
**Answer:** No. While 3NF decomposition is mathematically guaranteed to be both lossless and dependency-preserving, certain relations cannot be decomposed into BCNF without losing at least one functional dependency.

---

## Section C: Indexing, Transactions & Storage Internals (Q21 – Q30)

### Q21. Why shouldn't foreign keys automatically have indexes created by PostgreSQL?
**Answer:** Unlike Primary Keys and Unique constraints, PostgreSQL does not automatically create indexes on Foreign Key columns. While indexing FKs speeds up joins and child cascading checks, it adds write and maintenance overhead. Indexes should be intentionally created based on query patterns.

### Q22. What is a Covering Index (Index with `INCLUDE`), and how does it prevent heap fetches?
**Answer:** An index created with the `INCLUDE` clause (e.g., `CREATE INDEX ON shipment_line(shipment_id) INCLUDE (quantity_sent)`) stores non-key payload columns in the leaf pages of the B-Tree. When a query requests these columns, PostgreSQL performs an **Index Only Scan**, eliminating table heap page access entirely.

### Q23. What is a BRIN (Block Range Index), and when is it vastly superior to a B-tree?
**Answer:** A BRIN index stores the minimum and maximum value for physical page ranges on disk rather than indexing every single row tuple. It is hundreds of times smaller than a B-tree and ideal for naturally correlated physical data (e.g., sequential timestamps like `shipment_date` or sequential serial IDs).

### Q24. What is a Partial Index, and what are its advantages?
**Answer:** A partial index is built over a subset of rows defined by a `WHERE` predicate (e.g., `WHERE status = 'delivered'`). It reduces index storage footprint, stays in RAM cache, and accelerates queries filtering on that specific condition without incurring index maintenance on other rows.

### Q25. What is Multi-Version Concurrency Control (MVCC) in PostgreSQL?
**Answer:** MVCC ensures that readers do not block writers and writers do not block readers. When a row is updated or deleted, PostgreSQL does not overwrite the row in place; instead, it writes a new version (tuple) with updated transaction boundary identifiers (`xmin`, `xmax`). Each transaction sees a consistent snapshot based on its isolation level.

### Q26. What is the function of the PostgreSQL VACUUM process?
**Answer:** Because MVCC creates new tuple versions rather than updating in-place, dead tuples accumulate (table bloat). `VACUUM` reclaims storage occupied by dead tuples, freezes transaction IDs to prevent wraparound failure, and updates the visibility map.

### Q27. What are the four ACID properties in DBMS?
**Answer:**
- **Atomicity:** All operations in a transaction succeed, or none take effect.
- **Consistency:** Transactions transition the database from one valid state satisfying all schema constraints to another.
- **Isolation:** Concurrent transactions execute without interfering with one another.
- **Durability:** Committed transaction changes survive system crashes or power failures (guaranteed via Write-Ahead Logging / WAL).

### Q28. What is Write-Ahead Logging (WAL), and why is it necessary?
**Answer:** WAL mandates that changes to data pages must be written to sequential, non-volatile log files on disk *before* the actual data pages are flushed to table files. In the event of a sudden power loss or server crash, PostgreSQL replays the WAL to restore unwritten buffer modifications, guaranteeing Durability with high sequential write throughput.

### Q29. What is the difference between `READ COMMITTED` and `REPEATABLE READ` in PostgreSQL?
**Answer:**
- `READ COMMITTED`: A new snapshot of the database is taken at the start of *each query* within the transaction. Rows committed by concurrent transactions between two queries in the same transaction become visible (Non-Repeatable Read).
- `REPEATABLE READ`: A single snapshot is taken at the start of the *transaction* (first non-utility statement). Subsequent queries see the exact same view of data throughout the transaction.

### Q30. What does `SELECT ... FOR UPDATE SKIP LOCKED` do, and where is it used?
**Answer:** `FOR UPDATE` places exclusive row-level locks on selected rows. Adding `SKIP LOCKED` instructs PostgreSQL to immediately bypass any row that is currently locked by another concurrent session without blocking or waiting. This pattern is optimal for high-throughput, contention-free concurrent worker queues (e.g., emergency supply request dispatching).
