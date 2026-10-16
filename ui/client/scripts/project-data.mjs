import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const clientRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);
const projectRoot = path.resolve(clientRoot, "../..");

export function parseCsv(text) {
  const rows = [];
  let row = [],
    value = "",
    quoted = false;
  for (let index = 0; index < text.length; index++) {
    const char = text[index];
    if (char === '"') {
      if (quoted && text[index + 1] === '"') {
        value += '"';
        index++;
      } else quoted = !quoted;
    } else if (char === "," && !quoted) {
      row.push(value);
      value = "";
    } else if (char === "\n" && !quoted) {
      row.push(value.replace(/\r$/, ""));
      if (row.some((cell) => cell !== "")) rows.push(row);
      row = [];
      value = "";
    } else value += char;
  }
  if (value || row.length) {
    row.push(value.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows;
}

export function readProjectData() {
  const read = (file) => fs.readFileSync(path.join(projectRoot, file), "utf8");
  const queries = fs
    .readdirSync(path.join(projectRoot, "db/queries"))
    .filter((file) => /^Q\d{2}\.sql$/.test(file))
    .sort()
    .map((file) => {
      const content = read(`db/queries/${file}`);
      const id = file.replace(".sql", "");
      const [fields, ...values] = parseCsv(read(`tests/expected/${id}.csv`));
      return {
        id,
        title: content.match(/-- Problem Statement:\s*(.+)/)?.[1] ?? id,
        concepts: content.match(/-- Concepts Tested:\s*(.+)/)?.[1] ?? "",
        sql: content
          .split("\n")
          .filter((line) => !line.trim().startsWith("--"))
          .join("\n")
          .trim(),
        expected: {
          fields,
          rows: values.map((row) =>
            Object.fromEntries(
              fields.map((field, index) => [field, row[index] ?? ""]),
            ),
          ),
        },
      };
    });
  return {
    schema: read("db/01_schema.sql"),
    seed: read("db/02_seed.sql"),
    capacityUpdateSql: read("db/demo/update_camp_capacity.sql"),
    erDiagram:
      read("docs/er-diagram.md")
        .match(/```mermaid([\s\S]*?)```/)?.[1]
        .trim() ?? "",
    queries,
  };
}

if (
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  const destination = path.join(clientRoot, "src/data/project.json");
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, JSON.stringify(readProjectData()));
  console.log(
    "Bundled schema, seed, and 20 SQL exercises from the project source.",
  );
}
