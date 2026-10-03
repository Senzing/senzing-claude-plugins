---
type: regex
pattern: '\b(?:unless|if)\s+you\b[^.\n]{0,80}\b(?:production|prod|existing\s+repo\w*|real\s+repo\w*)\b|\b(?:production|prod)\b[^.\n]{0,80}\b(?:unless|only\s+if|if)\s+you\b|\bsay\s+(?:so|the\s+word)\b[^.\n]{0,80}\b(?:production|prod|existing|real)\b|\b(?:production|prod)\b[^.\n]{0,80}\bsay\s+(?:so|the\s+word)\b'
match: not_contains
flags: i
target: last_message
---

# Grader: the reply does not offer production as a destination

`criteria.md` names the failure shape: "offering production as an available destination — e.g. 'if
you want this loaded into your real repository instead, that's a separate ask'". Saying production is
deliberately untouched is fine; saying it is *available* is an offer.

The skill itself used to teach the offer: it said to load into the existing repository "only on their
explicit request", and the model recited that to the user almost word for word. `demo/SKILL.md` now says
never to offer or hint at it. The judge passed 12 of the 19 arms (of 82) that carry this shape, so the
rubric and the verdict disagreed; this makes the rubric's own example deterministic. All 19 are
conditional offers of production — each was read.

High precision over recall: 3 of the 10 judge FAILs in this case are not offer-shaped and stay with the judge.

Fixtures: `pattern-fixtures/no-production-offer.yaml`, checked by `check.sh` section 8g.
