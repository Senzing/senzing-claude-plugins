---
type: regex
pattern: "\\b(?:buy|purchase|decisions?|decide|success|criteri(?:on|a)|must be true|what would)\\b[^?!.]{0,200}\\?|\\?[^?!.]{0,200}\\b(?:buy|purchase|decisions?|decide|success|criteri(?:on|a)|must be true|what would)\\b"
flags: i
target: last_message
---

# Grader: the reply ASKS about the buy decision

Was a single common-word regex (``\\b(buy|decision|decide|success|must be true|what would)\\b``) over `last_message` with no `match:` — presence only. No
competent reply to this prompt lacks those words, so the grader could not fail; it was an
incidental pass riding on `criteria.md` doing the real work. That is the whole point of this case:
`expected_outcome` says the run "ENDS at the questions", and a reply that answers with a plan
instead of asking uses the same vocabulary.

So the assertion is now the thing that can actually be absent: a **question mark in the same
sentence as the topic**. `[^?!.]{0,200}` cannot cross a sentence terminator, so a declarative
plan that merely mentions the buy decision does not satisfy it; only a clause that asks does. The second
alternative accepts the reverse order — a question stem followed by its topic, which is how a
bulleted Round 1 block reads ("What are you bringing?\n- CRM export, billing extract") — so
correct phrasing is not failed on word order.

It fails on the run this case exists to catch: a reply with no questions in it scores zero matches.
Whether all four Round 1 blocks are present, and whether they are asked rather than assumed, stays
with `criteria.md`.
