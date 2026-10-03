---
type: regex
pattern: '\blanguage\b[^?\n]{0,120}\?'
flags: i
target: last_message
---

# Grader: the SDK-language block is ASKED, as a question

Round 1 block (3): who runs it and **which SDK language** — as a sentence ending in `?`. Split out of the single `criteria` judge on 2026-10-03: it bundled seven obligations in one verdict, so a FAIL named none of them (`explanation` is just `judge votes: FAIL FAIL FAIL`).

Measured: 82 of 82 real final messages hit; 0 false fails.

**What this can and cannot catch.** It fires only on a reply with no question line naming the word `language`: a block that is
absent or only stated in a declarative plan. It cannot tell a reply that asks the block well from one that merely has
some question near those words, so "0 misses in 82 real replies" shows it will not fail a correct reply, not that it
detects every omission. Reading *how well* a block is asked stays unchecked here.
