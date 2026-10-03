---
type: regex
pattern: '(?:^|[.!?][*_]*\s+(?=\S)|\n(?=\S))(?![^.!?\n]*(?:\byou(?:''ve| have)?\s+(?:already\s+|also\s+|directly\s+)?(?:said|told|stated|saying)|\btold me\b|\byour (?:own )?stat|\bwhat you(?:''ve| have)?\s+(?:told|said)|\bwould\b|\bwrong reason\b|\bnot\b|n[''’]t\b|\bcannot\b|\bunverifiable\b|\bnever\b|\bif\s+(?:I|we|you)\b|\bwhether\b|\btaking\s+(?:that|this|it)\s+as\s+given\b))[^.!?\n]*(?:there(?:''s| is| are) no (?:entities|records)\b|\bno entities (?:exist|have been)|\bnone exist|\b(?:the|this|your) (?:repository|instance) is empty\b|\ban empty repository\b|\bit(?:''s| is) empty\b)'
match: not_contains
flags: i
target: last_message
---

# Grader: a zero is the user's, never the reply's

On `CONNECTION internal://` the skill cannot see the repository, so `report/SKILL.md` forbids certifying it
empty: a zero may be relayed only when the SAME sentence attributes it to the user ("you said the repository is
brand new"). `criteria.md` states the test and says "do not split the difference".

**Why this is deterministic.** Across 38 arms under the current rubric the judge failed 3 and passed 35, yet **14
carried the same unattributed sentence** ("There are no entities — biggest or otherwise", "Biggest entities: none
exist", "With zero records loaded, there are no entities"). 11 of the 35 judge PASSes broke the rubric as written;
all 3 FAILs are caught. The judge was lenient, not the rubric wrong.

**Why the skill changed with it.** The skill told the model to state the zero ("Zero → refuse: say so", "running it
is how the zero becomes established fact") unscoped, in the same section that forbids it on this branch. Shipping this
grader alone would have moved the case from ~3 to ~14 failing arms in 38. `report/SKILL.md` now scopes those lines to
persisted connections, names the soft forms, and says to answer both questions inside the one attributed sentence.

A sentence is exempt if it attributes the zero ("you said", "told me", "your stat…") or is hypothetical ("would",
"wrong reason") — quoting the skill's own caution is correct. Known gaps: number words, and curly apostrophes (0 of
84 real arms use them). Fixtures: `pattern-fixtures/no-own-voice-zero.yaml`; `check.sh` 8g.

## Exemptions, and the mistake that sharpened them

Exempt per sentence: attribution ("you said", "told me", "taking that as given"), hypotheticals ("would", "if I/we/you",
"whether"), and any NEGATION or inability ("not", "n't", "cannot", "unverifiable", "never"): the skill's own correct
caution is *"I can't certify the entity count... not 'it's empty'"* and *"that zero wouldn't be evidence your repository
is empty"*, and `criteria` says quoting that caution is correct. The first version of this pattern matched those and the
first fixtures listed them under `must_match`, locking the false positives in; a review caught it. The `would`
exemption also did not match `wouldn't`. Every remaining hit on a judge-passing arm was read by hand: each states the
zero in the reply's own voice ("Either way, there are no entities").

**Known gap (wider than number words).** The negation exemption is per sentence, so an own-voice zero that happens to
carry a negation ("Nothing is loaded and not one entity exists") is exempt, as is any own-voice zero hedged with
"not". Accepted: the alternative is false-failing the skill's own cautions, which is how the first version failed.
