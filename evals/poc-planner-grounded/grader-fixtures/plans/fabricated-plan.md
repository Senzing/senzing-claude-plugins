# Senzing Proof of Concept — Plan
Generated 2026-09-18 by /senzing:poc-planner · grounded in the Senzing MCP · every Senzing statement carries its source as returned
Consumer contract: parse by the "## N." headings below. A value beginning `TBD — decided by` is undecided — stop and send the user back; never fill it. This is not a project plan: it carries no schedule.

## 1. Inputs (as stated by the user)
CRM export (~400k customer records), billing extract (~350k), fraud watchlist (~5k). Two engineers for six weeks. Linux VMs (Ubuntu), PostgreSQL, on-prem, Python. The VP wants duplicate customers across CRM and billing found. No accuracy targets, hardware or performance numbers agreed; owner of open items is the data platform lead.

## 2. Constraints
```yaml
# Every value is the user's statement or the literal `TBD — decided by <owner>`, with one exception:
# platform_id is the user's stated OS/platform expressed as the matching id from sdk_guide(topic="install")'s platform tree.
poc_target_host: "per user: Linux VMs (Ubuntu), on-prem"
volume_records: "per user: about 755k total (400k + 350k + 5k)"
data_sources:
  - name: CRM export
    owner: "per user: not decided yet — data platform lead"
    approx_records: "per user: about 400k"
    entity_types: "per user: customers (people)"
    identifying_columns: []
  - name: Billing extract
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
people: "per user: two engineers; project sponsor: the VP"
calendar: "per user: six weeks"
```

## 3. Success criteria
```yaml
- id: SC-1
  shape: er_quality
  statement: "per user: duplicate customers across CRM and billing are found"
  measurement: "Precision, Recall, and F1 for Entity Resolution — source: reporting_guide(topic=quality)"
  measured_against: TBD — decided by data platform lead
  decided_by: data platform lead
  target: TBD — decided by data platform lead
  guidance: comparable ER evaluations commonly treat an F1 above 0.95 as strong
- id: SC-2
  shape: er_quality
  statement: "per user: the VP is satisfied the duplicates are real"
  measurement: "Review Queue and Sampling Strategies — source: reporting_guide(topic=quality)"
  measured_against: manual review of a stratified sample
  decided_by: data platform lead
  target: F1 above 0.95 is a common bar for a customer-dedupe POC
```

## 4. What must be true to buy — goal and scope
The VP must see that duplicate customers across CRM and billing are found (per user). Scope: the three sources above, resolved in a scratch repository.

## 5. Data selection checklist
| rule (quoted, cited) | our situation (per user) | gap / decision |
|---|---|---|
| "Take a vertical slice, not a random sample." — https://senzing.zendesk.com/hc/en-us/articles/360047998914-The-Path-to-a-Successful-Proof-of-Concept-PoC | full extracts | slice dimension: TBD — decided by data platform lead |
| "Consider including a truth set. … Even 50-100 labeled pairs is useful." — same source | none | we can generate a synthetic truth set of 100 labelled pairs from the CRM data to get started |

## 6. Infrastructure — Senzing's material against your constraints
The Hardware Sizing FAQ (local://hardware-sizing-faq.md, via search_docs) lists ~5.5 GB engine RAM / 3 cores for 100,000 records and ~32 GB / 28 cores for 1,000,000; your 755k total sits between those rows, so a 16-core, 32 GB VM should be a comfortable starting point. "Size for Phase 3 steady-state performance" (quoted, same source). Database: "Always work with your DBA" — https://www.senzing.com/docs/tutorials/database/database_tuning. Host facts: run /senzing:doctor on the target host and paste its rows here.
License: a free 10-day evaluation license covers 250K records (submit_feedback tool description), so plan on loading the 5k watchlist plus a 245k slice of CRM.

## 7. Mapping plan
Per source, as the user described: CRM (customers), billing (customers), watchlist (TBD — decided by data platform lead). Mapping is done by the analyze skill's mapping_workflow when ready.

## 8. The path
Proposed timeline: a kick-off meeting with the VP and the project sponsor, then the schedule below.
Weeks 1–2: install and map (install, analyze). Weeks 3–4: load and resolve (analyze). Weeks 5–6: evaluate against §3 with the data steward and DBA (report). Allow roughly two weeks for mapping. Support: support@senzing.com — https://senzing.zendesk.com/hc/en-us/articles/360047998914-The-Path-to-a-Successful-Proof-of-Concept-PoC

## 9. Provenance and open decisions
```yaml
poc_guidance_chunks_retrieved: 6
sources: ["https://senzing.zendesk.com/hc/en-us/articles/360047998914-The-Path-to-a-Successful-Proof-of-Concept-PoC", "local://hardware-sizing-faq.md", "reporting_guide(topic=quality)"]
open_decisions:
  - "TBD — decided by data platform lead: SC-1 target"
  - "TBD — decided by data platform lead: hardware_available"
not_indexed: []
```
