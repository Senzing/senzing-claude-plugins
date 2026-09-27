---
type: llm
focus: last_message
---

# Grader: poc-planner asks Round 1 and stops

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. Do NOT vote FAIL because a message you cannot see would be needed to verify a claim: the
> deterministic graders beside this file already assert the required tool calls, the absence of a
> written file and the forbidden tools. Absent a visible violation, vote PASS.

The user gave no inventory, no constraints and no criteria. A correct reply is **`poc-planner`
asking its Round 1** — all four blocks present: (1) the data (what, where, who owns it, how many
records), (2) infrastructure (hardware available, platform/OS, database, cloud or on-prem,
throughput/latency to demonstrate), (3) people and the SDK language, (4) what would have to be
TRUE for their organization to buy — the three shapes (result quality, a functional integration,
specific entity-graph scenarios) offered as openers, not as a menu to pick from. It may quote the
retrieved guidance's own questions, with their source.

It must NOT: assume an inventory; propose a target, a size, a platform or a timeline; present a
phased or week-numbered plan; name any number that is not a verbatim cited quote; start a demo,
a mapping or an install; or activate `ask` or `demo`.

FAIL if the reply answers "how to structure" with a plan or a schedule before any user input,
names a number of any kind that is not a verbatim cited quote, or fires `demo`/`ask`.
