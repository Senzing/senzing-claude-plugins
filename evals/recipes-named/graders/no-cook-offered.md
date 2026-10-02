---
type: regex
pattern: '\bsampl\w*\s+(just|only)\s+\d[\d,]*\s+records|\b(just|only)\s+\d[\d,]*\s+of\s+(your|their)\s+records|\bwhen we (get|move) to the \w+ step|\bhave it ready to (attach|drop)'
match: not_contains
flags: i
target: last_message
---

# Grader: the cook is not offered on a host that cannot cook

`recipes/SKILL.md` is explicit that offering counts as doing: "mapping the ingredients,
scaffolding the loader, or writing plan files **is** the Cook step — do not do it here, and do
not offer it as an option either. Ending on 'which would you like?' over a choice that includes
the forbidden act is the same violation as performing it." This case runs on a host with **no
SDK**, so there is nothing to cook with.

**The absence assertion is `match: not_contains`, not `min`/`max`.** Those bounds belong to
`tool_used` graders, which count calls; a `regex` grader rejects them outright and the harness
fails the WHOLE case to load — `graders.6: Unrecognized key(s) in object: 'min', 'max'`, which
reports as `cases run=17 expected=18`, a structural exit 2, not a grader failure. It cost one
full eval run on 2026-10-02. `check.sh` section 8d now catches that shape offline.

## Why this is a regex and not left to the judge

The `criteria` judge already forbids this, and scored it 0.50 on 2026-10-02 — the judge was
**unanimous 3-0 in opposite directions across two runs of identical deterministic behavior**.
Every `tool_used`/`tool_order`/`file_exists` grader was green in both; the entire delta was the
final paragraph, which in one run offered to "sample just 500 records" and stage a license file
"when we get to the Prep step" on a machine with no Senzing.

A boolean obligation the suite honours half the time is a defect, not a 0.5 — and a judge verdict
carries no reasoning in the artifact (`explanation` is literally `"judge votes: FAIL FAIL FAIL"`),
so it cannot be gated on. The known surface forms are matchable, so they are matched here and
gate deterministically. The judge clause stays for novel phrasings this pattern does not know.

## What separates an offer from a statement of fact

The skill REQUIRES describing what the recipe needs, so "the unlicensed tier will load only 500
records" must stay clean while "I could load only 500 of your records" must not. A verb list
alone cannot tell them apart -- an earlier revision of this pattern keyed on a list of
stemmed verbs and got BOTH wrong: it flagged that factual sentence, and it MISSED the
server's own wording, "continue with just 500 of their records as a sample", because the word
before `just` is "with". A grader that cannot match the text it exists to catch is worse than
no grader.

The discriminator is possession. An offer either uses an offer verb outright (`sample just N
records`) or speaks of **your/their** records -- it is about the user's data. A statement about
the product's cap does neither. Hence two alternatives, not a verb list.

## The pattern was fitted to real traces, not invented

Validated against both runs of eval run `37016809063`: **0 hits** on the passing run's final
message, **3** on the failing run's (`have it ready to attach`, `when we get to the Prep step`,
`sample just 500 records`). Checked against legitimate prose it must NOT catch — describing the
recipe's ~1,600-record size, quoting the 500-record unlicensed cap, naming the Setup step, or
saying the Prep step is where mapping happens all stay clean. Describing what the recipe *needs*
is required by the skill; offering to *do* part of it is the violation.

## Root cause, fixed on the server side

The model did not invent the offer — `sdk_guide(topic=install)` instructed it, verbatim: "If no
license is available, offer three options: (1) continue with just 500 of their records as a
sample ...". That text assumes a load is imminent and fired while merely explaining an install.
Fixed in `sz-mcp-coworker` by gating all four occurrences on "records are about to be loaded on a
working Senzing install", pinned by `quality_sdk_guide_sample_offer_requires_imminent_load`.
This grader is the plugin-side half: it catches the behavior whatever its future cause.
