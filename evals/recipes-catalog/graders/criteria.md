---
type: llm
focus: trace
---

# Grader: recipes (catalog browsing, no simulation)

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool call, the file, and the real catalog titles. Absent a visible violation, vote PASS.

The user asked to browse the Senzing Cookbook with no recipe named. A correct response MUST:

- Activate the **`recipes`** skill and fetch the live `cookbook.md` catalog (`Bash` `curl`) before
  presenting any list — never answer from training data.
- Present ONLY entries that trace back to the fetched catalog: title, the metadata line
  (category/difficulty/kitchen/duration/author) as the catalog carries it, and the
  "What you'll make" line. Do not invent a recipe, a category, an author, or a use case (for
  example, a "fraud" recipe) that is not in the visible fetch result — even though the `recipes`
  skill's own description names "fraud" as an example use case, that is not evidence a fraud
  recipe exists in the catalog.
- If the fetch had instead failed validation (empty body, an HTML error page, or missing
  headings), the only correct response is to say the cookbook is unreachable and quote the URL and
  status — never to fall back to a remembered or plausible-looking list. Judge this branch only if
  it is what you actually see; do not assume it happened.

FAIL if the response: lists any recipe, author, or use case not present in a visible fetch result;
presents a catalog before any tool call; claims the cookbook is unreachable while a successful
fetch is visible in the trace (or vice versa); or writes a file.
