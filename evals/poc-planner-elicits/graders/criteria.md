---
type: llm
focus: last_message
---

# Grader: poc-planner asks Round 1 and stops

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. Do NOT vote FAIL because a message you cannot see would be needed to verify a claim: the
> deterministic graders beside this file already assert the required tool calls (PoC guidance
> retrieved via `search_docs`), the absence of a written file and the forbidden tools. Absent a
> visible violation, vote PASS.

The user gave no inventory, no constraints and no criteria. A correct reply is **`poc-planner`
asking its Round 1** and stopping.

**Did we get the outcome?** The reply ASKS, and proposes nothing of its own.

- **All four Round-1 blocks are present, each AS A QUESTION** — a sentence ending in `?` (a
  bulleted question stem counts): (1) the data — what, where it lives, who owns it, how many
  records; (2) infrastructure — hardware available, platform/OS, database, cloud or on-prem,
  throughput/latency to demonstrate; (3) people and the SDK language — who runs it; (4) what
  would have to be TRUE for their organization to buy — the three shapes (result quality, a
  functional integration, specific entity-graph scenarios) offered as openers, not as a menu to
  pick from. A block that is only *mentioned* in a declarative plan ("we will profile your data")
  is not asked; FAIL a block that is absent or only stated. (Were four `asks-about-*` regexes — a
  `?` within one sentence of a topic word; whether a block was asked is yours to read.)
- **No target, size, platform or timeline of its own**, in its own voice: no metric threshold
  (precision/recall/F1/match rate at or above N%), no duration or duration range ("4–6 weeks",
  "about a month"), no week/sprint/phase/milestone label, no hardware size. A number inside a
  verbatim quote carrying its source is the reply quoting the guidance and is not a FAIL; the
  same shape stated in the reply's own voice always is. (Were `no-metric-thresholds`,
  `no-duration-ranges` and `no-phase-labels`, each with a line-scoped quote exemption.)
- **No assumed inventory**, and no demo, mapping or install started.

**Did we use Senzing?** Retrieval is asserted deterministically. You judge: any Senzing claim in
the reply carries its source as returned; the reply may quote the retrieved guidance's own
questions, with their source, and that is correct.

FAIL if the reply answers "how to structure" with a plan or a schedule before any user input;
omits or merely states (rather than asks) any of the four blocks; names a target, size, platform
or duration of any kind that is not a verbatim cited quote; or fires `demo`/`ask`.
