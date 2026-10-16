import { useEffect, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Database,
  GitBranch,
  Loader2,
  ShieldCheck,
  Table2,
} from "lucide-react";
import { getDatabase } from "./lib/database";
import { relations } from "./data/review";

const workflow = [
  {
    table: "donor",
    title: "Contribute",
    text: "Donors provide relief supplies.",
  },
  {
    table: "shipment",
    title: "Deliver",
    text: "Shipments carry itemized quantities.",
  },
  {
    table: "relief_camp",
    title: "Coordinate",
    text: "Camps receive supplies and shelter families.",
  },
  {
    table: "camp_stock",
    title: "Track",
    text: "Inventory records each camp–item balance.",
  },
];

export default function ProjectOverview({
  ready,
  counts,
  passed,
  verifying,
  busy,
  onBrowse,
  onQuery,
  onReview,
  onVerify,
}: {
  ready: boolean;
  counts: Record<string, number>;
  passed: number;
  verifying: boolean;
  busy: boolean;
  onBrowse: (table: string) => void;
  onQuery: (id: string) => void;
  onReview: () => void;
  onVerify: () => void;
}) {
  const [constraints, setConstraints] = useState<Record<string, number>>({});
  const [error, setError] = useState("");
  useEffect(() => {
    let cancelled = false;
    if (ready)
      getDatabase()
        .then((db) =>
          db.query<{ kind: string; total: number }>(`
      SELECT c.contype AS kind, COUNT(*)::int AS total
      FROM pg_constraint c
      JOIN pg_class t ON t.oid = c.conrelid
      JOIN pg_namespace n ON n.oid = t.relnamespace
      WHERE n.nspname = 'public' AND t.relkind = 'r'
      GROUP BY c.contype
    `),
        )
        .then(({ rows }) => {
          if (!cancelled)
            setConstraints(
              Object.fromEntries(rows.map((row) => [row.kind, row.total])),
            );
        })
        .catch((error) => {
          if (!cancelled) setError(String(error));
        });
    return () => {
      cancelled = true;
    };
  }, [ready]);

  const number = (value: number | undefined) =>
    ready && value !== undefined ? value.toLocaleString() : "—";
  const total = Object.values(counts).reduce((sum, value) => sum + value, 0);
  return (
    <section className="section-page overview-page">
      <div className="section-heading">
        <div>
          <p className="eyebrow">
            DISASTER RELIEF LOGISTICS · PROJECT OVERVIEW
          </p>
          <h1>One model. A coordinated response.</h1>
          <p>
            Connect donors, supplies, camps, volunteers, and families through a
            relational database.
          </p>
        </div>
        <button className="secondary-button" onClick={onReview}>
          <BookOpen size={16} /> Start review walkthrough{" "}
          <ArrowRight size={16} />
        </button>
      </div>

      <div className="overview-metrics">
        {[
          {
            title: "Relational tables",
            value: String(relations.length),
            detail: "7 strong · 5 weak · 3 other entities",
            table: "shipment_line",
          },
          {
            title: "Records in this session",
            value: number(total),
            detail: "Actual row counts across all 15 tables",
            table: "family_member",
          },
          {
            title: "Relief camps",
            value: number(counts.relief_camp),
            detail: "Linked to families, requests, and stock",
            table: "relief_camp",
          },
          {
            title: "Shipments",
            value: number(counts.shipment),
            detail: "Headers with separate item lines",
            table: "shipment",
          },
        ].map((metric) => (
          <button
            className="overview-metric"
            key={metric.title}
            onClick={() => onBrowse(metric.table)}
          >
            <span>
              {metric.title}
              <ArrowRight size={14} />
            </span>
            <strong>{metric.value}</strong>
            <small>{metric.detail}</small>
          </button>
        ))}
      </div>

      <div className="overview-workflow panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">THE PROBLEM WE MODEL</p>
            <h2>From contribution to camp inventory</h2>
          </div>
          <GitBranch size={22} />
        </div>
        <div className="workflow-stages">
          {workflow.map((stage, index) => (
            <button key={stage.table} onClick={() => onBrowse(stage.table)}>
              <span className="workflow-number">0{index + 1}</span>
              <strong>{stage.title}</strong>
              <p>{stage.text}</p>
              <code>{stage.table}</code>
              <ArrowRight size={16} />
            </button>
          ))}
        </div>
        <p className="workflow-caption">
          Each stage is a real table. Foreign keys connect the records; joins
          turn them into useful answers.
        </p>
      </div>

      <div className="overview-columns">
        <div className="panel overview-model">
          <div className="panel-heading">
            <h2>Show what is inside</h2>
            <Table2 size={19} />
          </div>
          <p>
            Open any table to inspect its columns, complete data, relationships,
            and original SQL definition.
          </p>
          <div className="overview-relations">
            {[
              "relief_camp",
              "shipment",
              "shipment_line",
              "registered_family",
              "assignment",
              "camp_stock",
            ].map((table) => (
              <button key={table} onClick={() => onBrowse(table)}>
                <Table2 size={14} />
                <code>{table}</code>
                <span>{number(counts[table])} rows</span>
              </button>
            ))}
          </div>
          <button
            className="text-button"
            onClick={() => onBrowse("relief_camp")}
          >
            Explore all 15 tables <ArrowRight size={14} />
          </button>
        </div>
        <div className="panel overview-proof">
          <div className="panel-heading">
            <h2>Enforced by the database</h2>
            <ShieldCheck size={19} />
          </div>
          {error ? (
            <p role="alert">Could not read constraints: {error}</p>
          ) : (
            <div className="constraint-metrics">
              {[
                { key: "p", title: "Primary keys" },
                { key: "f", title: "Foreign keys" },
                { key: "c", title: "CHECK constraints" },
                { key: "u", title: "Unique constraints" },
              ].map((item) => (
                <div key={item.key}>
                  <strong>{number(constraints[item.key])}</strong>
                  <span>{item.title}</span>
                </div>
              ))}
            </div>
          )}
          <p>
            These counts come from PostgreSQL's system catalog. Inspect the
            named constraints in each table's definition.
          </p>
          <div className="overview-validation">
            <CheckCircle2 size={19} />
            <div>
              <strong>{passed}/20 query checks passed</strong>
              <span>Complete outputs compared with reference CSVs.</span>
            </div>
          </div>
          <button
            className="secondary-button"
            onClick={onVerify}
            disabled={!ready || busy}
          >
            {verifying ? (
              <Loader2 className="spin" size={15} />
            ) : (
              <ShieldCheck size={15} />
            )}
            {verifying ? "Verifying queries…" : "Verify all queries"}
          </button>
        </div>
      </div>

      <div className="overview-questions">
        <div>
          <p className="eyebrow">DATA INTO DECISIONS</p>
          <h2>Three questions to demonstrate</h2>
        </div>
        {[
          {
            id: "Q01",
            title: "Which camps are nearing capacity?",
            concept: "Joins · GROUP BY · HAVING",
          },
          {
            id: "Q08",
            title: "Where are medical volunteers missing?",
            concept: "Correlated NOT EXISTS",
          },
          {
            id: "Q20",
            title: "How do we reuse an inventory summary?",
            concept: "Materialized view · unique index",
          },
        ].map((item) => (
          <button key={item.id} onClick={() => onQuery(item.id)}>
            <span className="query-id-tag">{item.id}</span>
            <strong>{item.title}</strong>
            <small>{item.concept}</small>
            <ArrowRight size={16} />
          </button>
        ))}
      </div>
      <div className="session-note">
        <Database size={17} />
        <p>
          <strong>Demo session</strong> · Real PostgreSQL queries run locally in
          your browser. Data changes last until reload or reset; this workspace
          is separate from the Docker PostgreSQL server.
        </p>
      </div>
    </section>
  );
}
