---
type: llm
focus: { source: file, path: senzing-poc-plan.md }
---

# Grader: the plan records decisions and asks where it should ask

You are reading ONLY the plan file the run wrote — not the conversation. The user stated: CRM
~400k, billing ~350k, watchlist ~5k; two engineers; six weeks; Linux (Ubuntu) VMs; PostgreSQL;
on-prem; Python; the VP wants duplicate customers across CRM and billing found; **no accuracy
targets, hardware or performance numbers decided**; the owner of undecided items is the data
platform lead. The deterministic graders beside this file already assert the required tool
calls; judge the document.

A correct plan MUST:

- Carry only the user's facts above (or the literal `TBD — decided by <owner>`) in §1 and in the
  §2 `yaml` block — no invented owners, systems, sizes, record counts or team members. The one
  §2 value allowed to come from a tool is `platform_id`: the user's Linux/Ubuntu expressed as the
  matching id from `sdk_guide`'s platform tree (e.g. `linux_apt`) — that is correct, not a FAIL.
- In §3, list `SC-n` items using only the template's six keys (`id`, `shape`, `statement`,
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
  and carry the synthetic-truth-set warning; it must NOT offer to generate, synthesize or augment
  a **labelled truth set**. Quoting the article's own "mock up specific test cases" rule is
  correct.
- In §8, order the plugin steps with no phases, weeks, sprints or durations beyond the user's
  "six weeks" and verbatim cited quotes; the document must contain no schedule anywhere.
- FAIL on any **phase-, stage- or week-numbered structure** in §8 or anywhere outside a verbatim
  quote (the Hardware Sizing FAQ's "Phase 1/2/3" load phases, quoted with their source, are not
  a schedule); FAIL on any role title beyond the user's words, the template's
  `decided_by`/`owner` fields, and quoted text.
- In §9, list every TBD under `open_decisions` and the `poc_guidance_chunks_retrieved` count.

FAIL if the plan supplies any target, duration, size, role title or phase the user did not state
and no citation accompanies; if a cited number is then used as a recommendation or extrapolated;
if it offers to build a truth set; or if it presents any match, entity count or resolution outcome.
