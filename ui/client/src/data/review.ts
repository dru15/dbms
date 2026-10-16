export const queryNotes: Record<
  string,
  {
    title: string;
    group: string;
    level: string;
    tags: string[];
    tables: string[];
    why: string;
    steps: string[];
  }
> = {
  Q01: {
    title: "Camps nearing capacity",
    group: "Joins & aggregation",
    level: "Foundation",
    tags: ["INNER JOIN", "GROUP BY", "HAVING"],
    tables: ["relief_camp", "registered_family", "family_member"],
    why: "Find camps above 90% occupancy so relief teams can arrange extra shelter before space runs out.",
    steps: [
      "Join camps to families and their members.",
      "Count people per camp and calculate occupancy.",
      "Use HAVING to filter the aggregated count.",
    ],
  },
  Q02: {
    title: "Supplies sent to each camp",
    group: "Joins & aggregation",
    level: "Foundation",
    tags: ["MULTI-TABLE JOIN", "SUM"],
    tables: ["shipment", "shipment_line", "relief_camp", "supply_item"],
    why: "Trace every supply item sent to a camp, including shipments still in transit.",
    steps: [
      "Join shipment headers with their line items.",
      "Resolve camp and item names using foreign keys.",
      "Sum quantities for each camp–item pair.",
    ],
  },
  Q03: {
    title: "Critical requests without supply",
    group: "Subqueries & sets",
    level: "Intermediate",
    tags: ["NOT EXISTS", "CORRELATED SUBQUERY"],
    tables: ["supply_request", "request_line", "shipment", "shipment_line"],
    why: "Identify critical request lines without a matching later shipment. Shipment existence is measured; this does not claim delivery.",
    steps: [
      "Select critical supply requests.",
      "Correlate shipments by camp, item, and date.",
      "Keep request lines for which no shipment exists.",
    ],
  },
  Q04: {
    title: "Donors reaching every camp",
    group: "Subqueries & sets",
    level: "Intermediate",
    tags: ["RELATIONAL DIVISION", "COUNT DISTINCT"],
    tables: ["donor", "shipment", "relief_camp"],
    why: "Discover donors with complete geographical coverage across all registered camps.",
    steps: [
      "Count distinct camps served by each donor.",
      "Get the total number of relief camps.",
      "Retain donors whose coverage equals that total.",
    ],
  },
  Q05: {
    title: "Top donors by supply category",
    group: "Window functions",
    level: "Advanced",
    tags: ["CTE", "DENSE_RANK", "PARTITION BY"],
    tables: ["shipment", "shipment_line", "supply_item", "donor"],
    why: "Rank donors within each supply category, using delivered quantities and preserving ties.",
    steps: [
      "Aggregate delivered quantities by donor and category.",
      "Assign DENSE_RANK within each category.",
      "Return the first three ranks, including tied donors.",
    ],
  },
  Q06: {
    title: "Where demand exceeds delivery",
    group: "Joins & aggregation",
    level: "Advanced",
    tags: ["CTE", "FULL OUTER JOIN", "COALESCE"],
    tables: ["supply_request", "request_line", "shipment", "shipment_line"],
    why: "Compare requested and delivered units without losing items that appear on only one side.",
    steps: [
      "Aggregate requested and delivered quantities separately.",
      "FULL OUTER JOIN on camp and item; replace NULL with zero.",
      "Return positive differences as unmet demand.",
    ],
  },
  Q07: {
    title: "Expired volunteer certifications",
    group: "Joins & aggregation",
    level: "Foundation",
    tags: ["INNER JOIN", "DATE FILTER"],
    tables: [
      "volunteer",
      "volunteer_certification",
      "assignment",
      "relief_camp",
    ],
    why: "Find assigned volunteers needing certification renewal as of the fixed review date, 30 September 2026.",
    steps: [
      "Join volunteers, certifications, and camp assignments.",
      "Compare expiry dates with the seed reference date.",
      "Display the affected volunteer and camp.",
    ],
  },
  Q08: {
    title: "Camps missing medical volunteers",
    group: "Subqueries & sets",
    level: "Intermediate",
    tags: ["ANTI-JOIN", "NOT EXISTS"],
    tables: ["relief_camp", "assignment", "volunteer"],
    why: "Highlight camps with no assigned volunteer whose skill is medical.",
    steps: [
      "Start from every relief camp.",
      "Search its assignments for medical-skilled volunteers.",
      "Keep camps for which that search finds no rows.",
    ],
  },
  Q09: {
    title: "Running delivery totals",
    group: "Window functions",
    level: "Advanced",
    tags: ["SUM OVER", "PARTITION BY", "ROWS"],
    tables: ["shipment", "shipment_line", "relief_camp"],
    why: "Show how delivered inventory accumulates over time without collapsing each shipment into a single camp total.",
    steps: [
      "Sum line quantities per delivered shipment.",
      "Partition by camp and order by date and shipment ID.",
      "Accumulate quantities with an explicit ROWS frame.",
    ],
  },
  Q10: {
    title: "Request-to-shipment response time",
    group: "Joins & aggregation",
    level: "Intermediate",
    tags: ["CTE", "MIN", "DATE ARITHMETIC"],
    tables: ["supply_request", "request_line", "shipment", "shipment_line"],
    why: "Measure average days to the first matching shipment. This measures shipment response, rather than full quantity fulfillment.",
    steps: [
      "Match each requested item to later shipments at its camp.",
      "Choose the first matching shipment date per request line.",
      "Average the date differences for matched lines.",
    ],
  },
  Q11: {
    title: "Children and elders by camp",
    group: "Joins & aggregation",
    level: "Intermediate",
    tags: ["FILTER", "CONDITIONAL AGGREGATION"],
    tables: ["relief_camp", "registered_family", "family_member"],
    why: "Support targeted care by counting children under five and elders over sixty.",
    steps: [
      "Keep all camps with LEFT JOIN.",
      "Apply different FILTER conditions to the same members.",
      "Return both vulnerable groups in one aggregated row.",
    ],
  },
  Q12: {
    title: "Month-over-month shipments",
    group: "Window functions",
    level: "Advanced",
    tags: ["LAG", "DATE_TRUNC", "CTE"],
    tables: ["shipment"],
    why: "Compare monthly shipment activity with the preceding month to identify changes in logistics throughput.",
    steps: [
      "Group shipment dates into calendar months.",
      "Use LAG to access the preceding monthly count.",
      "Subtract that count to calculate the change.",
    ],
  },
  Q13: {
    title: "Requested items never shipped",
    group: "Subqueries & sets",
    level: "Intermediate",
    tags: ["EXISTS", "NOT EXISTS"],
    tables: ["supply_item", "request_line", "shipment_line"],
    why: "Find catalog items with real demand but no shipment history.",
    steps: [
      "Require an item to appear in request_line.",
      "Exclude items present in shipment_line.",
      "Resolve the item name and category.",
    ],
  },
  Q14: {
    title: "Shelter capacity versus people",
    group: "Joins & aggregation",
    level: "Advanced",
    tags: ["CTE", "LEFT JOIN", "FAN-OUT PREVENTION"],
    tables: [
      "shelter_unit",
      "registered_family",
      "family_member",
      "relief_camp",
    ],
    why: "Compare shelter capacity with registered members without multiplying rows from two independent one-to-many relationships.",
    steps: [
      "Aggregate shelters and members independently.",
      "Join each one-row-per-camp summary to relief_camp.",
      "Subtract population from total shelter capacity.",
    ],
  },
  Q15: {
    title: "Volunteers sharing a skill",
    group: "Joins & aggregation",
    level: "Intermediate",
    tags: ["SELF-JOIN", "DEDUPLICATION"],
    tables: ["assignment", "volunteer", "relief_camp"],
    why: "Find pairs of volunteers with matching skills at the same camp, listing each pair once.",
    steps: [
      "Self-join assignments within the same camp.",
      "Compare skills after resolving both volunteers.",
      "Use the ID inequality to avoid self-pairs and mirrored pairs.",
    ],
  },
  Q16: {
    title: "Camps above average deliveries",
    group: "Subqueries & sets",
    level: "Intermediate",
    tags: ["SCALAR SUBQUERY", "AVG", "CTE"],
    tables: ["relief_camp", "shipment", "shipment_line"],
    why: "Identify camps receiving more delivered supply units than the average across all camps.",
    steps: [
      "Compute delivered totals while retaining zero-delivery camps.",
      "Calculate the average of those camp totals.",
      "Filter camp totals against that scalar average.",
    ],
  },
  Q17: {
    title: "Demand and shipment mismatch",
    group: "Subqueries & sets",
    level: "Advanced",
    tags: ["EXCEPT", "UNION ALL", "SET DIFFERENCE"],
    tables: ["request_line", "shipment_line", "supply_item"],
    why: "Find the symmetric difference: items requested only or shipped only, excluding items present in both sets.",
    steps: [
      "Subtract shipped items from requested items.",
      "Subtract requested items from shipped items.",
      "Combine both differences with their activity labels.",
    ],
  },
  Q18: {
    title: "Donors active every month",
    group: "Subqueries & sets",
    level: "Intermediate",
    tags: ["RELATIONAL DIVISION", "DATE_TRUNC"],
    tables: ["donor", "shipment"],
    why: "Identify donors with shipments in all nine months of the seed period, January through September 2026.",
    steps: [
      "Bucket shipments into distinct months per donor.",
      "Count the donor’s active months.",
      "Keep donors covering the full nine-month period.",
    ],
  },
  Q19: {
    title: "Camp operations view",
    group: "Views & materialization",
    level: "Advanced",
    tags: ["CREATE VIEW", "CTE", "LEFT JOIN"],
    tables: [
      "relief_camp",
      "registered_family",
      "supply_request",
      "assignment",
    ],
    why: "Provide one reusable relation for camp population, requests, and volunteer coverage. Requests have no closed-status field in this schema.",
    steps: [
      "Aggregate each operational dimension independently.",
      "Define a reusable camp_status_dashboard view.",
      "Query the view just like a regular relation.",
    ],
  },
  Q20: {
    title: "Materialized stock summary",
    group: "Views & materialization",
    level: "Advanced",
    tags: ["MATERIALIZED VIEW", "UNIQUE INDEX", "REFRESH"],
    tables: ["camp_stock", "relief_camp", "supply_item"],
    why: "Store a precomputed district–category inventory summary and demonstrate its explicit refresh lifecycle.",
    steps: [
      "Create the aggregate materialized view.",
      "Add a unique index on district and category.",
      "Refresh concurrently and read the stored summary.",
    ],
  },
};

export const relations = [
  {
    name: "relief_camp",
    kind: "Strong",
    description:
      "The central relief location. Owns shelters, receives shipments, and houses families.",
    key: "camp_id",
    topic:
      "A surrogate identity key distinguishes camps even when names repeat.",
  },
  {
    name: "supply_item",
    kind: "Strong",
    description:
      "Catalog of food, water, medical, shelter, clothing, and hygiene supplies.",
    key: "item_id",
    topic:
      "A UNIQUE constraint prevents duplicate item names; CHECK restricts categories.",
  },
  {
    name: "donor",
    kind: "Strong",
    description: "Individuals, NGOs, companies, and government contributors.",
    key: "donor_id",
    topic: "Shipments reference donors through a restricted foreign key.",
  },
  {
    name: "shipment",
    kind: "Strong",
    description: "A dated shipment linking one donor to one camp.",
    key: "shipment_id",
    topic:
      "Separate header data from repeated shipment lines to avoid partial dependencies.",
  },
  {
    name: "supply_request",
    kind: "Strong",
    description: "A camp request with its date and urgency level.",
    key: "request_id",
    topic:
      "Request header attributes depend on request_id, not on an item line.",
  },
  {
    name: "volunteer",
    kind: "Strong",
    description: "Volunteer identity, contact information, and primary skill.",
    key: "volunteer_id",
    topic:
      "Volunteers can serve several camps through the assignment relation.",
  },
  {
    name: "registered_family",
    kind: "Strong",
    description: "A household registration associated with a relief camp.",
    key: "family_id",
    topic:
      "Family identity determines household attributes; members are separate rows.",
  },
  {
    name: "shelter_unit",
    kind: "Weak",
    description: "An individual shelter belonging to one relief camp.",
    key: "camp_id + unit_no",
    topic:
      "unit_no is a partial key: shelter 1 can exist in several camps. Owner deletion cascades.",
  },
  {
    name: "shipment_line",
    kind: "Weak",
    description: "An item and quantity within a shipment.",
    key: "shipment_id + line_no",
    topic: "The owner key plus line discriminator identifies the weak entity.",
  },
  {
    name: "request_line",
    kind: "Weak",
    description: "An item and quantity within a supply request.",
    key: "request_id + line_no",
    topic: "Deleting the owner request cascades to its dependent lines.",
  },
  {
    name: "volunteer_certification",
    kind: "Weak",
    description: "A volunteer-owned qualification with an expiry date.",
    key: "volunteer_id + cert_no",
    topic: "Certification identity depends on its volunteer owner.",
  },
  {
    name: "family_member",
    kind: "Weak",
    description: "An individual person in a registered household.",
    key: "family_id + member_no",
    topic: "member_no distinguishes members only within one family.",
  },
  {
    name: "assignment",
    kind: "Associative",
    description:
      "Resolves the many-to-many relationship between volunteers and camps.",
    key: "volunteer_id + camp_id",
    topic: "The composite key permits one assignment per volunteer–camp pair.",
  },
  {
    name: "camp_stock",
    kind: "Supporting",
    description: "Inventory balance per camp and supply item.",
    key: "camp_id + item_id",
    topic:
      "A CHECK constraint rejects negative stock; composite identity prevents duplicate balances.",
  },
  {
    name: "request_audit",
    kind: "Supporting",
    description: "History of supply-request urgency changes.",
    key: "audit_id",
    topic:
      "The audit structure exists; its automatic logging trigger remains coursework to implement.",
  },
];

export const reviewSteps = [
  {
    title: "Start with the relational model",
    subtitle: "Keys, dependencies & normalization",
    page: "schema",
    query: "Q01",
    say: "Our database models disaster-relief logistics with 15 relations. Five weak entities use an owner key and a discriminator. Shipment headers and line items are decomposed to avoid repeating donor and camp data.",
    ask: "Why is shipment_line a weak entity?",
    answer:
      "line_no identifies a line only within its shipment. Its full primary key is (shipment_id, line_no), and it cannot exist without the owner shipment.",
  },
  {
    title: "Turn joins into a decision",
    subtitle: "INNER JOIN · GROUP BY · HAVING",
    page: "queries",
    query: "Q01",
    say: "This query joins camps, families, and members, groups by camp, and filters camps above 90% occupancy. WHERE filters rows before grouping; HAVING filters the aggregated groups.",
    ask: "Why use HAVING instead of WHERE?",
    answer:
      "The member count exists after aggregation. HAVING can filter COUNT(), whereas WHERE filters the input rows before COUNT() is calculated.",
  },
  {
    title: "Find a missing relationship",
    subtitle: "Correlated subquery · NOT EXISTS",
    page: "queries",
    query: "Q08",
    say: "An anti-join finds camps with no medical volunteer. NOT EXISTS asks whether a qualifying related assignment exists, without multiplying camp rows.",
    ask: "Why choose NOT EXISTS over NOT IN?",
    answer:
      "NOT EXISTS tests the existence of related rows. NOT IN requires extra care with NULL values in its subquery, which can make the predicate unknown.",
  },
  {
    title: "Rank without losing detail",
    subtitle: "CTEs · DENSE_RANK · PARTITION BY",
    page: "queries",
    query: "Q05",
    say: "We aggregate delivered contributions, then rank donors independently within each category. DENSE_RANK preserves ties and does not leave gaps in the ranking.",
    ask: "How is DENSE_RANK different from ROW_NUMBER?",
    answer:
      "DENSE_RANK gives equal totals the same rank. ROW_NUMBER assigns every row a separate position, even when the ordered values are tied.",
  },
  {
    title: "Explain time and performance",
    subtitle: "LAG · EXPLAIN ANALYZE",
    page: "queries",
    query: "Q12",
    say: "LAG compares each month with the previous month while keeping every monthly row. Open Execution plan to show what PostgreSQL actually executed; a sequential scan can be sensible for this small dataset.",
    ask: "Does an index always make a query faster?",
    answer:
      "No. On a small table or a query reading most rows, a sequential scan can cost less. Measure with EXPLAIN ANALYZE rather than assuming an index will help.",
  },
  {
    title: "Finish with reusable relations",
    subtitle: "Views · materialization · validation",
    page: "queries",
    query: "Q20",
    say: "A normal view stores a query definition; this materialized view stores its computed result. The unique index supports concurrent refresh. Finish by verifying all 20 queries against the independent Python reference outputs.",
    ask: "When can a materialized view be stale?",
    answer:
      "When underlying rows change after its last refresh. Its result remains stored until REFRESH MATERIALIZED VIEW recomputes it.",
  },
];

export const integrityExamples = [
  {
    title: "No negative inventory",
    constraint: "CHECK",
    sql: "UPDATE camp_stock\nSET quantity_on_hand = -1\nWHERE camp_id = 1 AND item_id = 1;",
    code: "23514",
    explanation: "quantity_on_hand >= 0 rejects an invalid stock balance.",
  },
  {
    title: "Every shipment needs a real donor",
    constraint: "FOREIGN KEY",
    sql: "INSERT INTO shipment\n  (shipment_date, status, donor_id, camp_id)\nVALUES (DATE '2026-09-30', 'dispatched', 99999, 1);",
    code: "23503",
    explanation:
      "donor_id must reference an existing donor; an orphan shipment is rejected.",
  },
  {
    title: "A shelter identity is unique",
    constraint: "PRIMARY KEY",
    sql: "INSERT INTO shelter_unit\nSELECT * FROM shelter_unit\nLIMIT 1;",
    code: "23505",
    explanation:
      "The composite key (camp_id, unit_no) rejects a duplicate shelter.",
  },
];
