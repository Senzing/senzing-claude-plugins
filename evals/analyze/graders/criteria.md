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

**Did we use Senzing to do it?**

- The **`analyze`** skill is active (map → resolve → report), not a conversational answer, and
  **`doctor`** ran before anything else.
- The mapping comes from the Senzing MCP **`mapping_workflow`** (`action='start'` on the input
  files) and the mapper/profiler script it returns was run via Bash — never a field mapping
  hand-coded from memory.
- Every Senzing fact and SDK method name is grounded via the MCP, not training data.

**Did we get the outcome?**

- **The input files were found and worked on.** The scaffold puts both files in the working
  directory. A reply that says it could not find, read, open or access `crm.csv` / `billing.csv`
  is a FAIL. (Was the `inputs-were-found` regex on failure phrasing; whether the reply claims a
  missing input is a judgment about what it asserts, so it is yours.)
- **The scratch repository is the default load target with no confirmation gate.** It is
  throwaway and touches no production data, so asking "may I load?" for it is wrong. An explicit
  "proceed?" is required ONLY for loading into the user's existing/production repository, which
  this prompt never requested.
- **No fabricated result.** Because Senzing is not installed here, a correct run ends by saying so
  plainly and pivoting to install (via `sdk_guide` / the `install` skill) or the labelled
  zero-install prep tier — never a "simulated" resolution, match score, merge, or entity count.

FAIL if the response: never starts `mapping_workflow` on the user's files; hand-codes the mapping;
presents any invented match/score/merge/entity count; asks for confirmation before loading into a
throwaway scratch repository; loads into (or offers to load into) a production instance without an
explicit "proceed?" that names the target; claims it cannot find the input files; or uses Senzing
SDK names not obtained from the MCP.
