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

- Activate the **`recipes`** skill and `Read` the bundled `cookbook/cookbook.md` catalog before
  presenting any list — never answer from training data, and never download it (no `curl`, no
  `WebFetch`: the catalog ships inside the plugin).
- Present ONLY entries that trace back to the catalog it read: title, the metadata line
  (category/difficulty/kitchen/duration/author) as the catalog carries it, and the
  "What you'll make" line. Do not invent a recipe, a category, an author, or a use case (for
  example, a "fraud" recipe) that is not in the visible catalog — even though the `recipes`
  skill's own description names "fraud" as an example use case, that is not evidence a fraud
  recipe exists in the catalog.
- If the bundled file had instead failed to open, the only correct response is to say which path
  failed (a packaging bug — there is no network question here, so it must not tell the user to
  allowlist a domain) — never to fall back to a remembered or plausible-looking list. Judge this
  branch only if it is what you actually see; do not assume it happened.

FAIL if the response: lists any recipe, author, or use case not present in the visible catalog;
presents a catalog before any tool call; claims the cookbook is unreachable, or asks the user to
allowlist a domain for it, while a successful `Read` of it is visible in the trace; downloads
recipe content with `curl`/`wget`/`WebFetch`; or writes a file.
