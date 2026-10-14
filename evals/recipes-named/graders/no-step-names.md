---
type: regex
pattern: 'Prep\s*(?:→|->)\s*(?:Cook|Plate|Plus)'
match: not_contains
flags: i
target: last_message
---

# Grader: the reply does not name the recipe's Prep → Cook steps

On a host that cannot cook, `recipes/SKILL.md` hands off to `install` and the reply is install's message, nothing
more. A post-merge run (CI run 37938113230) appended "...and only then resume the recipe's Prep → Cook → Plate
steps" to install's message: the judge (`criteria`) failed it 3 of 3, and `no-cook-promise` missed it because it
matches an "I'll install ... then cook" chain, not a bare mention of the steps. Naming the steps in the reply is the
announcement `criteria` forbids, so this is a deterministic backstop for that one phrase, not a new rule.

Fixtures: `pattern-fixtures/no-step-names.yaml`.

PR #72 (v1.38.2) eval: a run put "the recipe's full Prep→Plate flow is reachable here once Senzing is
installed" ahead of install's message — `criteria` failed it 3 of 3 and this pattern, then `Prep → Cook` only,
missed it. Any `Prep →` step chain is the same announcement, so the pattern now covers Cook, Plate and Plus.
