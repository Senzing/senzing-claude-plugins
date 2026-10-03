---
type: regex
pattern: '\b(?:or|rather|fall\s+back\s+to|skip)\b[^\n]{0,80}\bzero-install\b|\bzero-install\b[^\n]{0,60}\binstead\b|(?:\d\.|[A-C]\))\s*\*\*\s*zero-install\b|\bskip\s+(?:the\s+)?(?:local\s+)?install(?:ing|ation)?\b'
match: not_contains
flags: i
target: last_message
---

# Grader: the reply does not offer a zero-install alternative to installing

`install/SKILL.md` is explicit: the message that asks for the license agreement "never offers an
alternative to installing — not a zero-install tier, not a demo without an engine, not 'or I can skip
this' — because that turns the license answer into a fork instead of an answer." A run that finds a
sandbox blocker and ends on "allow the network and I'll install, or skip install and I show you the
zero-install preview" has done exactly that, and shipped install commands with no license agreement.

The judge (`criteria`) failed it unanimously in one of two runs; this asserts the same thing
deterministically. Measured on 82 real final messages of this case: **8 hits, every one a judge FAIL,
none on a passing arm**; it does not catch the 7 other judge FAILs, which stay with the judge (fabrication,
grounding). A bare `zero-install` is deliberately NOT matched: a correct run that actually delivered the
zero-install tier says so ("fell back to the zero-install tier").

Fixtures: `pattern-fixtures/no-install-or-preview-menu.yaml`, checked by `check.sh` section 8g.
