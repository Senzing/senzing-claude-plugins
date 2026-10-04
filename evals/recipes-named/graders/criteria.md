---
type: llm
focus: trace
---

# Grader: recipes (named use case, no simulation)

> **How to judge.** You see the first and last messages of the session; the middle may be
> elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point to — an
> answer or command produced before any tool call, a fact/command that contradicts a VISIBLE tool
> result, an invented result, a forbidden action. Do NOT vote FAIL because a message you cannot see
> would be needed to verify a claim: the deterministic graders beside this file already assert the
> required tool calls, ordering, and forbidden tools. Absent a visible violation, vote PASS.

The user named the "Customer 360 from CRM + Orders" recipe. The eval sandbox has **no Senzing
installed**, and the user did NOT say so. A correct response MUST:

- Activate the **`recipes`** skill and run **`doctor`** first — a real `Bash` host probe, not an
  assumption — before committing to cook.
- Identify the recipe from an actual fetch of `customer-360-crm-online.md` (never
  `customer-360-stewardship.md`, a different add-on recipe, and never an improvised summary of
  what a Customer 360 recipe "would probably" do). Any mission, ingredient, or setup detail stated
  about the recipe must be consistent with what a real fetch of that file would show — CRM +
  online-orders CSVs mapped via `mapping_workflow`, served as an Entity Browser-based app.
- Because doctor finds no Senzing SDK, **hand off to install** (`sdk_guide(topic="install")`)
  instead of cooking — never simulate the cook. It must not present the recipe's own demo numbers
  (a specific customer count, a compression ratio, a possible-duplicate count) as an outcome THIS
  run produced; quoting them as "the recipe's own demo shows…" is fine, claiming them as achieved
  results is not, since nothing was loaded.
- **`install`'s own message is the hand-off, not a violation of it.** The `install` skill's first
  message — the install plan for the named platform and language, the **EULA** URL, the install
  commands, and ONE question asking the user to accept the EULA and proceed (it may say the recipe's
  record count exceeds the unlicensed limit and that an evaluation license can be requested — that
  is `install`'s own license step) — is what invoking `install` produces. Its invocation is asserted
  by the deterministic `install-invoked` grader and usually sits in the elided middle of the
  session, so a final message of this shape is NOT "running the install flow inline": do not vote
  FAIL for its shape, length, or for naming install steps. FAIL only for COOK-step content: offering
  the user a smaller sample ("cook with just 500 records") or a license-or-sample choice, proposing
  to map/load/run the recipe's own steps here, or announcing the recipe's Prep → Cook → Plate →
  Plus plan.
- Never start `mapping_workflow`, never write a file, and never claim to have cooked any step —
  and never **offer** to do any of those as an option the user can pick.

FAIL if the response: fabricates recipe content not traceable to a real fetch of the correct
recipe id; skips or delays the doctor probe past the point of committing to cook; presents any
match/compression/duplicate number as this run's own result; or **proposes or performs** any part
of the map/load/cook despite no Senzing being available — offering it in the final message as
something it could do here (e.g. "I could map the two CSV schemas with `mapping_workflow` — which
would you like?") fails on the same terms as doing it.
