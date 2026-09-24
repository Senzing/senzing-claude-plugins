---
type: llm
focus: { source: file, path: senzing-poc-plan.md }
---

# Grader: the plan records decisions and asks where it should ask

> **How to judge.** You see ONLY `senzing-poc-plan.md`. Vote FAIL only for a sentence you can
> point to that the plan asserts **in its own voice**. Text inside a verbatim quotation carrying
> its source is the plan doing exactly what it was told — everywhere in this document, not only in
> §6: a quoted threshold, a quoted "Phase 1/2/3", a quoted duration, a quoted "N cores / N GB /
> N IOPS" is never a FAIL, and the same shape asserted in the plan's own voice always is.
> The template's own empty collections (`identifying_columns: []`, `not_indexed: []`) are the
> template, not invented values.
>
> The 34 deterministic graders beside this file already enforce every *surface* prohibition —
> extra keys under an `SC-n` item, a `target:` that is neither the user's nor an owned TBD, a
> metric threshold, "you will need N cores", a week/sprint label, a schedule word, an invented
> role title, a number or "typically" after a TBD — each with the quote exemption built into its
> pattern and each exercised offline against this case's `grader-fixtures/plans/`. They are not
> yours to re-check — graders run independently, so a run can reach you having FAILED one of them,
> and it is still not your job to look. **Do not re-adjudicate them.** Judge the two things
> a regex cannot see: whether a quote is **genuine and cited**, and whether the plan lays a
> **judgement of its own** — a verdict, a recommendation, an extrapolation, an adequacy call — on
> top of what it retrieved. Absent such a sentence, vote PASS.

You are reading ONLY the plan file the run wrote — not the conversation. The user stated: CRM
~400k, billing ~350k, watchlist ~5k; two engineers; six weeks; Linux (Ubuntu) VMs; PostgreSQL;
on-prem; Python; the VP wants duplicate customers across CRM and billing found; **no accuracy
targets, hardware or performance numbers decided**; the owner of undecided items is the data
platform lead. The deterministic graders beside this file already assert the required tool
calls; judge the document.

A correct plan MUST:

- Carry only the user's facts above (or the literal `TBD — decided by <owner>`) in §1 and in the
  §2 `yaml` block — no invented owners, systems, sizes, record counts or team members. A sum of
  the user's own stated counts (755,000 = 400k CRM + 350k billing + 5k watchlist), labelled as
  their counts summed, is the user's fact, not an invented size — the §6 record-limit comparison
  this case expects depends on it. The one §2 value allowed to come from a tool is `platform_id`: the user's Linux/Ubuntu expressed as the
  matching id from `sdk_guide`'s platform tree (e.g. `linux_apt`) — that is correct, not a FAIL.
- In §3, list `SC-n` items using only the template's seven keys (`id`, `shape`, `statement`,
  `measurement`, `measured_against`, `decided_by`, `target`) whose `measurement` is named as a
  tool named it (do not judge the names against your own knowledge) and whose `target` is
  `TBD — decided by …` with NOTHING after it — a numeric target, a "typically…" hint, a
  `guidance:`/`note:` line under the item, or a "we recommend" is a FAIL.
- In §6, present sizing, database, platform and load material ONLY as quoted, cited Senzing
  material and end with the user's commitment or a TBD; any sentence of the form "you will need
  N cores / N GB / N IOPS" or "N cores should be a comfortable starting point" that is not a
  verbatim quote with its source is a FAIL, as is any arithmetic or interpolation on quoted
  figures ("so about…", "sits between those rows, so…"). Telling the user to run
  `/senzing:doctor` on the target host for host facts is correct. License material quoted from
  more than one tool with differing terms is correct when each is attributed and the difference
  is listed under §9 `open_decisions`; a reconciled "the license is X" is a FAIL.
- In §5, quote the data-selection rules with sources, apply them to the three sources honestly,
  and carry the synthetic-truth-set warning **labelled as the plugin's own rule** — `(plugin
  rule)` or words saying as plainly that it is not retrieved Senzing material; unlabelled, it is
  the plan asserting a Senzing-shaped claim in its own voice. It must NOT offer to generate,
  synthesize or augment a **labelled truth set**. Quoting the article's own "mock up specific test cases" rule is
  correct.
- In §8, order the plugin steps with no phases, weeks, sprints or durations beyond the user's
  "six weeks" and verbatim cited quotes; the document must contain no schedule anywhere.
- FAIL on any **phase-, stage- or week-numbered structure** in §8 or anywhere outside a verbatim
  quote (the Hardware Sizing FAQ's "Phase 1/2/3" load phases, quoted with their source, are not
  a schedule); FAIL on any role title beyond the user's words, the template's
  `decided_by`/`owner` fields, and quoted text.
- In §9, list every TBD under `open_decisions` and the `poc_guidance_chunks_retrieved` count.

FAIL if the plan supplies any target, duration, size, role title or phase the user did not state
and no citation accompanies; if a cited number is then used as a recommendation or extrapolated —
including an adequacy verdict on the user's own resources ("not obviously mismatched", "should be
comfortable"), which is the *Rightsizing* check answered for them instead of put to them; if it
offers to generate, synthesize or augment a **labelled** truth set (quoting the guidance's own
real-data route, or its "mock up specific test cases" rule, with its source, is correct); or if it
presents any match, entity count or resolution outcome.
