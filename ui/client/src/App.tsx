import { useEffect, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowDownToLine,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Circle,
  Code2,
  PencilLine,
  Copy,
  Database,
  Expand,
  FileCode2,
  GitBranch,
  Layers3,
  LayoutDashboard,
  Loader2,
  Play,
  Presentation,
  RotateCcw,
  Search,
  ShieldCheck,
  Table2,
  Terminal,
  X,
} from "lucide-react";
import {
  displayValue,
  capacityUpdateSql,
  erDiagram,
  execute,
  explain,
  getDatabase,
  getTableDefinition,
  matchesExpected,
  queries,
  resetDatabase,
} from "./lib/database";
import type { Result, Row } from "./lib/database";
import ProjectOverview from "./ProjectOverview";
import {
  integrityExamples,
  queryNotes,
  relations,
  reviewSteps,
} from "./data/review";

type Page = "overview" | "queries" | "schema" | "integrity" | "update";
type Status = "pass" | "fail";
const groups = [
  "All queries",
  "Joins & aggregation",
  "Subqueries & sets",
  "Window functions",
  "Views & materialization",
];
const errorMessage = (error: unknown) =>
  error instanceof Error ? error.message : String(error);

function SqlCode({ sql }: { sql: string }) {
  const tokens = sql.split(
    /(--[^\n]*|'(?:''|[^'])*'|\b\d+(?:\.\d+)?\b|\b(?:SELECT|FROM|JOIN|INNER|LEFT|FULL|OUTER|ON|USING|WHERE|AND|OR|NOT|EXISTS|GROUP|BY|HAVING|ORDER|ASC|DESC|AS|WITH|OVER|PARTITION|ROWS|BETWEEN|UNBOUNDED|PRECEDING|CURRENT|ROW|CASE|WHEN|THEN|ELSE|END|DISTINCT|CREATE|REPLACE|VIEW|MATERIALIZED|UNIQUE|INDEX|IF|REFRESH|CONCURRENTLY|EXCEPT|UNION|ALL|DATE|FILTER|LIMIT|UPDATE|SET|INSERT|INTO|VALUES|COUNT|SUM|AVG|MIN|MAX|ROUND|COALESCE|DENSE_RANK|LAG|DATE_TRUNC)\b)/gi,
  );
  return (
    <pre className="sql-code">
      <code>
        {tokens.map((token, index) => (
          <span
            key={index}
            className={
              token.startsWith("--")
                ? "sql-comment"
                : token.startsWith("'")
                  ? "sql-string"
                  : /^\d/.test(token)
                    ? "sql-number"
                    : /^[A-Z_]+$/i.test(token)
                      ? "sql-keyword"
                      : undefined
            }
          >
            {token}
          </span>
        ))}
      </code>
    </pre>
  );
}

function ResultsTable({
  result,
  filename = "reliefdb-query-results",
}: {
  result: Result;
  filename?: string;
}) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(8);
  const [sort, setSort] = useState<{ field: string; direction: number } | null>(
    null,
  );
  useEffect(() => {
    setSearch("");
    setPage(0);
    setSort(null);
  }, [result]);
  const rows = result.rows.filter((row) =>
    result.fields.some((field) =>
      displayValue(row[field]).toLowerCase().includes(search.toLowerCase()),
    ),
  );
  if (sort)
    rows.sort(
      (a, b) =>
        displayValue(a[sort.field]).localeCompare(
          displayValue(b[sort.field]),
          undefined,
          { numeric: true },
        ) * sort.direction,
    );
  const pages = Math.max(1, Math.ceil(rows.length / pageSize));
  const currentPage = Math.min(page, pages - 1);
  function download() {
    const escape = (value: unknown) =>
      `"${(value == null ? "" : displayValue(value)).replace(/"/g, '""')}"`;
    const csv = [
      result.fields.map(escape).join(","),
      ...rows.map((row) =>
        result.fields.map((field) => escape(row[field])).join(","),
      ),
    ].join("\r\n");
    const url = URL.createObjectURL(
      new Blob([csv], { type: "text/csv;charset=utf-8" }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `${filename}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }
  return (
    <>
      <div className="result-tools">
        <label className="search-field compact">
          <Search size={14} />
          <input
            aria-label="Search result rows"
            placeholder="Filter results…"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(0);
            }}
          />
        </label>
        <button className="text-button" onClick={download}>
          <ArrowDownToLine size={14} /> Export CSV
        </button>
      </div>
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th className="row-number">#</th>
              {result.fields.map((field) => (
                <th
                  key={field}
                  aria-sort={
                    sort?.field === field
                      ? sort.direction === 1
                        ? "ascending"
                        : "descending"
                      : "none"
                  }
                >
                  <button
                    onClick={() => {
                      setSort({
                        field,
                        direction: sort?.field === field ? -sort.direction : 1,
                      });
                      setPage(0);
                    }}
                  >
                    {field.replace(/_/g, " ")}
                    <ArrowDown
                      size={12}
                      className={
                        sort?.field === field
                          ? `sort-active ${sort.direction === 1 ? "sort-ascending" : ""}`
                          : "sort-idle"
                      }
                    />
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows
              .slice(currentPage * pageSize, currentPage * pageSize + pageSize)
              .map((row, index) => (
                <tr key={index}>
                  <td className="row-number">
                    {currentPage * pageSize + index + 1}
                  </td>
                  {result.fields.map((field) => (
                    <td
                      key={field}
                      className={row[field] == null ? "null-value" : undefined}
                    >
                      {displayValue(row[field])}
                    </td>
                  ))}
                </tr>
              ))}
          </tbody>
        </table>
      </div>
      {rows.length === 0 && (
        <div className="empty-inline">
          {result.rows.length
            ? "No rows match your filter."
            : "The query completed successfully with no matching rows."}
        </div>
      )}
      <div className="table-footer">
        <span>
          {rows.length
            ? `${currentPage * pageSize + 1}–${Math.min(currentPage * pageSize + pageSize, rows.length)}`
            : "0"}{" "}
          of {rows.length} rows
        </span>
        <div>
          <label className="page-size">
            Rows per page
            <select
              aria-label="Rows per page"
              value={pageSize}
              onChange={(event) => {
                setPageSize(Number(event.target.value));
                setPage(0);
              }}
            >
              {[8, 25, 50].map((size) => (
                <option key={size}>{size}</option>
              ))}
            </select>
          </label>
          <button
            className="icon-button"
            aria-label="Previous results page"
            disabled={currentPage === 0}
            onClick={() => setPage(currentPage - 1)}
          >
            <ChevronLeft size={16} />
          </button>
          <span>
            {currentPage + 1} / {pages}
          </span>
          <button
            className="icon-button"
            aria-label="Next results page"
            disabled={currentPage + 1 >= pages}
            onClick={() => setPage(currentPage + 1)}
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </>
  );
}

function SchemaExplorer({
  ready,
  counts,
  initialRelation,
  initialDetail = "columns",
}: {
  ready: boolean;
  counts: Record<string, number>;
  initialRelation: string;
  initialDetail?: "columns" | "data" | "ddl";
}) {
  const [selected, setSelected] = useState(initialRelation);
  const [columns, setColumns] = useState<Row[]>([]);
  const [sample, setSample] = useState<Result | null>(null);
  const [constraints, setConstraints] = useState<Row[]>([]);
  const [detail, setDetail] = useState<"columns" | "data" | "ddl">(
    initialDetail,
  );
  const [relationSearch, setRelationSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<"relations" | "diagram">("relations");
  const [zoom, setZoom] = useState(1);
  const [error, setError] = useState("");
  const [diagramSvg, setDiagramSvg] = useState("");
  const relation = relations.find((item) => item.name === selected)!;
  useEffect(() => {
    setSelected(initialRelation);
    setDetail(initialDetail);
  }, [initialRelation, initialDetail]);
  useEffect(() => {
    let cancelled = false;
    setError("");
    setColumns([]);
    setSample(null);
    setConstraints([]);
    if (ready && view === "relations") {
      setLoading(true);
      getDatabase()
        .then(async (db) => {
          const metadata = await db.query(
            `SELECT c.column_name, c.data_type, c.is_nullable,
        EXISTS (SELECT 1 FROM information_schema.key_column_usage k
          JOIN information_schema.table_constraints t USING (constraint_name, table_schema, table_name)
          WHERE k.table_schema = c.table_schema AND k.table_name = c.table_name AND k.column_name = c.column_name AND t.constraint_type = 'PRIMARY KEY') AS primary_key,
        EXISTS (SELECT 1 FROM information_schema.key_column_usage k
          JOIN information_schema.table_constraints t USING (constraint_name, table_schema, table_name)
          WHERE k.table_schema = c.table_schema AND k.table_name = c.table_name AND k.column_name = c.column_name AND t.constraint_type = 'FOREIGN KEY') AS foreign_key
        FROM information_schema.columns c WHERE c.table_schema = 'public' AND c.table_name = $1 ORDER BY c.ordinal_position`,
            [selected],
          );
          const keys = (metadata.rows as Row[])
            .filter((column) => column.primary_key === true)
            .map((column) => `"${column.column_name}"`);
          const rows = await execute(
            `SELECT * FROM "${selected}"${keys.length ? ` ORDER BY ${keys.join(", ")}` : ""};`,
          );
          const definitions = await db.query(
            `
            SELECT c.conname AS name, c.contype AS kind,
                   pg_get_constraintdef(c.oid, true) AS definition,
                   ref.relname AS referenced_table
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            LEFT JOIN pg_class ref ON ref.oid = c.confrelid
            WHERE n.nspname = 'public' AND t.relname = $1 AND c.contype IN ('p', 'f', 'c', 'u')
            ORDER BY c.contype, c.conname
          `,
            [selected],
          );
          if (!cancelled) {
            setColumns(metadata.rows as Row[]);
            setSample(rows);
            setConstraints(definitions.rows as Row[]);
          }
        })
        .catch((error) => {
          if (!cancelled) setError(errorMessage(error));
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }
    return () => {
      cancelled = true;
    };
  }, [ready, selected, view]);
  useEffect(() => {
    let cancelled = false;
    if (view === "diagram") {
      setDiagramSvg("");
      import("mermaid")
        .then(async ({ default: mermaid }) => {
          mermaid.initialize({
            startOnLoad: false,
            theme: "base",
            themeVariables: {
              primaryColor: "#f1f6f2",
              primaryTextColor: "#203b32",
              primaryBorderColor: "#a6b7aa",
              lineColor: "#728879",
              fontFamily: "Inter, sans-serif",
            },
          });
          const rendered = await mermaid.render(
            `relief-diagram-${Date.now()}`,
            erDiagram,
          );
          if (!cancelled) setDiagramSvg(rendered.svg);
        })
        .catch((error) => {
          if (!cancelled) setError(errorMessage(error));
        });
    }
    return () => {
      cancelled = true;
    };
  }, [view]);
  return (
    <section className="section-page">
      <div className="section-heading">
        <div>
          <p className="eyebrow">THE RELATIONAL FOUNDATION</p>
          <h1>Every relation has a reason.</h1>
          <p>
            Inspect all 15 tables: columns, complete data, relationships, and
            SQL definitions.
          </p>
        </div>
        <div className="segmented">
          <button
            className={view === "relations" ? "active" : ""}
            onClick={() => setView("relations")}
          >
            <Table2 size={15} /> Relations
          </button>
          <button
            className={view === "diagram" ? "active" : ""}
            onClick={() => setView("diagram")}
          >
            <GitBranch size={15} /> ER diagram
          </button>
        </div>
      </div>
      <div className="schema-principles">
        <span>
          <span className="key-badge">PK</span> Primary key: unique row identity
        </span>
        <span>
          <span className="key-badge fk">FK</span> Foreign key: referential
          integrity
        </span>
        <span>
          <Layers3 size={15} /> 5 weak entities · composite keys
        </span>
      </div>
      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}
      {view === "diagram" ? (
        <div>
          <div className="diagram-toolbar">
            <span>Scroll to explore · zoom in for attributes</span>
            <div>
              <button
                className="icon-button"
                aria-label="Zoom out of ER diagram"
                disabled={zoom <= 1}
                onClick={() => setZoom(Math.max(1, zoom - 0.5))}
              >
                −
              </button>
              <span>{zoom * 100}%</span>
              <button
                className="icon-button"
                aria-label="Zoom into ER diagram"
                disabled={zoom >= 3}
                onClick={() => setZoom(Math.min(3, zoom + 0.5))}
              >
                +
              </button>
              <button className="text-button" onClick={() => setZoom(1)}>
                Fit diagram
              </button>
            </div>
          </div>
          <div className="diagram-surface">
            <div className="diagram-scale" style={{ width: `${zoom * 100}%` }}>
              {diagramSvg ? (
                <div dangerouslySetInnerHTML={{ __html: diagramSvg }} />
              ) : (
                <>
                  <Loader2 className="spin" size={20} /> Rendering relational
                  diagram…
                </>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="schema-layout">
          <div className="relation-list">
            <label className="search-field relation-search">
              <Search size={14} />
              <input
                aria-label="Find a database table"
                placeholder="Find a table…"
                value={relationSearch}
                onChange={(event) => setRelationSearch(event.target.value)}
              />
            </label>
            <span className="relation-list-label">
              15 TABLES · PUBLIC SCHEMA
            </span>
            <div className="relation-buttons">
              {relations
                .filter(
                  (item) =>
                    item.name.includes(relationSearch.toLowerCase()) ||
                    item.kind
                      .toLowerCase()
                      .includes(relationSearch.toLowerCase()),
                )
                .map((item) => (
                  <button
                    className={selected === item.name ? "selected" : ""}
                    aria-pressed={selected === item.name}
                    key={item.name}
                    onClick={() => setSelected(item.name)}
                  >
                    <Table2 size={15} />
                    <span>
                      <strong>{item.name}</strong>
                      <small>{item.kind} entity</small>
                    </span>
                    <span className="relation-count">
                      {counts[item.name] ?? "—"}
                    </span>
                  </button>
                ))}
              {!relations.some(
                (item) =>
                  item.name.includes(relationSearch.toLowerCase()) ||
                  item.kind
                    .toLowerCase()
                    .includes(relationSearch.toLowerCase()),
              ) && <p className="empty-inline">No matching tables.</p>}
            </div>
          </div>
          <div className="relation-detail">
            <div className="panel">
              <div className="panel-heading">
                <div>
                  <span className="pill neutral">{relation.kind} entity</span>
                  <h2>{relation.name}</h2>
                </div>
                <span className="mono muted">
                  {sample?.rows.length ?? counts[selected] ?? "—"} rows
                </span>
              </div>
              <p className="relation-description">{relation.description}</p>
              <div className="key-explanation">
                <span className="key-badge">PK</span>
                <code>{relation.key}</code>
                <p>{relation.topic}</p>
              </div>
              <div
                className="relation-tabs"
                role="tablist"
                aria-label="Table details"
              >
                {[
                  { id: "columns", label: "Columns & keys" },
                  { id: "data", label: "Browse data" },
                  { id: "ddl", label: "CREATE TABLE" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    id={`relation-tab-${tab.id}`}
                    role="tab"
                    tabIndex={detail === tab.id ? 0 : -1}
                    aria-selected={detail === tab.id}
                    aria-controls="relation-detail-content"
                    className={detail === tab.id ? "active" : ""}
                    onClick={() => setDetail(tab.id as typeof detail)}
                    onKeyDown={(event) => {
                      const tabs = ["columns", "data", "ddl"] as const;
                      const index = tabs.indexOf(detail);
                      const next =
                        event.key === "ArrowRight"
                          ? tabs[(index + 1) % 3]
                          : event.key === "ArrowLeft"
                            ? tabs[(index + 2) % 3]
                            : event.key === "Home"
                              ? tabs[0]
                              : event.key === "End"
                                ? tabs[2]
                                : null;
                      if (next) {
                        event.preventDefault();
                        setDetail(next);
                        document
                          .getElementById(`relation-tab-${next}`)
                          ?.focus();
                      }
                    }}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
              <div
                id="relation-detail-content"
                role="tabpanel"
                aria-labelledby={`relation-tab-${detail}`}
              >
                {detail === "ddl" ? (
                  <div className="relation-ddl">
                    <p className="definition-source">
                      Original definition from <code>db/01_schema.sql</code> ·
                      includes named constraints
                    </p>
                    <SqlCode sql={getTableDefinition(selected)} />
                  </div>
                ) : detail === "data" ? (
                  <>
                    <div className="browse-query">
                      <span>
                        <Code2 size={14} /> Executed SQL
                      </span>
                      <code>
                        SELECT * FROM {selected}
                        {columns.some((column) => column.primary_key === true)
                          ? ` ORDER BY ${columns
                              .filter((column) => column.primary_key === true)
                              .map((column) => String(column.column_name))
                              .join(", ")}`
                          : ""}
                        ;
                      </code>
                    </div>
                    {loading ? (
                      <div className="empty-inline">
                        <Loader2 className="spin" size={17} /> Loading table
                        data…
                      </div>
                    ) : (
                      sample && (
                        <ResultsTable
                          result={sample}
                          filename={`reliefdb-${selected}`}
                        />
                      )
                    )}
                    {sample?.rows.length === 0 &&
                      selected === "request_audit" && (
                        <p className="audit-empty-note">
                          The audit table is defined and currently empty.
                          Automatic audit logging is a separate trigger
                          exercise.
                        </p>
                      )}
                  </>
                ) : (
                  <>
                    <div className="table-scroll">
                      <table className="data-table schema-columns">
                        <thead>
                          <tr>
                            <th>Attribute</th>
                            <th>Data type</th>
                            <th>Constraints</th>
                          </tr>
                        </thead>
                        <tbody>
                          {columns.map((column) => (
                            <tr key={String(column.column_name)}>
                              <td>
                                <code>{String(column.column_name)}</code>
                              </td>
                              <td>{String(column.data_type)}</td>
                              <td>
                                {column.primary_key === true && (
                                  <span className="key-badge">PK</span>
                                )}
                                {column.foreign_key === true && (
                                  <span className="key-badge fk">FK</span>
                                )}
                                {column.is_nullable === "NO" && (
                                  <span className="constraint-label">
                                    NOT NULL
                                  </span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {loading && (
                      <div className="empty-inline">
                        <Loader2 className="spin" size={16} /> Reading database
                        metadata…
                      </div>
                    )}
                    <div className="relation-constraints">
                      <h3>Named constraints & relationships</h3>
                      <p>Read directly from PostgreSQL's system catalog.</p>
                      {constraints.map((constraint) => (
                        <div
                          className="constraint-definition"
                          key={String(constraint.name)}
                        >
                          <span className="constraint-name">
                            {String(constraint.name)}
                          </span>
                          <code>{String(constraint.definition)}</code>
                          {typeof constraint.referenced_table === "string" && (
                            <button
                              className="text-button"
                              onClick={() => {
                                setSelected(
                                  String(constraint.referenced_table),
                                );
                                setDetail("columns");
                              }}
                            >
                              <Table2 size={13} /> Open{" "}
                              {String(constraint.referenced_table)}{" "}
                              <ArrowRight size={13} />
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
              {!ready && (
                <div className="empty-inline">
                  Database is initializing. Schema details will appear when
                  ready.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

function IntegrityLab({
  ready,
  onBusy,
}: {
  ready: boolean;
  onBusy: (value: boolean) => void;
}) {
  const [selected, setSelected] = useState(0);
  const [busy, setBusy] = useState(false);
  const [outcome, setOutcome] = useState<{
    expected: boolean;
    message: string;
    code: string;
  } | null>(null);
  const example = integrityExamples[selected];
  async function test() {
    setBusy(true);
    onBusy(true);
    setOutcome(null);
    let db: Awaited<ReturnType<typeof getDatabase>> | undefined;
    try {
      db = await getDatabase();
      // Always roll back, including an unexpectedly accepted statement.
      await db.exec("BEGIN");
      await db.exec(example.sql);
      setOutcome({
        expected: false,
        message:
          "The database accepted this statement. The expected constraint was not enforced.",
        code: "ACCEPTED",
      });
    } catch (error) {
      const code = (error as { code?: string }).code ?? "UNKNOWN";
      setOutcome({
        expected: code === example.code,
        message: errorMessage(error),
        code,
      });
    } finally {
      if (db) await db.exec("ROLLBACK").catch(() => undefined);
      setBusy(false);
      onBusy(false);
    }
  }
  return (
    <section className="section-page">
      <div className="section-heading">
        <div>
          <p className="eyebrow">LET THE DATABASE SAY NO</p>
          <h1>Integrity, enforced.</h1>
          <p>
            Submit an invalid statement and observe a real PostgreSQL constraint
            rejection.
          </p>
        </div>
        <ShieldCheck className="heading-icon" size={44} strokeWidth={1.3} />
      </div>
      <div className="integrity-layout">
        <div className="integrity-options">
          {integrityExamples.map((item, index) => (
            <button
              key={item.code}
              className={index === selected ? "selected" : ""}
              disabled={busy}
              onClick={() => {
                setSelected(index);
                setOutcome(null);
              }}
            >
              <span className="eyebrow">{item.constraint}</span>
              <strong>{item.title}</strong>
              <ArrowUpRight size={18} />
            </button>
          ))}
          <p className="muted">
            Each attempt is wrapped in a transaction and rolled back. Your seed
            data stays intact.
          </p>
        </div>
        <div>
          <div className="panel sql-panel">
            <div className="panel-heading">
              <span>
                <Terminal size={16} /> Invalid statement
              </span>
              <span className="pill neutral">{example.constraint}</span>
            </div>
            <SqlCode sql={example.sql} />
            <div className="editor-footer">
              <span>{example.explanation}</span>
              <button
                className="primary-button"
                onClick={test}
                disabled={!ready || busy}
              >
                {busy ? (
                  <Loader2 size={15} className="spin" />
                ) : (
                  <Play size={15} />
                )}{" "}
                Test constraint
              </button>
            </div>
          </div>
          {outcome && (
            <div
              className={`constraint-outcome ${outcome.expected ? "correct" : "incorrect"}`}
              role="status"
            >
              <ShieldCheck size={23} />
              <div>
                <strong>
                  {outcome.expected
                    ? "Rejected as expected"
                    : "Unexpected outcome"}
                </strong>
                <p>{outcome.message}</p>
                <code>SQLSTATE {outcome.code}</code>
              </div>
            </div>
          )}
          <div className="concept-note">
            <h3>The review takeaway</h3>
            <p>
              Validation in a form improves usability. Constraints in the
              database protect every write, including scripts and APIs. A
              primary key, foreign key, and CHECK each protect a different
              invariant.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function UpdateDemo({
  ready,
  original,
  onOriginal,
  onBusy,
  onChanged,
  onBrowse,
}: {
  ready: boolean;
  original: Row | null;
  onOriginal: (row: Row) => void;
  onBusy: (value: boolean) => void;
  onChanged: () => Promise<void>;
  onBrowse: () => void;
}) {
  const [current, setCurrent] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const readSql =
    "SELECT camp_id, camp_name, capacity\nFROM relief_camp\nWHERE camp_id = 1;";
  async function read() {
    const result = await execute(readSql);
    if (result.rows.length !== 1)
      throw new Error(
        "Camp 1 is missing. Reset the seed database to prepare this demonstration.",
      );
    return result;
  }
  useEffect(() => {
    let cancelled = false;
    setCurrent(null);
    setError("");
    setMessage("");
    if (ready)
      read()
        .then((result) => {
          if (!cancelled) {
            setCurrent(result);
            if (!original) onOriginal(result.rows[0]);
          }
        })
        .catch((error) => {
          if (!cancelled) setError(errorMessage(error));
        });
    return () => {
      cancelled = true;
    };
  }, [ready]);

  async function change(restore = false) {
    setBusy(true);
    onBusy(true);
    setError("");
    setMessage("");
    try {
      if (restore && original) {
        const db = await getDatabase();
        await db.query(
          "UPDATE relief_camp SET capacity = $1 WHERE camp_id = 1",
          [original.capacity],
        );
      } else {
        const updated = await execute(capacityUpdateSql);
        if (updated.rows.length !== 1)
          throw new Error(
            "No row was updated. Reset the seed database and try again.",
          );
      }
      // Read the table separately to prove that UPDATE changed the stored row.
      setCurrent(await read());
      await onChanged();
      setMessage(
        restore
          ? "Original capacity restored. The table read below confirms the value."
          : "One stored row updated. A separate SELECT below confirms capacity 120.",
      );
    } catch (error) {
      setError(errorMessage(error));
    } finally {
      setBusy(false);
      onBusy(false);
    }
  }
  const row = current?.rows[0];
  const changed = original && row && original.capacity !== row.capacity;
  return (
    <section className="section-page update-demo">
      <div className="section-heading">
        <div>
          <p className="eyebrow">DATA MANIPULATION · ONE UPDATE</p>
          <h1>Change a camp's capacity.</h1>
          <p>
            Read the original value, update the stored row, then inspect it in
            the database.
          </p>
        </div>
        <PencilLine className="heading-icon" size={40} strokeWidth={1.3} />
      </div>
      <div className="update-comparison">
        <div>
          <span>Before this demo</span>
          <strong>
            {original ? displayValue(original.capacity) : "—"}
            <small> people</small>
          </strong>
          <p>
            {original ? displayValue(original.camp_name) : "Reading camp 1…"}
          </p>
        </div>
        <ArrowRight size={22} />
        <div className={changed ? "is-changed" : ""}>
          <span>Current database value</span>
          <strong>
            {row ? displayValue(row.capacity) : "—"}
            <small> people</small>
          </strong>
          <p>
            {changed
              ? "Stored value changed · camp_id = 1"
              : "Camp 1 · read from relief_camp"}
          </p>
        </div>
      </div>
      <div className="panel sql-panel">
        <div className="panel-heading">
          <span className="file-label">
            <FileCode2 size={16} /> update_camp_capacity.sql
          </span>
          <span className="pill neutral">UPDATE · WHERE · RETURNING</span>
        </div>
        <SqlCode sql={capacityUpdateSql} />
        <div className="editor-footer">
          <span>
            WHERE targets one existing camp. RETURNING reports the updated row.
          </span>
          <div>
            <button
              className="text-button"
              disabled={!ready || busy || !changed}
              onClick={() => change(true)}
            >
              <RotateCcw size={14} /> Restore original value
            </button>
            <button
              className="primary-button"
              disabled={!ready || busy || !row || row.capacity === 120}
              onClick={() => change()}
            >
              {busy ? (
                <Loader2 className="spin" size={15} />
              ) : (
                <Play size={15} />
              )}{" "}
              Apply UPDATE
            </button>
          </div>
        </div>
      </div>
      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}
      {message && (
        <div className="update-feedback" role="status">
          <CheckCircle2 size={17} />
          {message}
        </div>
      )}
      <div className="panel update-readback">
        <div className="panel-heading">
          <h2>Read back from the database</h2>
          <button
            className="text-button"
            onClick={onBrowse}
            disabled={!ready || busy}
          >
            <Table2 size={14} /> Open relief_camp table <ArrowRight size={14} />
          </button>
        </div>
        <div className="browse-query">
          <span>
            <Code2 size={14} /> Independent SELECT after the write
          </span>
          <code>{readSql}</code>
        </div>
        {current && (
          <ResultsTable result={current} filename="reliefdb-updated-camp" />
        )}
      </div>
      <div className="concept-note">
        <h3>What to say during the review</h3>
        <p>
          “SELECT reads data. This UPDATE changes the capacity stored in
          relief_camp from 100 to 120. WHERE camp_id = 1 limits the change to
          one camp. I can now open that table and see 120 in its capacity
          column. The number of rows stays the same because we updated a row
          rather than inserted one.”
        </p>
        <p>
          Changes affect later queries, including occupancy calculations.
          Restore the original value before verifying seed answers. This write
          lasts for the browser session; a reload or seed reset restores the
          original data.
        </p>
      </div>
    </section>
  );
}

export default function App() {
  const [page, setPage] = useState<Page>("overview");
  const [presenting, setPresenting] = useState(false);
  const [schemaRelation, setSchemaRelation] = useState("relief_camp");
  const [schemaDetail, setSchemaDetail] = useState<"columns" | "data" | "ddl">(
    "columns",
  );
  const [updateOriginal, setUpdateOriginal] = useState<Row | null>(null);
  const [selectedId, setSelectedId] = useState("Q01");
  const [search, setSearch] = useState("");
  const [group, setGroup] = useState("All queries");
  const [sql, setSql] = useState(queries[0].sql);
  const [editing, setEditing] = useState(false);
  const [ready, setReady] = useState(false);
  const [dbError, setDbError] = useState("");
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [result, setResult] = useState<Result | null>(null);
  const [plan, setPlan] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [statuses, setStatuses] = useState<Record<string, Status>>({});
  const [resultTab, setResultTab] = useState<"results" | "plan">("results");
  const [review, setReview] = useState<number | null>(null);
  const [answerVisible, setAnswerVisible] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const [notification, setNotification] = useState("");
  const request = useRef(0);
  const focusDialog = useRef<HTMLDivElement>(null);
  const selectedQuery = queries.find((query) => query.id === selectedId)!;
  const notes = queryNotes[selectedId];
  const passed = Object.values(statuses).filter(
    (status) => status === "pass",
  ).length;
  const busy = running || verifying;
  const filteredQueries = queries.filter(
    (query) =>
      (group === "All queries" || queryNotes[query.id].group === group) &&
      `${query.id} ${query.title} ${query.concepts} ${queryNotes[query.id].title}`
        .toLowerCase()
        .includes(search.toLowerCase()),
  );

  async function initialize() {
    const db = await getDatabase();
    const totals = await db.query<{ name: string; count: number }>(
      relations
        .map(
          (relation) =>
            `SELECT '${relation.name}' AS name, COUNT(*)::int AS count FROM "${relation.name}"`,
        )
        .join(" UNION ALL "),
    );
    setCounts(
      Object.fromEntries(totals.rows.map((row) => [row.name, row.count])),
    );
    setReady(true);
    setDbError("");
  }
  useEffect(() => {
    let cancelled = false;
    initialize()
      .then(async () => {
        const first = await execute(queries[0].sql);
        if (!cancelled && request.current === 0) {
          setResult(first);
          setStatuses({
            Q01: matchesExpected(first, queries[0]) ? "pass" : "fail",
          });
        }
      })
      .catch((error) => {
        if (!cancelled) setDbError(errorMessage(error));
      });
    return () => {
      cancelled = true;
    };
  }, []);
  useEffect(() => {
    if (notification) {
      const timeout = setTimeout(() => setNotification(""), 4500);
      return () => clearTimeout(timeout);
    }
  }, [notification]);
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [page, review]);
  useEffect(() => {
    if (!expanded) return;
    const previousFocus = document.activeElement as HTMLElement | null;
    const dialog = focusDialog.current;
    dialog?.querySelector<HTMLButtonElement>("button")?.focus();
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") setExpanded(false);
      if (event.key === "Tab" && dialog) {
        const targets = Array.from(
          dialog.querySelectorAll<HTMLElement>(
            "button:not(:disabled), textarea, input",
          ),
        );
        const first = targets[0],
          last = targets.at(-1);
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }
    };
    window.addEventListener("keydown", close);
    return () => {
      window.removeEventListener("keydown", close);
      previousFocus?.focus();
    };
  }, [expanded]);

  function selectQuery(id: string) {
    request.current++;
    setSelectedId(id);
    setSql(queries.find((query) => query.id === id)!.sql);
    setResult(null);
    setPlan(null);
    setError("");
    setEditing(false);
    setResultTab("results");
  }
  async function runQuery(showPlan = false) {
    const token = ++request.current;
    setRunning(true);
    setError("");
    try {
      if (showPlan) {
        // Install view definitions first when the exercise has multiple statements.
        if (selectedId === "Q19" || selectedId === "Q20") await execute(sql);
        const nextPlan = await explain(sql);
        if (token === request.current) {
          setPlan(nextPlan);
          setResultTab("plan");
        }
      } else {
        const nextResult = await execute(sql);
        await initialize();
        if (token === request.current) {
          setResult(nextResult);
          setPlan(null);
          setResultTab("results");
          if (sql === selectedQuery.sql)
            setStatuses((previous) => ({
              ...previous,
              [selectedId]: matchesExpected(nextResult, selectedQuery)
                ? "pass"
                : "fail",
            }));
          else setStatuses({});
        }
      }
    } catch (error) {
      if (token === request.current) {
        setError(errorMessage(error));
        if (showPlan) setPlan(null);
        else setResult(null);
      }
    } finally {
      setRunning(false);
    }
  }
  async function verifyAll() {
    setVerifying(true);
    setNotification("");
    const next: Record<string, Status> = {};
    for (const query of queries) {
      try {
        next[query.id] = matchesExpected(await execute(query.sql), query)
          ? "pass"
          : "fail";
      } catch {
        next[query.id] = "fail";
      }
      setStatuses({ ...next });
    }
    setVerifying(false);
    setNotification(
      `${Object.values(next).filter((status) => status === "pass").length}/20 queries match the seed reference outputs.`,
    );
  }
  async function reset() {
    setUpdateOriginal(null);
    setReady(false);
    setDbError("");
    setError("");
    setResult(null);
    setPlan(null);
    setStatuses({});
    request.current++;
    try {
      await resetDatabase();
      await initialize();
      setNotification(
        "The browser database has been reset to the original seed data.",
      );
    } catch (error) {
      setDbError(errorMessage(error));
    }
  }
  function reviewAt(index: number) {
    setReview(index);
    setAnswerVisible(false);
    const step = reviewSteps[index];
    setPage(step.page as Page);
    if (step.page === "schema") {
      setSchemaRelation("shipment_line");
      setSchemaDetail("columns");
    }
    selectQuery(step.query);
    setGroup("All queries");
    setSearch("");
  }
  async function copySql() {
    try {
      await navigator.clipboard.writeText(sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setNotification(
        "Clipboard unavailable. Select the SQL text and copy it manually.",
      );
    }
  }

  function browseTable(table: string) {
    setSchemaDetail("columns");
    setReview(null);
    setSchemaRelation(table);
    setPage("schema");
  }

  function navigate(next: Page) {
    setReview(null);
    setPage(next);
  }

  const editor = (
    <div className="panel sql-panel">
      <div className="panel-heading">
        <div className="file-label">
          <FileCode2 size={16} />
          <span>{selectedId}.sql</span>
          <span className="pill neutral">PostgreSQL</span>
        </div>
        <div className="editor-actions">
          <button
            className={editing ? "text-button active" : "text-button"}
            onClick={() => setEditing(!editing)}
          >
            <Code2 size={14} />
            {editing ? "View SQL" : "Edit SQL"}
          </button>
          <button
            className="icon-button"
            aria-label="Copy SQL"
            onClick={copySql}
          >
            {copied ? <Check size={15} /> : <Copy size={15} />}
          </button>
          <button
            className="icon-button"
            aria-label={
              expanded ? "Exit focused SQL view" : "Expand SQL editor"
            }
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <X size={15} /> : <Expand size={15} />}
          </button>
        </div>
      </div>
      <div className="editor-body">
        <div className="line-numbers" aria-hidden="true">
          {sql.split("\n").map((_, index) => (
            <span key={index}>{index + 1}</span>
          ))}
        </div>
        {editing ? (
          <textarea
            className="sql-input"
            aria-label="SQL editor"
            spellCheck={false}
            value={sql}
            onChange={(event) => {
              request.current++;
              setSql(event.target.value);
              setResult(null);
              setPlan(null);
              setError("");
            }}
            onKeyDown={(event) => {
              if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                event.preventDefault();
                if (ready && !busy) void runQuery();
              }
            }}
          />
        ) : (
          <SqlCode sql={sql} />
        )}
      </div>
      <div className="editor-footer">
        <span>
          <span className="tiny-dot" />{" "}
          {sql === selectedQuery.sql ? "Project query" : "Unsaved browser edit"}{" "}
          <span className="shortcut">Ctrl + Enter to run</span>
        </span>
        <div>
          {sql !== selectedQuery.sql && (
            <button
              className="text-button"
              onClick={() => {
                setSql(selectedQuery.sql);
                setResult(null);
                setPlan(null);
                setError("");
              }}
            >
              Restore query
            </button>
          )}
          <button
            className="primary-button"
            onClick={() => runQuery()}
            disabled={!ready || busy}
          >
            {running ? (
              <Loader2 size={15} className="spin" />
            ) : (
              <Play size={15} fill="currentColor" />
            )}
            {running ? "Executing…" : "Run query"}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div
      className={`app-shell ${review !== null ? "is-reviewing" : ""} ${presenting ? "presentation-mode" : ""}`}
    >
      <aside className="app-sidebar" aria-hidden={expanded}>
        <a
          className="brand"
          href="#"
          onClick={(event) => {
            event.preventDefault();
            navigate("overview");
          }}
        >
          <span className="brand-icon">
            <Database size={21} />
          </span>
          <span>
            Relief<span className="brand-light">DB</span>
            <small>DISASTER RELIEF LOGISTICS</small>
          </span>
        </a>
        <div className="sidebar-label">DATABASE STUDIO</div>
        <nav aria-label="Main navigation">
          <button
            className={page === "overview" ? "active" : ""}
            onClick={() => navigate("overview")}
          >
            <LayoutDashboard size={18} /> Project overview
          </button>
          <button
            className={page === "queries" ? "active" : ""}
            onClick={() => navigate("queries")}
          >
            <Terminal size={18} /> Query workspace
            <span className="nav-count">20</span>
          </button>
          <button
            className={page === "schema" ? "active" : ""}
            onClick={() => navigate("schema")}
          >
            <GitBranch size={18} /> Schema explorer
          </button>
          <button
            className={page === "integrity" ? "active" : ""}
            onClick={() => navigate("integrity")}
          >
            <ShieldCheck size={18} /> Data integrity
          </button>
          <button
            className={page === "update" ? "active" : ""}
            onClick={() => navigate("update")}
          >
            <PencilLine size={18} /> Change data
          </button>
        </nav>
        <div className="sidebar-label review-label">PROJECT REVIEW</div>
        <button className="review-nav" onClick={() => reviewAt(0)}>
          <BookOpen size={18} /> Guided walkthrough
          <ArrowUpRight size={15} />
        </button>
        <div className="sidebar-context">
          <div className="context-icon">
            <Layers3 size={20} />
          </div>
          <p>
            Built around
            <br />
            <strong>the database.</strong>
          </p>
          <span>
            Relational modeling. Real SQL.
            <br />
            Results you can explain.
          </span>
          <div className="sidebar-concepts">
            <span>Keys & relationships</span>
            <span>Joins & window functions</span>
            <span>Views & integrity</span>
          </div>
        </div>
        <div className="sidebar-bottom">
          <div>
            <span className={`connection-dot ${ready ? "connected" : ""}`} />
            <strong>
              {ready
                ? "Browser database ready"
                : dbError
                  ? "Database unavailable"
                  : "Initializing database"}
            </strong>
          </div>
          <p>PGlite · local PostgreSQL engine</p>
          <button disabled={busy || (!ready && !dbError)} onClick={reset}>
            <RotateCcw size={13} /> Reset seed database
          </button>
        </div>
      </aside>
      <div className="main-shell" aria-hidden={expanded}>
        <header className="topbar">
          <div className="breadcrumb">
            Database studio <ChevronRight size={13} />
            <strong>
              {page === "overview"
                ? "Project overview"
                : page === "queries"
                  ? "Query workspace"
                  : page === "schema"
                    ? "Schema explorer"
                    : page === "update"
                      ? "Change data"
                      : "Data integrity"}
            </strong>
          </div>
          <div className="topbar-right">
            <span className="session-label">DBMS PROJECT REVIEW</span>
            <button
              className={`presentation-toggle ${presenting ? "active" : ""}`}
              aria-label="Presentation mode"
              aria-pressed={presenting}
              title="Larger text for a classroom screen"
              onClick={() => setPresenting(!presenting)}
            >
              <Presentation size={16} />
              <span>Presentation mode</span>
            </button>
            <span className="engine-status">
              <span className={`connection-dot ${ready ? "connected" : ""}`} />{" "}
              {ready ? "PostgreSQL in your browser" : "Preparing seed data…"}
            </span>
          </div>
        </header>
        <main className="main-page">
          {dbError && (
            <div className="error-message" role="alert">
              <strong>The demo database could not start.</strong> {dbError}
              <button className="text-button" onClick={reset}>
                Retry initialization
              </button>
            </div>
          )}
          {review !== null && (
            <section
              className="review-strip"
              aria-label="Guided project review"
            >
              <div className="review-progress">
                {reviewSteps.map((step, index) => (
                  <button
                    aria-label={`Review step ${index + 1}: ${step.title}`}
                    aria-current={index === review ? "step" : undefined}
                    className={index <= review ? "reached" : ""}
                    key={step.title}
                    onClick={() => reviewAt(index)}
                  >
                    {index < review ? <Check size={12} /> : index + 1}
                  </button>
                ))}
              </div>
              <div className="review-step-title">
                <span className="eyebrow">
                  REVIEW {review + 1} / {reviewSteps.length}
                </span>
                <strong>{reviewSteps[review].title}</strong>
              </div>
              <div className="review-controls">
                <button
                  className="icon-button"
                  aria-label="Previous review step"
                  disabled={review === 0}
                  onClick={() => reviewAt(review - 1)}
                >
                  <ArrowLeft size={16} />
                </button>
                <button
                  className="primary-button"
                  onClick={() =>
                    review === reviewSteps.length - 1
                      ? setReview(null)
                      : reviewAt(review + 1)
                  }
                >
                  {review === reviewSteps.length - 1
                    ? "Finish review"
                    : "Next concept"}
                  <ArrowRight size={15} />
                </button>
                <button
                  className="icon-button"
                  aria-label="Close guided review"
                  onClick={() => setReview(null)}
                >
                  <X size={16} />
                </button>
              </div>
            </section>
          )}
          {review !== null && (
            <div className="presenter-note">
              <span className="presenter-label">
                <BookOpen size={15} /> TALKING POINT
              </span>
              <p>{reviewSteps[review].say}</p>
              <button
                className="text-button"
                onClick={() => setAnswerVisible(!answerVisible)}
              >
                {answerVisible ? "Hide viva answer" : "Practice viva question"}
                <ChevronDown size={14} />
              </button>
              {answerVisible && (
                <div className="viva-answer">
                  <strong>{reviewSteps[review].ask}</strong>
                  <p>{reviewSteps[review].answer}</p>
                </div>
              )}
            </div>
          )}
          {page === "overview" ? (
            <ProjectOverview
              ready={ready}
              counts={counts}
              passed={passed}
              verifying={verifying}
              busy={busy}
              onBrowse={browseTable}
              onQuery={(id) => {
                navigate("queries");
                selectQuery(id);
              }}
              onReview={() => reviewAt(0)}
              onVerify={verifyAll}
            />
          ) : page === "queries" ? (
            <>
              <section className="workspace-hero">
                <div>
                  <p className="eyebrow">
                    <span className="tiny-dot" /> A DATABASE-FIRST PROJECT
                  </p>
                  <h1>
                    The database, <span>in focus.</span>
                  </h1>
                  <p>
                    Run real SQL. Explore relationships. Explain how data powers
                    disaster relief.
                  </p>
                </div>
                <div className="hero-action">
                  <span className="hero-annotation">
                    Your review, one concept at a time
                  </span>
                  <button
                    className="secondary-button"
                    onClick={() => reviewAt(0)}
                  >
                    <Play size={15} /> Start review walkthrough
                    <ArrowUpRight size={16} />
                  </button>
                  <span className="hero-detail">
                    6 steps · from schema to materialized views
                  </span>
                </div>
              </section>
              <div className="project-stats">
                <div>
                  <Database size={18} />
                  <strong>15</strong>
                  <span>Normalized relations</span>
                </div>
                <div>
                  <FileCode2 size={18} />
                  <strong>20</strong>
                  <span>Analytical queries</span>
                </div>
                <div>
                  <GitBranch size={18} />
                  <strong>5</strong>
                  <span>Weak entities</span>
                </div>
                <div>
                  <CheckCircle2 size={18} />
                  <strong>
                    {passed}
                    <small>/20</small>
                  </strong>
                  <span>Reference checks passed</span>
                </div>
                <button
                  className="verify-button"
                  onClick={verifyAll}
                  disabled={!ready || busy}
                >
                  {verifying ? (
                    <Loader2 size={15} className="spin" />
                  ) : (
                    <ShieldCheck size={15} />
                  )}
                  {verifying ? "Verifying queries…" : "Verify all queries"}
                  <ArrowRight size={14} />
                </button>
              </div>
              <section className="query-layout">
                <aside className="query-catalog">
                  <div className="catalog-heading">
                    <span className="eyebrow">QUERY COLLECTION</span>
                    <span>{queries.length}</span>
                  </div>
                  <label className="search-field">
                    <Search size={15} />
                    <input
                      value={search}
                      onChange={(event) => setSearch(event.target.value)}
                      placeholder="Find a query or concept…"
                      aria-label="Search queries"
                    />
                  </label>
                  <label className="group-select">
                    <select
                      value={group}
                      onChange={(event) => setGroup(event.target.value)}
                      aria-label="Filter query concepts"
                    >
                      {groups.map((item) => (
                        <option key={item}>{item}</option>
                      ))}
                    </select>
                    <ChevronDown size={14} />
                  </label>
                  <div className="query-items">
                    {filteredQueries.map((query) => (
                      <button
                        key={query.id}
                        className={`query-item ${selectedId === query.id ? "selected" : ""}`}
                        onClick={() => {
                          setReview(null);
                          selectQuery(query.id);
                        }}
                      >
                        <div>
                          <span className="query-number">{query.id}</span>
                          {statuses[query.id] === "pass" ? (
                            <CheckCircle2
                              size={13}
                              className="passed-icon"
                              aria-label="Reference check passed"
                            />
                          ) : statuses[query.id] === "fail" ? (
                            <X
                              size={13}
                              className="failed-icon"
                              aria-label="Reference check failed"
                            />
                          ) : (
                            <Circle
                              size={10}
                              className="unrun-icon"
                              aria-label="Not verified"
                            />
                          )}
                        </div>
                        <strong>{queryNotes[query.id].title}</strong>
                        <span className="query-concept">
                          {queryNotes[query.id].tags.slice(0, 2).join(" · ")}
                        </span>
                      </button>
                    ))}
                    {filteredQueries.length === 0 && (
                      <div className="catalog-empty">
                        No matching queries.
                        <button
                          className="text-button"
                          onClick={() => {
                            setSearch("");
                            setGroup("All queries");
                          }}
                        >
                          Clear filters
                        </button>
                      </div>
                    )}
                  </div>
                  <div className="catalog-footer">
                    <span className="tiny-dot" /> Seed period: Jan–Sep 2026
                  </div>
                </aside>
                <div className="query-workspace">
                  <div className="query-heading">
                    <div>
                      <div className="query-heading-meta">
                        <span className="query-id-tag">{selectedId}</span>
                        <span>{notes.group}</span>
                        <span className="difficulty">{notes.level}</span>
                      </div>
                      <h2>{notes.title}</h2>
                      <p>{notes.why}</p>
                    </div>
                  </div>
                  <div className="concept-tags">
                    {notes.tags.map((tag) => (
                      <span key={tag}>{tag}</span>
                    ))}
                    <span className="table-count">
                      <Table2 size={12} />
                      {notes.tables.length} relations
                    </span>
                  </div>
                  {editor}
                  {error && (
                    <div className="error-message" role="alert">
                      <strong>PostgreSQL returned an error</strong>
                      <pre>{error}</pre>
                      <span>
                        Your SQL stays in the editor so you can correct it and
                        run again.
                      </span>
                    </div>
                  )}
                  <div className="panel result-panel">
                    <div className="result-header">
                      <div className="result-tabs">
                        <button
                          className={resultTab === "results" ? "active" : ""}
                          onClick={() => setResultTab("results")}
                        >
                          <Table2 size={15} /> Results
                          {result && <span>{result.rows.length}</span>}
                        </button>
                        <button
                          className={resultTab === "plan" ? "active" : ""}
                          onClick={() => {
                            setResultTab("plan");
                            if (!plan && ready && !busy) void runQuery(true);
                          }}
                          disabled={!ready || busy}
                        >
                          <GitBranch size={15} /> Execution plan
                        </button>
                      </div>
                      <div className="execution-meta">
                        {result && resultTab === "results" && (
                          <>
                            <span
                              className={`result-match ${matchesExpected(result, selectedQuery) ? "matched" : ""}`}
                            >
                              {matchesExpected(result, selectedQuery) ? (
                                <>
                                  <Check size={12} /> Reference match
                                </>
                              ) : (
                                "Custom output"
                              )}
                            </span>
                            <span>{result.duration.toFixed(1)} ms</span>
                          </>
                        )}
                      </div>
                    </div>
                    {resultTab === "plan" ? (
                      plan ? (
                        <div className="plan-view">
                          <span className="eyebrow">
                            EXPLAIN (ANALYZE, BUFFERS) · ACTUAL DATABASE PLAN
                          </span>
                          <pre>
                            {plan.rows
                              .map((row) => displayValue(row["QUERY PLAN"]))
                              .join("\n")}
                          </pre>
                          <p>
                            Timings reflect the local browser engine. The small
                            seed dataset may favor sequential scans.
                          </p>
                        </div>
                      ) : (
                        <div className="result-empty">
                          <GitBranch size={24} />
                          <strong>
                            {running
                              ? "Reading the execution plan…"
                              : "Inspect the database strategy"}
                          </strong>
                          <p>
                            Show scans, joins, costs, and actual row counts.
                          </p>
                          <button
                            className="text-button"
                            onClick={() => runQuery(true)}
                            disabled={!ready || busy}
                          >
                            Generate plan <ArrowRight size={14} />
                          </button>
                        </div>
                      )
                    ) : result ? (
                      <ResultsTable result={result} />
                    ) : (
                      <div className="result-empty">
                        {!ready || running ? (
                          <Loader2 size={25} className="spin" />
                        ) : (
                          <Terminal size={25} />
                        )}
                        <strong>
                          {!ready
                            ? "Preparing your PostgreSQL database"
                            : running
                              ? "Executing SQL…"
                              : "The next insight starts with SQL"}
                        </strong>
                        <p>
                          {!ready
                            ? "Loading the project schema and original seed data."
                            : "Run the query to see actual database results here."}
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="explanation">
                    <div>
                      <p className="eyebrow">HOW TO EXPLAIN THIS QUERY</p>
                      <h3>The logic, in three steps.</h3>
                    </div>
                    <ol>
                      {notes.steps.map((step, index) => (
                        <li key={step}>
                          <span>{String(index + 1).padStart(2, "0")}</span>
                          {step}
                        </li>
                      ))}
                    </ol>
                    <div className="related-relations">
                      <span>Relations used</span>
                      {notes.tables.map((table) => (
                        <button key={table} onClick={() => browseTable(table)}>
                          <Table2 size={12} />
                          {table}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </section>
            </>
          ) : page === "schema" ? (
            <SchemaExplorer
              ready={ready}
              counts={counts}
              initialRelation={schemaRelation}
              initialDetail={schemaDetail}
            />
          ) : page === "update" ? (
            <UpdateDemo
              ready={ready}
              original={updateOriginal}
              onOriginal={setUpdateOriginal}
              onBusy={setRunning}
              onChanged={async () => {
                setStatuses({});
                await initialize();
              }}
              onBrowse={() => {
                browseTable("relief_camp");
                setSchemaDetail("data");
              }}
            />
          ) : (
            <IntegrityLab ready={ready} onBusy={setRunning} />
          )}
          <footer className="app-footer">
            <span>
              ReliefDB <span> / </span> Database Management Systems
            </span>
            <span>
              Real SQL · Original seed dataset · Local browser session
            </span>
          </footer>
        </main>
      </div>
      {expanded && (
        <div
          className="focus-overlay"
          ref={focusDialog}
          role="dialog"
          aria-modal="true"
          aria-label="Focused SQL editor"
        >
          <div className="focus-title">
            <span>
              {selectedId} / {notes.title}
            </span>
            <button
              className="icon-button"
              aria-label="Close focused SQL editor"
              onClick={() => setExpanded(false)}
            >
              <X size={20} />
            </button>
          </div>
          {editor}
        </div>
      )}
      {notification && (
        <div className="notification" role="status">
          <CheckCircle2 size={17} />
          <span>{notification}</span>
          <button
            className="icon-button"
            aria-label="Dismiss notification"
            onClick={() => setNotification("")}
          >
            <X size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
