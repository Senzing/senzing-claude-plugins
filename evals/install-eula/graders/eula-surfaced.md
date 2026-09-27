---
type: regex
pattern: 'senzing\.com/end-user-license-agreement'
flags: i
target: last_message
---

# Grader: the EULA is surfaced BY ITS LIVE URL, not by the word "EULA"

This was an alternation of the words EULA / license agreement / end user license — it matched
the WORD. The defect class
that actually shipped is a dead link, not a missing noun: MCP server v1.36.1 fixed five
occurrences of `senzing.com/senzing-eula`, which 404s, and every one of them sat in a sentence
saying "review the EULA". The old pattern passes that reply untouched, so the one thing the user
has to be able to open was the one thing nothing asserted.

Asserting the canonical path is what makes the grader bite: `senzing.com/senzing-eula` does not
contain `end-user-license-agreement`, so the shipped-defect reply now fails here.

Provably able to PASS a correct run: both `install-eula` sessions in the last full run (f2) ended
with it — trace-14/50 `https://senzing.com/end-user-license-agreement/.` and trace-26/62
`https://senzing.com/end-user-license-agreement.`. The pattern deliberately stops before the
trailing slash so both spellings match. Provably able to FAIL: the same replies with the
v1.36.1 URL substituted, and any reply that names the EULA without a link, do not match.

The URL's LIVENESS is checked separately, by the `eula-link` job in `.github/workflows/ci.yml` —
a grader can only assert what the reply says, never whether the page still exists.
