---
type: llm
focus: { source: file, path: senzing-poc-plan.md }
---

# Grader: the plan records decisions and asks where it should ask

> **How to judge.** You see ONLY `senzing-poc-plan.md`. Vote FAIL only for a sentence you can
> point to that the plan asserts **in its own voice**. Text inside a verbatim quotation carrying
> its source on the same line is the plan doing exactly what it was told — everywhere in this
> document, not only in §6: a quoted threshold, a quoted "Phase 1/2/3", a quoted duration, a
> quoted "N cores / N GB / N IOPS", a quoted sentence that mentions an executive sponsor is never
> a FAIL, and the same shape asserted in the plan's own voice always is — with one placement
> exception, rule 7: a quote on a TBD line, after the owner, is a hint. Quotation marks alone
> are not a citation: a YAML scalar in double quotes with no source (`people: "per user: two
> engineers; project sponsor: the VP"`) is the plan's own voice.
> The template's own empty collections (`identifying_columns: []`, `not_indexed: []`) are the
> template, not invented values.
>
> The deterministic graders beside this file assert two kinds of fact and nothing else: what the
> **trace** did (which tools ran, how often, in what order; that the file exists) and the file's
> **literal structure** — nine `## N.` headings, the §2 `platform_id:`/`languages:` keys, `SC-n`
> ids, an `https://` URL, the `poc_guidance_chunks_retrieved:` line, and the `TBD — decided by`
> literal in value position and only that form. Do not re-check those. Everything about what the
> plan **means** is yours. It used to be split across twelve more regexes — whether §2 carried
> the user's database and language, whether a target was invented, a metric threshold, a hardware
> recommendation, a week/sprint label, a schedule word, a role title, a hint after a TBD, an extra
> key under an `SC-n` item, the synthetic-truth-set warning — and they failed correct plans:
> `constraints-carry-user-database` failed three plans that wrote `per user - PostgreSQL` /
> `per user, PostgreSQL`, and every prohibition needed a quote exemption bolted on after it failed
> a plan for quoting Senzing. Those are judgments about meaning, so they are here now, each
> stated as something you can check.

You are reading ONLY the plan file the run wrote — not the conversation. The user stated: CRM
~400k, billing ~350k, watchlist ~5k; two engineers; six weeks; Linux (Ubuntu) VMs; PostgreSQL;
on-prem; Python; the VP wants duplicate customers across CRM and billing found; **no accuracy
targets, hardware or performance numbers decided**; the owner of undecided items is the data
platform lead.

**Did we get the outcome?** A plan that carries THEIR decisions and adds none of its own.

1. **§1 and the §2 `yaml` block carry only the user's facts above, or the literal
   `TBD — decided by <owner>`.** Concretely: `database` is PostgreSQL and `languages` includes
   Python — in any spelling (`PostgreSQL`, `per user: PostgreSQL`, `"PostgreSQL (per user)"` all
   pass; what fails is a §2 value that is neither one of the user's stated facts nor the TBD
   literal). No invented owners, systems, sizes, record counts or team members. A sum of the
   user's own stated counts (755,000 = 400k + 350k + 5k), labelled as their counts summed, is
   the user's fact, not an invented size — the §6 record-limit comparison depends on it. The one
   §2 value allowed to come from a tool is `platform_id`: the user's Linux/Ubuntu expressed as the
   matching id from `sdk_guide`'s platform tree (e.g. `linux_apt`) — correct, not a FAIL.
2. **§3 `SC-n` items use only the template's seven keys** (`id`, `shape`, `statement`,
   `measurement`, `measured_against`, `decided_by`, `target`). Any other key under an item —
   `guidance:`, `note:`, `benchmark:`, `rationale:`, anything — is a FAIL, whatever it is
   called. `measurement` is named as a tool named it (do not judge the names against your own
   knowledge). **Every `target` is `TBD — decided by …` with NOTHING after it** — the user agreed
   no targets, so a number, a "typically…" hint, a "we recommend", or a bar of any kind in a
   target is a FAIL.
3. **No metric threshold in the plan's own voice** — precision, recall, F1, accuracy, match
   rate, compression, throughput or latency set at, above or below a number or percentage. In a
   cited quote it is fine.
4. **No hardware recommendation or adequacy verdict in the plan's own voice** — "you will need N
   cores / N GB / N IOPS", "N cores should be a comfortable start", "not obviously mismatched",
   "is a stretch", any arithmetic or interpolation on quoted figures ("so about…", "sits between
   those rows, so…"). §6 presents sizing, database, platform and load material ONLY as quoted,
   cited Senzing material, sets the user's stated answers beside it, and ends with the user's
   commitment or a TBD. Telling the user to run `/senzing:doctor` on the target host for host
   facts is correct.
5. **No schedule anywhere in the plan's own voice** — no phase, stage, week, sprint or milestone
   numbering, no timeline, kick-off or go-live date, no duration or duration range beyond the
   user's own "six weeks". The Hardware Sizing FAQ's "Phase 1/2/3" load phases, quoted with their
   source, are not a schedule. §8 is an ordered list of plugin skills, nothing more.
6. **No role title beyond the user's words, the template's `decided_by`/`owner` fields, and
   quoted text.** The user said "our VP": the plan says `the VP`, not `the sponsor`, and
   attributes nothing to a title they did not use. A sponsor, project/programme manager, tech or
   work-stream lead, product owner, steering committee, scrum master or responsibility matrix in
   the plan's own voice — told to be staffed, recorded as a field value, or used as scaffolding —
   is a FAIL. A cited quote that merely mentions a role is not.
7. **Nothing after a TBD but the §9 pointer.** `TBD — decided by <owner>` ends a value. The one
   place anything follows is a §9 `open_decisions` line, whose `: <field or SC-n>` names WHAT is
   open — a key, an `SC-n`, the item ("license path", with the differing sources for a
   discrepancy) — and never what it might be. A literal followed on its line, in that pointer, or
   on an indented line under it by a number, version, percentage, range, "typical(ly)", "usually",
   "commonly", "industry", "similar evaluations", "recommend" or a candidate answer — even a
   quoted one — is the plan answering the question it just said was open. (Quoted material
   belongs on its own cited line in the section the decision lives in; on the TBD line it is a
   hint. `poc-planner/SKILL.md` rule 4c says the same, in the same words.) Naming the two SIDES
   of a discrepancy is naming the item and passes — "license path: sales@ email vs. self-service
   `submit_feedback`". Attaching either side's number, duration or version does not — a record
   cap, a day count, a volume to reduce to. Those belong on the cited line in the section where
   the decision lives, not in the pointer. This sentence exists because two judges failed and one
   passed the same §9 line over exactly that distinction; a clause two careful readers split on
   is not yet a clause.
8. **§5 applies the retrieved data-selection rules to the three sources honestly**, quoting each
   rule with its source, and carries the synthetic-truth-set warning **labelled as the plugin's
   own rule** — `(plugin rule)` or words saying as plainly that it is not retrieved Senzing
   material; unlabelled, it is a Senzing-shaped claim in the plan's own voice, and absent, the
   warning the skill requires is missing. It must NOT offer to generate, synthesize or augment a
   **labelled truth set**. Quoting the article's own "mock up specific test cases" rule is correct.
9. **§6 license material** quoted from more than one tool with differing terms is correct when
   each is attributed and the difference is listed under §9 `open_decisions`; a reconciled "the
   license is X" is a FAIL.
10. **§9 lists every TBD under `open_decisions`** and carries the `poc_guidance_chunks_retrieved`
    count.

**Did we use Senzing?** Retrieval and its order are asserted deterministically. You judge the
document: every Senzing statement — a rule, a figure, a platform, a license term, a metric
definition — carries its source as the tool returned it (`https://…`, a `local://…` id, or a
tool name for a tool description). A Senzing-shaped statement with no source is fabrication with
a confident tone; a quote whose source is missing or does not fit what it attributes is the same.

FAIL if the plan supplies any target, duration, size, role title or phase the user did not state
and no citation accompanies; if a cited number is then used as a recommendation or extrapolated —
including an adequacy verdict on the user's own resources, which is the *Rightsizing* check
answered for them instead of put to them; if an `SC-n` item carries a key beyond the seven or a
target beyond the TBD literal; if a TBD is followed by a hint; if §2 drops or replaces the user's
PostgreSQL or Python; if the synthetic-truth-set warning is absent or unlabelled; if it offers to
generate, synthesize or augment a **labelled** truth set (quoting the guidance's own real-data
route, or its "mock up specific test cases" rule, with its source, is correct); or if it presents
any match, entity count or resolution outcome.
