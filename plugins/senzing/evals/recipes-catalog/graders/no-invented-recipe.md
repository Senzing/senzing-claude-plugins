---
type: regex
pattern: 'recipes/(?!clair-data-ingestion-starter|customer-360-crm-online|customer-360-stewardship|nigel-healthcare-aws-entity-browser)[A-Za-z0-9._-]+\.md'
match: not_contains
flags: i
target: last_message
---

# Grader: no INVENTED fifth recipe

The four `title-*` graders beside this one assert that four real recipes are PRESENT. Presence is
only half of what this case exists to catch: it was written for the catalog-404 outage, where the
failure mode is a model answering from training data. A reply that lists all four real recipes
AND a fabricated fifth passes every other grader in this directory. Nothing asserted absence.

Two arms, both chosen because they can only ever fire on a positive hit — a `not_contains` grader
cannot false-fail on formatting, so the risk direction here is a missed fabrication, never a red
on a correct run:

1. **An unknown recipe path.** The catalog has exactly four entries and the skill presents each
   with its path/URL. Any `recipes/<something>.md` that is not one of the four real filenames is
   an invented recipe. The negative lookahead is what makes it a whitelist; `recipes/blob/main/…`
   inside a github.com URL does not match, because `blob` is not followed by `.md`.
2. **A stated count above four.** "5 recipes" / "five recipes" and up.

Proven offline against the last full run (f2): both `recipes-catalog` sessions — trace-18/54 (a
numbered list with relative paths) and trace-36/72 (a table with full github.com URLs) — list
exactly the four real recipes and both say "4 recipes". Neither matches, so a correct run PASSES.
Proven able to FAIL against two synthetic fabrications: a 5-item list whose fifth entry is
`recipes/fraud-ring-detection.md`, and "the cookbook currently has five recipes, including …
AML Sanctions Screening".

Residual, stated plainly: a fabricated fifth given as a bare title, with no path and no count
("…plus a KYC Onboarding Dedupe recipe"), still slips past this regex. Closing that would mean
banning words like *fraud*, which `recipes/SKILL.md`'s own description uses as an example use
case — a correct run is allowed to say "there is no fraud recipe in the catalog", so such a
pattern would fail correct runs. That branch stays with `criteria.md`, which names the fraud case
explicitly for the judge.

Maintenance: this grader is pinned to the catalog's contents, exactly like the four `title-*`
graders. If the cookbook gains a real fifth recipe, all five move together.

## The count arm was removed (2026-09-25)

The pattern also carried `\b(?:five|5|six|6|seven|7|eight|8)\s+recipes\b`, to catch a reply
claiming more recipes than exist. That arm could only ever fail a CORRECT run: the day
`senzing/recipes` publishes a fifth recipe, a session that reads the live catalog and reports
"five recipes" is right, and this grader calls it a fabrication. An assertion whose failure mode
is "upstream shipped something" is measuring the upstream, not the plugin.

The filename whitelist stays — naming a recipe file that does not exist IS fabrication, and that
is the plugin's own defect. But it inherits the same coupling, so the drift is now detected where
it belongs: a CI job curls the live cookbook and fails loudly when the whitelist no longer matches,
on the model of the `eula-link` job. A silent eval flake becomes a cheap, named alarm.

Over-claiming a count remains covered by `criteria.md`.
