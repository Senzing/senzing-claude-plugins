---
type: regex
pattern: 'Prep\s*(?:→|->)\s*Cook'
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
