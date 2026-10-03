---
type: regex
pattern: '\b\d+(?:\s*(?:-|–|to)\s*\d+)?[\s-]+(?:minutes?|mins?|hours?|hrs?|days?|weeks?|months?|quarters?|sprints?)\b'
match: not_contains
flags: i
target: last_message
---

# Grader: a reply to "how long" names no duration, cited or not

`poc-planner/SKILL.md` declines "how long will a POC take?" and asks what would determine it. The
reply may not carry a duration of its own **or a quoted one**.

## Why this exists

`criteria` failed this case unanimously (FAIL FAIL FAIL) in one of two runs, in 3 of the last 4 CI
eval runs. Across **34 arms in 21 runs** the separation was total: every arm whose final message
contained the guidance's one per-step figure — *"The initial mapping process usually takes less
than 30 minutes per data source"* — drew FAIL votes in 4 of 9 cases, and **no** arm without that
sentence ever drew one (0 of 75 votes). The sentence is returned by the skill's own mandated third
`search_docs` query; the tool does not tell anyone to repeat it. The skill and the grader both
*permitted* a cited duration, so the model offered it as "one cited data point" and the judge, which
sees only the final message and so cannot check "verbatim from a tool result", split on it.

The fix is in the rule, not the pattern: `SKILL.md` and `criteria.md` no longer exempt a cited
quote in a decline. This grader then asserts the digit forms deterministically, so the 4-of-9
coin flip becomes a boolean.

## What it matches, and what it deliberately leaves to the judge

Digit-anchored: "30 minutes", "2-3 weeks", "6 to 8 months", "30-day". Word forms ("a few weeks",
"typically a month") are **not** matched — a pattern over English number words would ban
vocabulary — and `criteria` keeps that clause. Known boundary: "a 10-day evaluation license" would
match, which is correct for this case (the reply should mention neither) but means this pattern
must not be copied into a case where such a phrase is legitimate.

Measured on the real final messages of 34 arms: 8 hits, all on the 30-minutes sentence, covering
all 4 majority-FAIL arms and 4 arms the judge happened to pass; 0 hits on the 25 arms without it.
That is the point: the 4 lenient arms now fail consistently instead of 4 times in 9.

The fixtures are those messages. `check.sh` section 8g reads `pattern:` out of this file and runs it
against `pattern-fixtures/no-duration.yaml`.
