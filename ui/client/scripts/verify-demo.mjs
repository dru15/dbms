import assert from "node:assert/strict";
import { PGlite } from "@electric-sql/pglite";
import { readProjectData } from "./project-data.mjs";

const data = readProjectData();
const db = await PGlite.create({ parsers: { 1082: (value) => value } });
try {
  await db.exec(data.schema);
  await db.exec(data.seed);
  const normalize = (value) => {
    if (value == null || value === "") return "";
    const text = String(value);
    return /^-?\d+(\.\d+)?$/.test(text) ? Number(text).toFixed(2) : text;
  };
  const canonical = (rows, fields) =>
    rows
      .map((row) =>
        JSON.stringify(fields.map((field) => normalize(row[field]))),
      )
      .sort();
  for (const query of data.queries) {
    const results = await db.exec(query.sql);
    const result = results.at(-1);
    assert.deepEqual(
      result.fields.map((field) => field.name),
      query.expected.fields,
      `${query.id} columns`,
    );
    assert.deepEqual(
      canonical(result.rows, query.expected.fields),
      canonical(query.expected.rows, query.expected.fields),
      `${query.id} results`,
    );
    console.log(`${query.id} PASS (${result.rows.length} rows)`);
  }
  // DDL exercises must remain usable when repeated during a review.
  for (const id of ["Q19", "Q20"])
    await db.exec(data.queries.find((query) => query.id === id).sql);
  // These are real database constraints, not interface simulations.
  await assert.rejects(
    db.exec("UPDATE camp_stock SET quantity_on_hand = -1 WHERE camp_id = 1"),
    (error) => error.code === "23514",
  );
  await assert.rejects(
    db.exec(
      "INSERT INTO shipment (shipment_date, status, donor_id, camp_id) VALUES ('2026-09-30', 'dispatched', 99999, 1)",
    ),
    (error) => error.code === "23503",
  );
  await assert.rejects(
    db.exec("INSERT INTO shelter_unit SELECT * FROM shelter_unit LIMIT 1"),
    (error) => error.code === "23505",
  );
  const explain = await db.query(
    `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ${data.queries[0].sql}`,
  );
  assert.ok(explain.rows[0]["QUERY PLAN"][0].Plan);
  console.log(
    "Repeatable views, CHECK/FK/PK constraints, and real execution plan PASS",
  );
  const before = await db.query("SELECT * FROM relief_camp ORDER BY camp_id");
  const original = before.rows.find((row) => row.camp_id === 1);
  assert.equal(original.capacity, 100);
  const updated = (await db.exec(data.capacityUpdateSql)).at(-1);
  assert.equal(updated.rows.length, 1);
  const after = await db.query("SELECT * FROM relief_camp ORDER BY camp_id");
  assert.equal(after.rows.find((row) => row.camp_id === 1).capacity, 120);
  assert.equal(
    after.rows.length,
    before.rows.length,
    "UPDATE must not add rows",
  );
  assert.deepEqual(
    after.rows.filter((row) => row.camp_id !== 1),
    before.rows.filter((row) => row.camp_id !== 1),
    "Other camps must stay unchanged",
  );
  await db.query("UPDATE relief_camp SET capacity = $1 WHERE camp_id = 1", [
    original.capacity,
  ]);
  assert.deepEqual(
    (await db.query("SELECT * FROM relief_camp ORDER BY camp_id")).rows,
    before.rows,
  );
  console.log(
    "UPDATE demo: 100 → 120, independent table read, other camps unchanged, restore PASS",
  );
} finally {
  await db.close();
}
