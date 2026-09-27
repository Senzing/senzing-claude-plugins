---
type: llm
focus: trace
---

# Grader: analyze over two related files (one workflow, join recognized)

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls (one `start` carrying both files, a `customer_id` join key in the entity
> plan) and forbidden shapes (a single-file `file_paths`). Absent a visible violation, vote PASS.

The workspace contains `customers.csv` (customer master) and `orders.csv` (order history). Both
share `customer_id`. The eval sandbox has **no Senzing installed**.

A correct response MUST:

- Activate the **`analyze`** skill and run **`doctor`** before anything else.
- Drive **ONE** `mapping_workflow` over **both** files — a single `start` whose `file_paths`
  lists both — and run the profiler/mapper scripts it returns via Bash. It must NOT hand-code the
  mapping, and it must NOT run one workflow per file.
- Treat the two files as **related**: the entity plan sent to the tool folds `orders` into the
  `customers` master through `customer_id` (child or relationship disposition), and any summary
  of the mapping presents the sources as one linked structure — not two unrelated datasets that
  happen to be in the same directory.
- If it fans out `field-mapper` sub-agents at all (the skill says fan-out is only for genuinely
  *independent* files, which these are not), **every sub-agent must receive its own
  `workspace_dir`** — two mappers sharing one directory overwrite each other's
  `profile_report.md` / `schema_hints.md` / `.sz-state.json`.
- Treat the scratch repository as the default load target with no confirmation gate; because
  Senzing is not installed here, end at the mapping-only exit — say so plainly, deliver the
  validated JSONL / field-to-attribute summary, and offer `install` — never a simulated result.
- Ground every Senzing fact and SDK method name via the MCP, not training data.

FAIL if you can see: two or more separate `mapping_workflow` `start` calls, or a `start` whose
`file_paths` holds only one of the two files; the files described as unrelated / mapped in
isolation with no join between them; two sub-agents given the same `workspace_dir`; a hand-coded
mapping; any invented match/score/merge/entity count; a "proceed?" gate before loading into a
throwaway scratch repository; a claim that the input files cannot be found; or Senzing SDK names
not obtained from the MCP.
