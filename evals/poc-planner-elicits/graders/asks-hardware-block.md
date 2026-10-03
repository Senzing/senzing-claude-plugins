---
type: regex
pattern: '\b(?:hardware|infrastructure|cores?|RAM|memory|VMs?|servers?|cloud|on-?prem\w*|platform|operating\s+system|OS|database|machines?|compute|system\s+resources?|bare\s+metal|docker)\b[^\n]{0,300}\?|\?[^\n]{0,300}\b(?:hardware|infrastructure|cores?|RAM|memory|VMs?|servers?|cloud|on-?prem\w*|platform|operating\s+system|OS|database|machines?|compute|system\s+resources?|bare\s+metal|docker)\b'
flags: i
target: last_message
---

# Grader: the infrastructure block is ASKED, as a question

Round 1 block (2): hardware available, platform/OS, database, cloud or on-prem — a sentence ending in `?` that names the topic, in either order within the line (a reply asked "What system resources are quickly available? (Database, OS, cloud vs. on-prem)" with the keywords AFTER the `?`; the first version of this pattern required them before and false-failed it).

This was a judge clause (`judge-hardware-asked`). Measured on 82 real final messages: 0 misses, and a declarative plan with no `?` does not hit, so it still catches the defect it exists for.

**What this can and cannot catch.** It fires only on a reply with no question line naming hardware/platform/database words: a block that is
absent or only stated in a declarative plan. It cannot tell a reply that asks the block well from one that merely has
some question near those words, so "0 misses in 82 real replies" shows it will not fail a correct reply, not that it
detects every omission. Reading *how well* a block is asked stays unchecked here.
