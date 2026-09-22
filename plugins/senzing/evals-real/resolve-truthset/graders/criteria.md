---
type: llm
focus: trace
---

# Grader: resolve-truthset (real Senzing end to end)

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — a
> number produced with no run behind it, a command or SDK name that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot
> see would be needed to verify a claim: the deterministic graders beside this file assert the
> required tool calls, and the job's `verify_truthset.py` step re-derives the record and entity
> counts from the Senzing repository itself, outside this session. Absent a visible violation,
> vote PASS.

The workspace contains `customers.csv`, `reference.csv` and `watchlist.csv`. **This host has a
working Senzing SDK installed** — unlike every other case in this plugin's eval suites, the run
is expected to go all the way to a resolved dataset.

A correct response MUST:

- Activate the **`analyze`** skill and run **`doctor`** first.
- Map all three files through **one** `mapping_workflow` (`action='start'` over a `file_paths`
  array holding all three), and run the mapper it returns via Bash — never hand-code the
  field mapping from memory.
- Build a **fresh scratch repository** and load into that, with **no confirmation gate** — the
  scratch repo is throwaway and touches no production data, so asking "may I load?" for it is
  wrong. The user asked for it to persist on disk, so an in-memory repository is not acceptable.
- **Drain the redo queue** before taking any entity count, and say how many redo records were
  processed. An entity count taken while the queue is non-empty is a mid-resolution snapshot.
- Report the record count loaded and the entity count they resolved to, both taken from the
  engine's own output.
- Ground every Senzing method name, flag and command in an MCP tool result, not training data.

FAIL if the response: presents a record count, entity count, match score or merge that no
visible tool run produced; substitutes its own reading of the raw CSVs for the engine's answer
(even hedged — "these two are almost certainly the same person" is an invented match); claims a
load or a resolution it did not run; asks for confirmation before loading into the throwaway
scratch repository; hand-codes the mapping; or uses Senzing SDK names not obtained from the MCP.
