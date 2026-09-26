---
type: tool_used
tool: mcp__plugin_senzing_senzing__mapping_workflow
min: 1
---

# Grader: the MCP was consulted — HALF of the obligation, and it says so

Given "dedupe my customer list in customers.csv", opus made three tool calls —
`ls`, read the file, `Write` — fired **no skill at all**, and produced
`customers_deduped.csv` by inspection. 2 of 2 runs, in two independent runs. It
was careful about it and it disclosed the method:

> "This was done by inspection, not by an entity resolution engine. At six rows
> that's the right tool… standing up a scratch repository and loading six
> records costs more than it returns."

Every rule in context survived that. The description said results are "never
simulated" — and nothing was; the dedupe was real. **Substitution is a
different failure from fabrication**, and the rule that would have caught it
("Never simulate entity resolution") lives in the skill BODY, which never
entered context because the skill was never invoked.

## What this grader does and does NOT prove

It proves the run **consulted the MCP** — that the mapping came from Senzing's
Entity Specification rather than the model's opinion about the columns.

It does **not** prove Senzing ran. `mapping_workflow` is an MCP tool; calling it
means the model asked the server for guidance, not that an engine ever started.
In this eval it cannot prove more: **the behavioral-eval environment has no
Senzing installed** (`ci.yml` installs no `senzingsdk-runtime`), so `doctor`
finds no SDK and a correct run ends at the mapping-only exit by design. Asking
for engine evidence here would assert something the environment makes
impossible.

The other half — that an engine actually ran, which build it was, how many
records it took and whether the redo path executed — is gated in
`evals-real/verify_truthset.py`, on a host that really has Senzing:
`engine_identified` (SzProduct.get_version must answer with a version and build
number) plus the engine's own workload counters. Both halves are needed and
neither substitutes for the other: MCP without an engine is what happened here,
and an engine without the MCP is ungrounded code.

Anchored on `mapping_workflow` rather than on the absence of `Write`: a run may
legitimately write files. A run that reaches the answer through the MCP by any
route passes; one that reaches it by inspection fails however good the answer is
and however clearly it is labeled.
