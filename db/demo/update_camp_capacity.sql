-- DML demonstration: change the existing camp, without adding or deleting rows.
UPDATE relief_camp
SET capacity = 120
WHERE camp_id = 1
RETURNING camp_id, camp_name, capacity;
