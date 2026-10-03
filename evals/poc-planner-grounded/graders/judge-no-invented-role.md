---
type: llm
focus: { source: file, path: senzing-poc-plan.md }
---

# Grader: no role title beyond the user's words, the template's fields and quoted text

> **Shared preamble — repeated word-for-word in every `judge-*.md` grader of this case, on
> purpose.** Until 2026-10-01 these clauses were one `criteria.md`, judged over a ~20,000-character
> plan; a FAIL reported all of them at once and each diagnosis cost a manual re-judge. They are
> now one grader per clause so a FAIL names the clause. Each file carries this whole preamble
> because the quoted-with-source exemption below is what keeps a CORRECT plan from failing: a
> judge shown one clause without it fails plans for quoting Senzing. Edit the preamble in every
> `judge-*.md` together — `scripts/check-poc-graders.py` fails if they drift apart.
>
> **How to judge.** You see ONLY `senzing-poc-plan.md`. Vote FAIL only for a sentence you can
> point to that the plan asserts **in its own voice**. Text inside a verbatim quotation carrying
> its source on the same line is the plan doing exactly what it was told — everywhere in this
> document, not only in §6: a quoted threshold, a quoted "Phase 1/2/3", a quoted duration, a
> quoted "N cores / N GB / N IOPS", a quoted sentence that mentions an executive sponsor is never
> a FAIL, and the same shape asserted in the plan's own voice always is — with one placement
> exception, the TBD clause (`judge-nothing-after-tbd.md`): a quote on a TBD line, after the
> owner, is a hint. Quotation marks alone are not a citation: a YAML scalar in double quotes
> with no source (`people: "per user: two engineers; project sponsor: the VP"`) is the plan's
> own voice.
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
> a plan for quoting Senzing. Those are judgments about meaning, so they are judge clauses now —
> one per `judge-*.md` grader beside this file, each stated as something you can check.

You are reading ONLY the plan file the run wrote — not the conversation. The user stated: CRM
~400k, billing ~350k, watchlist ~5k; two engineers; six weeks; Linux (Ubuntu) VMs; PostgreSQL;
on-prem; Python; the VP wants duplicate customers across CRM and billing found; **no accuracy
targets, hardware or performance numbers decided**; the owner of undecided items is the data
platform lead.

**Did we get the outcome?** A plan that carries THEIR decisions and adds none of its own. That
question is split across the `judge-*.md` graders beside this file; **this grader owns ONE clause
and votes on nothing else.** A violation of a different clause is a different grader's FAIL, not
this one's — do not vote FAIL here for it, and do not vote PASS here because the rest of the plan
is good.

## This grader's clause (clause 6 of the former `criteria.md`)

**No role title beyond the user's words, the template's `decided_by`/`owner` fields, and
quoted text.** The user said "our VP": the plan says `the VP`, not `the sponsor`, and
attributes nothing to a title they did not use. A sponsor, project/programme manager, tech or
work-stream lead, product owner, steering committee, scrum master or responsibility matrix in
the plan's own voice — told to be staffed, recorded as a field value, or used as scaffolding —
is a FAIL. A cited quote that merely mentions a role is not.

FAIL if the plan supplies any role title the user did not state and no citation accompanies. Absent
a visible violation of THIS clause, vote PASS.

---

*About this file.* It is one of eleven judge clauses that replaced the single `criteria.md` of
this case on 2026-10-01 (restructure, not rewrite: the obligation above is the former clause's
text, with its numeric cross-references resolved so the file stands alone). The `judge-` prefix
says this is an `llm` clause, and keeps the name clear of the `regex` graders beside it, which
are named for what they assert too (`tbd-only-in-literal-form`, `nine-template-sections`) and
whose retired siblings (`no-metric-thresholds`, `sc-items-closed-keys`, …) carried these same
assertions as regexes until 2026-09-29. The eleven:

| file | clause |
|---|---|
| `judge-constraints-are-the-users.md` | §1 and §2 carry only the user's facts or the TBD literal |
| `judge-no-metric-threshold.md` | no metric threshold in the plan's own voice |
| `judge-no-hardware-verdict.md` | no hardware recommendation or adequacy verdict in the plan's own voice |
| `judge-no-schedule.md` | no schedule anywhere in the plan's own voice |
| `judge-no-invented-role.md` | no role title beyond the user's words, the template's fields and quoted text |
| `judge-nothing-after-tbd.md` | nothing follows a TBD but the §9 pointer |
| `judge-truth-set-warning-labelled.md` | §5 applies the data-selection rules honestly and labels the synthetic-truth-set warning |
| `judge-license-terms-not-reconciled.md` | §6 license terms are quoted per tool, never reconciled |
| `judge-open-decisions-complete.md` | §9 lists every TBD and carries the provenance count |
| `judge-senzing-statements-sourced.md` | every Senzing statement carries the source the tool returned |
| `judge-no-resolution-outcome.md` | no match, entity count or resolution outcome is presented |
