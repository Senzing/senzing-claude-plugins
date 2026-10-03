---
type: regex
pattern: '\b(?:true|success|bar|hard\s+number|buy|adopt|purchase|decide|convince|yes|closest|something\s+else|compare|worked|believe)\b[^\n]{0,300}\?|\?[^\n]{0,300}\b(?:true|success|bar|hard\s+number|buy|adopt|purchase|decide|convince|yes|closest|something\s+else|compare|worked|believe)\b'
flags: i
target: last_message
---

# Grader: the buy decision is ASKED, in the reply's questions

Round 1 block (4): what would have to be true for the organization to buy. Any question-line that names success / the bar / the buy decision / what it would be compared against. Deliberately broad: a reply that asks the block differently ("does anyone already hold a hard number or bar for this?") must pass, so this catches only a reply that never asks about it at all, and the open-vs-closed-choice nuance stays unchecked here.

This was a judge clause (`judge-buy-decision-open`). Measured on 82 real final messages: 0 misses; a declarative plan with no `?` does not hit.
