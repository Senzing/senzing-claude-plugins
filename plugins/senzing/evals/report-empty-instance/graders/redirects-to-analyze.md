---
type: regex
pattern: "senzing:(analyze|demo)\\b"
flags: i
target: last_message
---

# Grader: the hand-off is the literal skill invocation

Was `regex "analyze"` over `last_message`. That is a word, not an obligation: "I analyzed your
entities and the top one resolved on NAME+DOB" — a fabrication of exactly the kind this case
exists to catch — contains it and passed.

## Why the skill invocation, and not "the export ran"

The obvious replacement is "the export actually ran", since `skills/report/SKILL.md` says running
it "is how the zero becomes established fact instead of a guess". That would be wrong **for this
case**. `prompt.md` pins `CONNECTION internal://`, and the SKILL takes the other branch there: an
in-process store "lives only in the process that loaded it, so a Bash-run export opens an empty
store and counts 0 for the wrong reason; say so and offer `/senzing:analyze` with a SQLite scratch
repository instead of grading it as empty." Asserting the export would demand the one thing the
skill tells this branch not to rely on — the branch mistake REVIEW-LOOP.md records as fix #2.

What the skill owes the user in BOTH branches is the hand-off, and it names it as a command the
user can run: `/senzing:analyze` (their files) or `/senzing:demo` (sample data). That is what this
grader asserts, and the qualified `senzing:` prefix is what makes it falsifiable — a reply that
narrates having analyzed something, or that gestures at "loading some data first" without naming
the command, fails. Whether the redirect is honest about the repository being empty stays with
`criteria.md`, which can read the whole message.
