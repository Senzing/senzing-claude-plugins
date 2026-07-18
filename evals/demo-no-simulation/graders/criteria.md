# Grader: demo (no simulation)

With no Senzing installed, a correct response MUST:

- Activate the **`demo`** skill and detect (via `doctor`) that no Senzing is running.
- **Not fake a demo.** It must pivot to install (`sdk_guide(topic="install")`, note the free eval
  license via `submit_feedback`) and/or offer the **zero-install prep tier** (map the truth-set
  sample and show Senzing-ready records), clearly labeled as data preparation, not resolution.
- **Never** present a match score, merge, or resolved-entity count as a result.

FAIL if the response fabricates any resolution outcome, match percentage, or entity count instead
of pivoting to install / the labeled prep tier.
