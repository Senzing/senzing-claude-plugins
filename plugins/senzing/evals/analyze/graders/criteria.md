---
type: llm
focus: trace
---

# Grader: analyze

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls, files and forbidden tools. Absent a visible violation, vote PASS.

The workspace contains `crm.csv` and `billing.csv`. The eval sandbox has **no Senzing installed**.

A correct response MUST:

- Activate the **`analyze`** skill (map → resolve → report), not answer conversationally, and
  run **`doctor`** before anything else.
- Use the Senzing MCP **`mapping_workflow`** (`action='start'` on the input files) to map the
  sources, and run the mapper/profiler script it returns via Bash — it must NOT hand-code the
  field mapping from memory.
- Treat the **scratch repository as the default load target with no confirmation gate**: the
  scratch repo is throwaway and touches no production data, so asking "may I load?" for it is
  wrong. An explicit "proceed?" confirmation is required ONLY for loading into the user's
  existing/production repository, which this prompt never requested.
- **Never fabricate** resolution results, match scores, merges, or entity counts. Because Senzing
  is not installed here, a correct run ends by saying so plainly and pivoting to install (via
  `sdk_guide`/the `install` skill) or the labeled zero-install prep tier — never by "simulating"
  what Senzing would do.
- Ground every Senzing fact and SDK method name via the MCP, not training data.

FAIL if the response: never starts `mapping_workflow` on the user's files; hand-codes the mapping;
presents any invented match/score/merge/entity count; asks for confirmation before loading into a
throwaway scratch repository; loads into (or offers to load into) a production instance without an
explicit "proceed?" that names the target; claims it cannot find the input files; or uses Senzing
SDK names not obtained from the MCP.
