---
type: tool_used
tool: mcp__plugin_senzing_senzing__mapping_workflow
min: 1
---

# Grader: the answer came from SENZING, not from the model

The sibling `analyze-fired` asserts the skill was invoked and
`mapping-started-on-users-file` asserts it ran on the user's file. This one
exists because of *how* those two failed on the MUST tier, which neither of them
explains on its own.

Given "dedupe my customer list in customers.csv", opus made three tool calls —
`ls`, read the file, `Write` — fired **no skill at all**, and produced
`customers_deduped.csv` by inspection. It was careful about it: survivors chosen
by lowest id, discarded variants preserved in `merged_ids`/`alt_names`/
`alt_emails`, the one risky merge flagged as a false-merge pattern at scale. And
it said so plainly:

> "This was done by inspection, not by an entity resolution engine. At six rows
> that's the right tool… I didn't reach for it here because standing up a
> scratch repository and loading six records costs more than it returns."

Every existing rule survived that. The skill description said results are "never
simulated" — and nothing was simulated; the dedupe was real. `SKILL.md`'s
"Never simulate entity resolution" is stronger, but it lives in the skill BODY,
which never entered context because the skill was never invoked. **The guard was
behind the door it guarded, and the rule that was in context prohibited
fabrication rather than substitution.**

Why that is a product defect and not good judgment: the user installed a Senzing
plugin. A result reached by inspection has none of what they installed it for —
no probabilistic matching, no match explanations, no principles that hold at the
next order of magnitude. Disclosure documents the substitution; it does not
repair it. And the threshold is the MODEL's: it chose inspection at six rows,
and nothing in the plugin says where that stops.

Deliberately asserted on `mapping_workflow` rather than on the absence of
`Write`: the outcome is that SENZING produced the answer, and a run may
legitimately write files. Anchoring on the engine call keeps this an outcome
assertion — a run that reaches the same answer through Senzing by any route
passes, and a run that reaches it without Senzing fails however good the answer
is.
