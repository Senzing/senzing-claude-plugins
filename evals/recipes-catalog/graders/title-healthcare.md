---
type: regex
pattern: "Healthcare Exclusion"
target: last_message
---

# Grader: the compliance recipe is named from the real catalog

Verified against the live `cookbook.md`: "Healthcare Exclusion Screening" is the real compliance
entry — note there is currently NO "fraud" recipe in the catalog even though the `recipes`
SKILL.md's own description names "fraud" as an example use case. A run that invents a fraud
recipe to satisfy that description text would fail this grader's sibling checks and is exactly
the fabrication class this case exists to catch. Proven offline against the hallucinated
fraud/AML/KYC reply — no match.
