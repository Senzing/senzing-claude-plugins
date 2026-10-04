---
type: regex
pattern: '\b(?:once|after|when)\s+I\s+have\s+(?:those|that|these|them|your\s+(?:answers?|input|go-ahead))\b[^\n]{0,60}\bI[''’]?ll\s+(?:install|stand\s+up|set\s+up)\b[^\n]{0,200}\bthen\s+(?:I[''’]?ll\s+)?cook\b|\bI[''’]?ll\s+(?:install|stand\s+up|set\s+up)\b[^\n.]{0,160}\bthen\s+(?:I[''’]?ll\s+)?cook\b'
match: not_contains
flags: i
target: last_message
---

# Grader: the reply does not promise to install AND cook in one breath

`recipes/SKILL.md` says to hand off to `install` and stop on a host that cannot cook. A run ended with a menu of
Cook-step questions (license agreement, language, license file or evaluation license) and the promise *"Once I have
those, I'll install Senzing + Java, stand up a local instance, then cook the recipe's Prep → Cook → Plate → Plus
steps (map/load CRM…)"*. The judge failed it 9 of 9 on replay (its passing control 9 of 9 PASS), so this one is a real
behavioral difference, not noise: the reply proposes the cook and did the install flow inline instead of handing off.

**Narrow on purpose.** It needs *I'll install / stand up / set up … then cook* in one chain. A reply that hands the
install to the user and says it will "pick up from there — re-run doctor, then cook the recipe" is the expected resume
and passes (a judge-passing real reply says exactly that). Measured on 14 real `recipes-named` replies: **1 hit, the
judge-FAIL arm**. The broader class ("proposes any part of the cook") stays with `criteria`, which is enforced.

Fixtures: `pattern-fixtures/no-cook-promise.yaml`; `check.sh` 8g.
