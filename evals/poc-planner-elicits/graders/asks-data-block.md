---
type: regex
pattern: '\brecords?\b[^?\n]{0,160}\?'
flags: i
target: last_message
---

# Grader: the data block is ASKED, as a question

Round 1 block (1): what the data is, where it lives, who owns it, **how many records** — as a sentence ending in `?`. Split out of the single `criteria` judge on 2026-10-03: it bundled seven obligations in one verdict, so a FAIL named none of them (`explanation` is just `judge votes: FAIL FAIL FAIL`).

Measured on 82 real final messages of this case: 82 of 82 hit, so it cannot fail a correct run. A block that is only stated declaratively ("we will profile your records") has no `?` and is the miss it exists to catch.
