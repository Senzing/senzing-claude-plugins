---
type: regex
pattern: '\brecords?\b[^?\n]{0,160}\?'
flags: i
target: last_message
---

# Grader: the data block is ASKED, as a question

Round 1 block (1): what the data is, where it lives, who owns it, **how many records** — as a sentence ending in `?`. Split out of the single `criteria` judge on 2026-10-03: it bundled seven obligations in one verdict, so a FAIL named none of them (`explanation` is just `judge votes: FAIL FAIL FAIL`).

Measured on 82 real final messages of this case: 82 of 82 hit, so it cannot fail a correct run. A block that is only stated declaratively ("we will profile your records") has no `?` and is the miss it exists to catch.

**What this can and cannot catch.** It fires only on a reply with no question line naming the word `records`: a block that is
absent or only stated in a declarative plan. It cannot tell a reply that asks the block well from one that merely has
some question near those words, so "0 misses in 82 real replies" shows it will not fail a correct reply, not that it
detects every omission. Reading *how well* a block is asked stays unchecked here.
