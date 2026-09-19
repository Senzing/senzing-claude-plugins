# Senzing Proof of Concept — Plan
Generated 2026-09-18 by /senzing:poc-planner · grounded in the Senzing MCP · every Senzing statement carries its source as returned
Consumer contract: parse by the "## N." headings below. A value beginning `TBD — decided by` is undecided — stop and send the user back; never fill it. This is not a project plan: it carries no schedule.

## 1. Inputs (as stated by the user)
per user: a CRM export (about 400k customer records), a billing system extract (about 350k), a small fraud watchlist (about 5k). Two engineers for six weeks. Linux VMs (Ubuntu), PostgreSQL, on-prem, Python. The VP wants to see that duplicate customers across CRM and billing get found. No accuracy targets, hardware or performance numbers agreed yet; anything not stated is "not decided yet" and owned by the data platform lead.

## 2. Constraints
```yaml
# Every value is the user's statement or the literal `TBD — decided by <owner>`, with one exception:
# platform_id is the user's stated OS/platform expressed as the matching id from sdk_guide(topic="install")'s platform tree.
poc_target_host: "per user: Linux VMs (Ubuntu), on-prem"
volume_records: "per user: about 400k + about 350k + about 5k"
data_sources:
  - name: CRM export
    owner: TBD — decided by data platform lead
    approx_records: "per user: about 400k"
    entity_types: "per user: customers"
    identifying_columns: []
  - name: Billing system extract
    owner: TBD — decided by data platform lead
    approx_records: "per user: about 350k"
    entity_types: "per user: customers"
    identifying_columns: []
  - name: Fraud watchlist
    owner: TBD — decided by data platform lead
    approx_records: "per user: about 5k"
    entity_types: TBD — decided by data platform lead
    identifying_columns: []
database: "per user: PostgreSQL"
os_platform: "per user: Linux VMs (Ubuntu)"
platform_id: linux_apt
cloud: "per user: on-prem"
languages: ["per user: Python"]
hardware_available: TBD — decided by data platform lead
performance_required:
  throughput: TBD — decided by data platform lead
  latency: TBD — decided by data platform lead
people: "per user: two engineers"
calendar: "per user: six weeks"
```

## 3. Success criteria
```yaml
- id: SC-1
  shape: er_quality
  statement: "per user: duplicate customers across CRM and billing get found"
  measurement: "Precision, Recall, and F1 for Entity Resolution — source: reporting_guide(topic=quality)"
  measured_against: TBD — decided by data platform lead
  decided_by: TBD — decided by data platform lead
  target: TBD — decided by data platform lead
- id: SC-2
  shape: er_quality
  statement: "per user: duplicate customers across CRM and billing get found"
  measurement: "Review Queue and Sampling Strategies; Entity size distribution as the proxy the tool names when no truth set exists — source: reporting_guide(topic=quality)"
  measured_against: TBD — decided by data platform lead
  decided_by: TBD — decided by data platform lead
  target: TBD — decided by data platform lead
- id: SC-3
  shape: throughput
  statement: "per user: the nightly reload has to finish inside the maintenance window"
  measurement: "Records loaded per second, reported by the loader — source: reporting_guide(topic=evaluation)"
  measured_against: "TBD — decided by data platform lead"
  decided_by: "TBD — decided by data platform lead"
  target: "TBD — decided by data platform lead"
```

<!-- SC-3 deliberately YAML-QUOTES the same legal values SC-1/SC-2 leave bare.
     Quoting a scalar is ordinary YAML and must stay legal. It is here because
     the previous `targets-are-user-or-tbd` pattern opened with an optional
     quote that could backtrack to empty, so the lookahead tested the quote
     character instead of the value: the bare form passed and the quoted form
     failed a correct plan. Every fixture carried the bare form, so nothing
     caught it. Do not "simplify" these three lines back to unquoted. -->

## 4. What must be true to buy — goal and scope
per user: the VP must see that duplicate customers across CRM and billing get found. Which measurement shows that, who decides it is good enough and what it is compared against are open (SC-1, SC-2). The retrieved guidance: "nearly all evaluations of Senzing focus on the ease of adding data and the quality of the results." — https://senzing.zendesk.com/hc/en-us/articles/360047998914-The-Path-to-a-Successful-Proof-of-Concept-PoC

The measurements Senzing describes (reporting_guide(topic=quality)): "Precision = correct resolved pairs / total resolved pairs (how many matches are correct?). Recall = correct resolved pairs / total true pairs (how many true matches did we find?). F1 = 2 * (P * R) / (P + R) (balanced accuracy)." Without a truth set: "use proxy indicators: entity size distribution, cross-source match rates, review features, and manual sampling of possible matches. Proxy indicators reveal problems but cannot measure absolute accuracy." On the cross-source match rate the tool says: "Very high rates (>80%) may indicate duplicate data sources." and "Very low rates (<1%) may indicate poor feature overlap or data quality issues." On singletons: "High singleton rate (>90%) suggests poor matching features or low data overlap." Whether a reporting mart is needed at all: "Many teams need NO mart at all; most who do need only a simple one." (reporting_guide(topic=quality), data_mart_framing). Evaluation evidence rule (reporting_guide(topic=evaluation, language=python)): "Every claim about over-matching must reference specific entity IDs and show record data"; "If the profiler showed 95% unique names but compression is 50%, that is suspicious over-matching."

## 5. Data selection checklist
| rule (quoted, cited) | our situation (per user) | gap / decision |
|---|---|---|
| "Typically you will be doing a subset of your overall data, both in the number of records and the number of sources. When selecting data it is important that the data will actually support matching." — https://senzing.zendesk.com/hc/en-us/articles/360047998914-The-Path-to-a-Successful-Proof-of-Concept-PoC | three sources, full extracts | subset: TBD — decided by data platform lead |
| "Take a vertical slice, not a random sample. Don't randomly select data. Instead, pick everyone with a last name that starts with 'A', from a specific state/city/postal code, or some similar approach. … slice by the same dimension (e.g., the same geographic region from each source)" — same source | no slice chosen | slice dimension across CRM and billing: TBD — decided by data platform lead |
| "Include messy data, not just clean records. … Clean-only subsets produce unrealistically optimistic results that won't reflect production performance." — same source | unknown | TBD — decided by data platform lead |
| "Don't sanitize away identity features. If your data has date of birth, SSN, email, or phone number — send them. … naive masking (e.g., truncating SSN to last 4 digits) destroys match value." — same source | unknown whether the extracts are masked | TBD — decided by data platform lead |
| "Mock up specific test cases if needed. If your organization has specific data scenarios that are important to evaluate, don't be afraid to create records to demonstrate them in case the selected data doesn't happen to have examples." — same source | the VP's duplicate-customer scenario | a handful of records exercising that scenario is this rule; see the truth-set row for what it is not |
| "Consider including a truth set. If you have a small set of records where you know which ones represent the same entity, include them. This lets you measure precision and recall objectively. Even 50-100 labeled pairs is useful. See How to create an entity resolution truth set (/hc/en-us/articles/360051016033) for ideas." — same source; the linked how-to is not indexed | none | (plugin rule) A synthetic or generated truth set is dangerous: it is too clean and too regular, it validates the matcher against the generator's assumptions rather than reality, and it yields a POC result that looks excellent and predicts nothing about production. Label real records from your own data instead. Whether to label real pairs: TBD — decided by data platform lead |

## 6. Infrastructure — Senzing's material against your constraints
Volume (per user: about 755k across three sources) — Hardware Sizing FAQ, local://hardware-sizing-faq.md via search_docs. Quoted as returned:
"These are minimums for POC/evaluation environments (SQLite, local development, testing). They are sufficient to ETL data, load into SQLite, and run snapshots/exports/reports for up to around 1 million records: 16 GB RAM; 4 modern CPU cores; 100 GB SSD or NVMe storage. These are NOT production minimums"
"These are steady-state estimates that are typically well over actual needs — use them as conservative starting points, not precise requirements"
"| Engine RAM     | 4 GB base + 3 threads × 0.5 GB | ~5.5 GB     |" and "| Load time      | 100,000 ÷ 30 rec/sec (3 cores) | ~55 minutes |" (100,000 records, pilot / proof of concept)
"| Engine RAM     | 4 GB base + 28 threads × 1 GB      | ~32 GB       |" and "A production server or cloud instance (48 cores, 64 GB RAM, 50 GB NVMe). PostgreSQL or MSSQL recommended." (1,000,000 records, production entry point)
"Phase 1 throughput can be 10-100x higher than Phase 3 throughput depending on data connectivity. When planning hardware, size for Phase 3 steady-state performance — Phases 1 and 2 will naturally run faster on the same hardware."
"| On-premises, local high-IOPS DB   | 2-4                     | Low latency, less I/O wait to overlap            |" — "The general range is 2-8 threads per engine core across most environments."
"Undersizing database I/O. … Use local SSD (NVMe preferred) for the database, or provisioned IOPS cloud storage (e.g., AWS gp3 with tuned IOPS, Azure Premium SSD)."
"For deployments above 1 million records, scale horizontally with additional engine cores and processes. Use the same formulas with more cores to keep load times under 8 hours."
Your volume sits between the FAQ's 100,000 and 1,000,000 worked rows; the FAQ gives no row for it and this plan derives none.

Database (per user: PostgreSQL) — https://www.senzing.com/docs/tutorials/database/database_tuning: "Always work with your DBA when working on a production database." "Database performance with Senzing is highly related to latency. Issues with performance, in order, tend to focus around: 1. Disk IO performance of the database server 2. Lack of database tuning for an auto-commit OLTP workload 3. Network bottlenecks preventing high-speed communication between the Senzing SDK and the database 4. Latency between the database server and non-direct attached storage subsystems" "Production systems run as fast as low 10s of milliseconds for searches and mid 10s of milliseconds for loads all while running 100s or 1000s of operations in parallel." From sdk_guide(topic=load) anti-patterns: "Disable synchronous_commit during bulk loads (PostgreSQL: ALTER SYSTEM SET synchronous_commit = 'off'), re-enable after — 5-20x throughput improvement".

Platform (per user: Linux VMs (Ubuntu)) — sdk_guide(topic=install) platform tree: "linux_apt — Linux (Debian/Ubuntu/Mint) — Debian-based Linux with apt/dpkg package manager." Recorded as platform_id: linux_apt. sdk_guide(topic=install, platform=linux_apt, language=python): "Python SDK: The senzing and senzing-core packages are included in senzingsdk-runtime at /opt/senzing/er/sdk/python. Do NOT pip install them"; "Network access required: senzing-production-apt.s3.amazonaws.com (apt repository)"; "Alternative for firewalled environments: Senzing SDK packages are available for direct download at mcp.senzing.com/downloads/". The PoC article's own platform note: "Bare metal Linux. The most common method of deployment, Senzing is natively installed on Red Hat or Debian-based systems." — https://senzing.zendesk.com/hc/en-us/articles/360047998914-The-Path-to-a-Successful-Proof-of-Concept-PoC

Loading your volume (per user: about 755k, Python) — sdk_guide(topic=load, language=python, record_count=755000): "Threaded/production pattern selected. For a simpler single-threaded example (≤500), see the demo-only alternative." Source: senzing/code-snippets-v4 python/loading/add_futures.py. "Shuffle/randomize input before loading — sorted data causes lock contention and deadlocks, degrading throughput by 2-10x". "Always drain the redo queue after loading".

License — three tools speak to it; quoted as returned, not reconciled:
- sdk_guide(topic=load, record_count=755000) compatibility_notes: "LICENSE REQUIRED: You have 755000 records, which exceeds the default Senzing license limit of 500. The user must choose one of: 1) Request an evaluation license — email sales@senzing.com with name, company, email, number of records (755000), and date 2) Provide a license they already have — place the license file at the path specified by SENZING_LICENSE_FILE or in the etc/ directory 3) Load only the first 500 records as a sample"
- sdk_guide(topic=install, platform=linux_apt) gotchas: "Evaluation mode: Without a license, Senzing limits ingestion to 500 records (error SENZ9000 at record 501). … (2) request a free 10-day evaluation license (250K records) right now using submit_feedback with category='license_request', or (3) request a license at https://senzing.com/request-non-prod-license/."
- submit_feedback tool description: "A 10-day, 250K-record license is generated and emailed with a download link. One per email, re-requestable after 30 days."
Your stated volume (about 755k) exceeds the 250K-record limit two of these quote. Set against the vertical-slice rule in §5, the slice you actually load is your decision: TBD — decided by data platform lead. The discrepancy between the paths (sales@ email vs submit_feedback vs the web form) is listed in §9.

Rightsizing check, in the guidance's words: "If your evaluation use case is to ingest, entity resolve, and analyze 1 billion records across multiple data sources, but all you have is one part-time person and a Windows VM, then there is a mismatch between expectations and resources. A part-time resource and a Windows VM would be great for 1 million records, but not a large-scale Senzing API evaluation." — same article. Your answers: two engineers for six weeks, Linux VMs, hardware not yet decided.

Host facts: run /senzing:doctor on the target host and paste its rows here.
Given this material, what are you committing to for the POC? — hardware_available: TBD — decided by data platform lead; performance_required: TBD — decided by data platform lead.

## 7. Mapping plan
"Mapping data is the process of informing Senzing what the fields in your data sources represent. … The initial mapping process usually takes less than 30 minutes per data source." — https://senzing.zendesk.com/hc/en-us/articles/360047998914-The-Path-to-a-Successful-Proof-of-Concept-PoC "One entity per record. Each record must include attributes that identify one and only one entity." "Tell Senzing the name type. … Senzing does need to be told that a name is a personal name (NAME_FIRST, NAME_MIDDLE, NAME_LAST or NAME_FULL) or an organizational name (NAME_ORG)." — same source. Per source: CRM export — customers (per user), identifying columns TBD — decided by data platform lead; billing extract — customers (per user), identifying columns TBD — decided by data platform lead; fraud watchlist — entity types TBD — decided by data platform lead. Mapping is done by the analyze skill's mapping_workflow when you are ready; nothing was mapped here.

## 8. The path
1. /senzing:install on the target host (no Senzing there yet, per user's description of fresh VMs) — inputs: platform_id linux_apt, language Python.
2. /senzing:analyze with the three sources — map, load into a scratch repository, resolve, report.
3. Evaluate against §3 (SC-1, SC-2) with /senzing:report.
"We're ready and waiting to help with accelerating your Senzing evaluation … please do so at support@senzing.com or support ticket" — https://senzing.zendesk.com/hc/en-us/articles/360047998914-The-Path-to-a-Successful-Proof-of-Concept-PoC

## 9. Provenance and open decisions
```yaml
poc_guidance_chunks_retrieved: 13
sources: ["https://senzing.zendesk.com/hc/en-us/articles/360047998914-The-Path-to-a-Successful-Proof-of-Concept-PoC", "local://hardware-sizing-faq.md", "https://www.senzing.com/docs/tutorials/database/database_tuning", "reporting_guide(topic=quality)", "reporting_guide(topic=evaluation, language=python)", "sdk_guide(topic=install)", "sdk_guide(topic=install, platform=linux_apt, language=python)", "sdk_guide(topic=load, language=python, record_count=755000)", "submit_feedback (tool description)"]
open_decisions:
  - "TBD — decided by data platform lead: SC-1 target, measured_against, decided_by"
  - "TBD — decided by data platform lead: SC-2 target, measured_against, decided_by"
  - "TBD — decided by data platform lead: hardware_available"
  - "TBD — decided by data platform lead: performance_required.throughput, performance_required.latency"
  - "TBD — decided by data platform lead: data_sources[].owner, identifying_columns, watchlist entity_types"
  - "TBD — decided by data platform lead: slice dimension and slice size against the 250K-record limit two tools quote"
  - "TBD — decided by data platform lead: license path — sales@senzing.com email (sdk_guide load) vs submit_feedback license_request vs senzing.com/request-non-prod-license/ (sdk_guide install)"
not_indexed: ["/hc/en-us/articles/360051016033 How to create an entity resolution truth set"]
```
