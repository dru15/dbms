# Relational Database Normalization Guide

**Course Project:** Disaster Relief Logistics DB  
**Subject:** Database Management Systems (CS204 / CS301)  
**Standard:** 1NF $\rightarrow$ 2NF $\rightarrow$ 3NF $\rightarrow$ BCNF Formal Decomposition  

---

## 1. Overview of Normalization Theory

Normalization is the systematic process of organizing relation schemas to reduce data redundancy and eliminate update, insertion, and deletion anomalies while ensuring:
1. **Lossless Join Property:** Decomposition $D = \{R_1, R_2\}$ must satisfy:
   $$R_1 \cap R_2 \rightarrow R_1 \quad \text{or} \quad R_1 \cap R_2 \rightarrow R_2$$
   meaning the natural join of the decomposed relations reconstructs the original relation without spurious tuples.
2. **Dependency Preservation:** Every functional dependency in the original set $F$ can be enforced within individual decomposed relations without requiring cross-table joins.

### Definitions of Normal Forms
- **First Normal Form (1NF):** All attribute domains contain only atomic (indivisible) values. No repeating groups or multi-valued attributes.
- **Second Normal Form (2NF):** Relation is in 1NF, and **no non-prime attribute is partially dependent** on any candidate key (every non-prime attribute is fully functionally dependent on every candidate key).
- **Third Normal Form (3NF):** Relation is in 2NF, and **no non-prime attribute is transitively dependent** on a candidate key. Formally, for every non-trivial $X \rightarrow Y$:
  - $X$ is a superkey, **OR**
  - $Y$ is a prime attribute (part of some candidate key).
- **Boyce-Codd Normal Form (BCNF):** For every non-trivial functional dependency $X \rightarrow Y$, **$X$ must be a superkey**.

---

## 2. Table-by-Table Normalization Analysis

---

### Case 1: `ShelterUnitFlat`
**Initial Schema:**  
`ShelterUnitFlat(camp_id, unit_no, camp_name, district, unit_type, unit_capacity)`

#### 1. Candidate Key & Primary Key Determination
- **Given Attributes:** $\{ \text{camp\_id}, \text{unit\_no}, \text{camp\_name}, \text{district}, \text{unit\_type}, \text{unit\_capacity} \}$
- **Functional Dependencies ($F$):**
  1. $FD_1: \{\text{camp\_id}, \text{unit\_no}\} \rightarrow \{\text{unit\_type}, \text{unit\_capacity}\}$ **[Full Functional Dependency]**
  2. $FD_2: \text{camp\_id} \rightarrow \{\text{camp\_name}, \text{district}\}$ **[Partial Dependency]**
  3. $FD_3: \text{camp\_name} \rightarrow \text{camp\_id}$ *(Assuming unique camp names within district)*

**Formal Attribute Closure Computation:**
Let us compute the closure of the composite attribute set $\{\text{camp\_id}, \text{unit\_no}\}$:
$$\{\text{camp\_id}, \text{unit\_no}\}^+ = \{\text{camp\_id}, \text{unit\_no}\}$$
Using $FD_1$: adds $\{\text{unit\_type}, \text{unit\_capacity}\}$  
Using $FD_2$: adds $\{\text{camp\_name}, \text{district}\}$  
$$\{\text{camp\_id}, \text{unit\_no}\}^+ = \{\text{camp\_id}, \text{unit\_no}, \text{camp\_name}, \text{district}, \text{unit\_type}, \text{unit\_capacity}\}$$
Since the closure contains all attributes in the relation, $\{\text{camp\_id}, \text{unit\_no}\}$ is a superkey. No proper subset can determine `unit_type` or `unit_capacity`, so:
$$\mathbf{Primary\ Key} = \{\text{camp\_id}, \text{unit\_no}\}$$
- **Prime Attributes:** `camp_id`, `unit_no`
- **Non-Prime Attributes:** `camp_name`, `district`, `unit_type`, `unit_capacity`

#### 2. Anomalies in Un-normalized Flat Table
Consider the un-normalized table:

| camp_id | unit_no | camp_name | district | unit_type | unit_capacity |
|---|---|---|---|---|---|
| 1 | 1 | Meppadi Camp | Wayanad | tent | 6 |
| 1 | 2 | Meppadi Camp | Wayanad | hall | 20 |
| 1 | 3 | Meppadi Camp | Wayanad | prefab | 12 |

- **Redundancy:** The pair `(Meppadi Camp, Wayanad)` is repeated for every shelter unit in camp 1.
- **Insertion Anomaly:** Cannot record a newly designated relief camp in the database until it builds its first shelter unit (since `unit_no` is part of the primary key and cannot be NULL).
- **Update Anomaly:** If the camp name changes from "Meppadi Camp" to "Meppadi Central Camp", multiple tuples must be updated. Updating only one creates an inconsistent state.
- **Deletion Anomaly:** If a camp dismantles all its shelter units (deleting rows `(1, 1)`, `(1, 2)`, `(1, 3)`), all records of the camp's existence and district are accidentally lost.

#### 3. Step-by-Step Decomposition

##### 1NF Check:
All values are atomic $\implies$ In 1NF.

##### 2NF Decomposition:
$FD_2: \text{camp\_id} \rightarrow \{\text{camp\_name}, \text{district}\}$ violates 2NF because the non-prime attributes `camp_name` and `district` depend on `camp_id`, which is a proper subset of the composite primary key $\{\text{camp\_id}, \text{unit\_no}\}$ (**Partial Dependency**).

We decompose into:
1. `relief_camp(camp_id, camp_name, district)`
   - Primary Key: `camp_id`
   - Functional Dependency: $\text{camp\_id} \rightarrow \{\text{camp\_name}, \text{district}\}$
2. `shelter_unit(camp_id, unit_no, unit_type, unit_capacity)`
   - Primary Key: `(camp_id, unit_no)`
   - Functional Dependency: $\{\text{camp\_id}, \text{unit\_no}\} \rightarrow \{\text{unit\_type}, \text{unit\_capacity}\}$
   - Foreign Key: `camp_id` references `relief_camp(camp_id)` ON DELETE CASCADE.

##### 3NF & BCNF Check:
- In `relief_camp`: LHS is `camp_id`, which is the candidate key $\implies$ in 3NF and BCNF.
- In `shelter_unit`: LHS is `(camp_id, unit_no)`, which is the candidate key $\implies$ in 3NF and BCNF.

##### Lossless Join & Dependency Preservation:
- **Common attribute:** `relief_camp` $\cap$ `shelter_unit` = $\{\text{camp\_id}\}$.
- Since $\text{camp\_id} \rightarrow \text{relief\_camp}$, the intersection is a superkey of `relief_camp`. Hence, the decomposition is **guaranteed lossless**.
- All original functional dependencies ($FD_1, FD_2$) are preserved.

---

### Case 2: `ShipmentLineFlat`
**Initial Schema:**  
`ShipmentLineFlat(shipment_id, line_no, shipment_date, donor_id, donor_name, camp_id, item_id, item_name, unit, quantity_sent)`

#### 1. Functional Dependencies & Classification
- **Primary Key:** `(shipment_id, line_no)`
- **Dependencies ($F$):**
  1. $FD_1: \{\text{shipment\_id}, \text{line\_no}\} \rightarrow \{\text{item\_id}, \text{quantity\_sent}\}$ **[Full Dependency]**
  2. $FD_2: \text{shipment\_id} \rightarrow \{\text{shipment\_date}, \text{donor\_id}, \text{camp\_id}\}$ **[Partial Dependency on PK]**
  3. $FD_3: \text{donor\_id} \rightarrow \text{donor\_name}$ **[Transitive Dependency via shipment_id]**
  4. $FD_4: \text{item\_id} \rightarrow \{\text{item\_name}, \text{unit}\}$ **[Transitive Dependency via (shipment_id, line_no)]**

#### 2. Anomalies in Flat Table
- **Insertion Anomaly:** Cannot register a new donor or a newly cataloged supply item until a shipment containing them is created.
- **Update Anomaly:** Changing a donor's name or an item's unit of measure requires updating thousands of shipment line rows.
- **Deletion Anomaly:** Deleting the only shipment delivered by an NGO deletes the NGO's contact record entirely.

#### 3. Step-by-Step Decomposition

##### To 2NF (Eliminate Partial Dependencies):
$FD_2$ is partial because `shipment_id` is a proper subset of `(shipment_id, line_no)`.  
Decompose into:
1. `ShipmentHeader(shipment_id, shipment_date, donor_id, donor_name, camp_id)`
2. `ShipmentLineSub(shipment_id, line_no, item_id, item_name, unit, quantity_sent)`

##### To 3NF / BCNF (Eliminate Transitive Dependencies):
- In `ShipmentHeader`: $\text{donor\_id} \rightarrow \text{donor\_name}$ is a transitive dependency ($\text{shipment\_id} \rightarrow \text{donor\_id} \rightarrow \text{donor\_name}$ where `donor_id` is not a superkey).  
  Decompose into:
  - `donor(donor_id, donor_name)` [PK: `donor_id`]
  - `shipment(shipment_id, shipment_date, donor_id, camp_id)` [PK: `shipment_id`]
- In `ShipmentLineSub`: $\text{item\_id} \rightarrow \{\text{item\_name}, \text{unit}\}$ is a transitive dependency.  
  Decompose into:
  - `supply_item(item_id, item_name, unit)` [PK: `item_id`]
  - `shipment_line(shipment_id, line_no, item_id, quantity_sent)` [PK: `(shipment_id, line_no)`]

##### Resulting Schema:
- `donor(donor_id, donor_name)`
- `supply_item(item_id, item_name, unit)`
- `shipment(shipment_id, shipment_date, donor_id, camp_id)`
- `shipment_line(shipment_id, line_no, item_id, quantity_sent)`

##### Proof of Lossless Join & Dependency Preservation:
- Every decomposed join attribute forms a primary key in its respective parent table.
- All functional dependencies $FD_1, FD_2, FD_3, FD_4$ are preserved in isolated tables.

---

### Case 3: `RequestLineFlat`
**Initial Schema:**  
`RequestLineFlat(request_id, line_no, request_date, camp_id, urgency, item_id, qty_requested)`

#### 1. Functional Dependencies
- **Primary Key:** `(request_id, line_no)`
- **Dependencies:**
  1. $FD_1: \{\text{request\_id}, \text{line\_no}\} \rightarrow \{\text{item\_id}, \text{qty\_requested}\}$ **[Full]**
  2. $FD_2: \text{request\_id} \rightarrow \{\text{request\_date}, \text{camp\_id}, \text{urgency}\}$ **[Partial Dependency]**

#### 2. Decomposition
- **2NF Violation:** `request_id` determines request header attributes while being only a part of the primary key.
- **Decompose into:**
  1. `supply_request(request_id, request_date, camp_id, urgency)`  
     PK: `request_id`, FK: `camp_id` $\rightarrow$ `relief_camp(camp_id)`.
  2. `request_line(request_id, line_no, item_id, qty_requested)`  
     PK: `(request_id, line_no)`, FK: `request_id` $\rightarrow$ `supply_request(request_id)` ON DELETE CASCADE, FK: `item_id` $\rightarrow$ `supply_item(item_id)`.
- **Result:** Both tables are in 3NF and BCNF.

---

### Case 4: `VolunteerCertFlat`
**Initial Schema:**  
`VolunteerCertFlat(volunteer_id, cert_no, volunteer_name, phone, cert_name, issued_by, expiry_date)`

#### 1. Functional Dependencies
- **Primary Key:** `(volunteer_id, cert_no)`
- **Dependencies:**
  1. $FD_1: \{\text{volunteer\_id}, \text{cert\_no}\} \rightarrow \{\text{cert\_name}, \text{issued\_by}, \text{expiry\_date}\}$ **[Full]**
  2. $FD_2: \text{volunteer\_id} \rightarrow \{\text{volunteer\_name}, \text{phone}\}$ **[Partial Dependency]**

#### 2. Anomalies & Decomposition
- **Anomalies:** Cannot store a volunteer with zero certifications without introducing NULLs into the primary key `cert_no`.
- **Decompose into:**
  1. `volunteer(volunteer_id, volunteer_name, phone)`  
     PK: `volunteer_id`. (In 3NF/BCNF).
  2. `volunteer_certification(volunteer_id, cert_no, cert_name, issued_by, expiry_date)`  
     PK: `(volunteer_id, cert_no)`. Identifying weak entity referencing `volunteer(volunteer_id)` ON DELETE CASCADE.

---

### Case 5: `FamilyMemberFlat`
**Initial Schema:**  
`FamilyMemberFlat(family_id, member_no, head_name, camp_id, origin_village, member_name, age, special_need)`

#### 1. Functional Dependencies
- **Primary Key:** `(family_id, member_no)`
- **Dependencies:**
  1. $FD_1: \{\text{family\_id}, \text{member\_no}\} \rightarrow \{\text{member\_name}, \text{age}, \text{special\_need}\}$ **[Full]**
  2. $FD_2: \text{family\_id} \rightarrow \{\text{head\_name}, \text{camp\_id}, \text{origin\_village}\}$ **[Partial Dependency]**

#### 2. Decomposition
- **2NF Violation:** `family_id` partially determines the household registration attributes.
- **Decompose into:**
  1. `registered_family(family_id, head_name, camp_id, origin_village, registered_on)`  
     PK: `family_id`.
  2. `family_member(family_id, member_no, member_name, age, special_need)`  
     PK: `(family_id, member_no)`. Weak entity cascading on `family_id`.

---

### Case 6: `VolunteerAssignmentFlat`
**Initial Schema:**  
`VolunteerAssignmentFlat(volunteer_id, camp_id, volunteer_name, camp_name, role, shift)`

#### 1. Functional Dependencies
- **Primary Key:** `(volunteer_id, camp_id)`
- **Dependencies:**
  1. $FD_1: \{\text{volunteer\_id}, \text{camp\_id}\} \rightarrow \{\text{role}, \text{shift}\}$ **[Full Dependency]**
  2. $FD_2: \text{volunteer\_id} \rightarrow \text{volunteer\_name}$ **[Partial Dependency]**
  3. $FD_3: \text{camp\_id} \rightarrow \text{camp\_name}$ **[Partial Dependency]**

#### 2. Decomposition
- **2NF Violations:** Both components of the composite primary key independently determine external descriptive names.
- **Decompose into:**
  1. `volunteer(volunteer_id, volunteer_name)`
  2. `relief_camp(camp_id, camp_name)`
  3. `assignment(volunteer_id, camp_id, role, shift)`  
     Associative table resolving M:N relationship with compound PK `(volunteer_id, camp_id)`.

---

## 3. Summary of Normalization Proofs

| Flat Entity | Primary Key | Normal Form Before | Violations | Resulting Normalized Relational Schemas |
|---|---|---|---|---|
| `ShelterUnitFlat` | `(camp_id, unit_no)` | 1NF | Partial ($FD_2$) | `relief_camp`, `shelter_unit` (BCNF) |
| `ShipmentLineFlat` | `(shipment_id, line_no)` | 1NF | Partial ($FD_2$), Transitive ($FD_3, FD_4$) | `donor`, `supply_item`, `shipment`, `shipment_line` (BCNF) |
| `RequestLineFlat` | `(request_id, line_no)` | 1NF | Partial ($FD_2$) | `supply_request`, `request_line` (BCNF) |
| `VolunteerCertFlat` | `(volunteer_id, cert_no)` | 1NF | Partial ($FD_2$) | `volunteer`, `volunteer_certification` (BCNF) |
| `FamilyMemberFlat` | `(family_id, member_no)` | 1NF | Partial ($FD_2$) | `registered_family`, `family_member` (BCNF) |
| `VolunteerAssignmentFlat` | `(volunteer_id, camp_id)` | 1NF | Partial ($FD_2, FD_3$) | `volunteer`, `relief_camp`, `assignment` (BCNF) |

**Conclusion:** All 15 database tables in the authoritative schema are in **Boyce-Codd Normal Form (BCNF)**, satisfying lossless joins and preserving all functional dependencies.
