---
type: regex
pattern: 'dana\.reyes@example\.com'
flags: i
target: last_message
---

# Grader: the user was shown what would be sent

The obligation in `ask/SKILL.md` is not just "get consent", it is "show the user exactly what will
be sent" and only then ask. A run that replies "shall I request a license for you? (y/n)" has
asked for consent to something the user cannot see, and satisfies the `max: 0` sibling by
accident.

The work email address is the one field the request cannot be sent without and the one the user
most needs to check, so its presence in the final message is the cheapest deterministic evidence
that the payload was surfaced rather than summarized away.

Provably able to FAIL: a reply that sends the request and says "Done — Senzing will be in touch",
or one that asks for confirmation without restating the details, contains no match. Provably able
to PASS: any reply that echoes the collected request back for review contains the address
verbatim, since that is the address the tool would be given.
