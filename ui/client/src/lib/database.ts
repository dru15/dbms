import { PGlite } from "@electric-sql/pglite";
import project from "../data/project.json";

export type Row = Record<string, unknown>;
export interface Result {
  fields: string[];
  rows: Row[];
  duration: number;
}
export interface Query {
  id: string;
  title: string;
  concepts: string;
  sql: string;
  expected: { fields: string[]; rows: Row[] };
}
export const queries: Query[] = project.queries;
export const erDiagram = project.erDiagram;
export const capacityUpdateSql = project.capacityUpdateSql;

export function getTableDefinition(name: string): string {
  // These are the original initialization statements, including named constraints.
  const start = project.schema.indexOf(`CREATE TABLE ${name} (`);
  const end = project.schema.indexOf("\n);", start);
  return start < 0 || end < 0 ? "" : project.schema.slice(start, end + 3);
}
let instance: Promise<PGlite> | undefined;

export function getDatabase() {
  if (!instance) {
    instance = (async () => {
      const db = await PGlite.create({ parsers: { 1082: (value) => value } });
      try {
        await db.exec(project.schema);
        await db.exec(project.seed);
        await db.exec("SET statement_timeout = '15s'");
        return db;
      } catch (error) {
        await db.close();
        throw error;
      }
    })().catch((error) => {
      instance = undefined;
      throw error;
    });
  }
  return instance;
}

export async function execute(sql: string): Promise<Result> {
  const db = await getDatabase();
  const started = performance.now();
  try {
    const results = await db.exec(sql);
    const last = results.at(-1);
    return {
      fields: last?.fields.map((field) => field.name) ?? [],
      rows: (last?.rows as Row[]) ?? [],
      duration: performance.now() - started,
    };
  } catch (error) {
    // A manually edited transaction may leave its session aborted.
    await db.exec("ROLLBACK").catch(() => undefined);
    throw error;
  }
}

export function displayValue(value: unknown): string {
  if (value === null || value === undefined) return "NULL";
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function matchesExpected(result: Result, query: Query): boolean {
  if (result.fields.join("|") !== query.expected.fields.join("|")) return false;
  const normalize = (value: unknown) => {
    if (value == null || value === "") return "";
    const text = displayValue(value);
    return /^-?\d+(\.\d+)?$/.test(text) ? Number(text).toFixed(2) : text;
  };
  const canonical = (rows: Row[]) =>
    rows
      .map((row) =>
        JSON.stringify(result.fields.map((field) => normalize(row[field]))),
      )
      .sort();
  return (
    JSON.stringify(canonical(result.rows)) ===
    JSON.stringify(canonical(query.expected.rows))
  );
}

export async function resetDatabase() {
  if (instance) await (await instance).close();
  instance = undefined;
  return getDatabase();
}

export async function explain(sql: string): Promise<Result> {
  const statement = sql
    .split(";")
    .map((part) => part.replace(/--[^\n]*/g, "").trim())
    .filter(Boolean)
    .at(-1);
  if (!statement || !/^(SELECT|WITH)\b/i.test(statement))
    throw new Error(
      "Execution plans are available for a final SELECT or WITH statement.",
    );
  return execute(`EXPLAIN (ANALYZE, BUFFERS) ${statement}`);
}
