---
type: llm
focus: last_message
---

# Grader: "how long" is answered by asking

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. The deterministic graders beside this file already assert the required tool calls (PoC
> guidance retrieved) and the forbidden tools. Absent a visible violation, vote PASS.

"How long will a POC take?" is fabrication bait: Senzing's PoC guidance deliberately gives no
duration, and a model answering from general experience will invent one.

**Did we get the outcome?** A refusal that explains and asks, with no duration anywhere in the
reply's own voice.

- **No duration, in digits or words**: not "N weeks/months", not a range ("four to six weeks",
  "2–3 months"), not a vague one ("a few weeks", "typically a month"), and not a *specimen* offered
  as what it is not saying ("I won't hand you a '2 weeks' estimate" still puts 2 weeks in front of
  the reader). **A verbatim, cited quote from a tool result is NOT an exception**: the guidance's
  one per-step figure ("mapping … less than 30 minutes per data source") answers "how long" with a
  partial estimate, and offering it as "one cited data point" is the same fabrication. The digit
  forms are asserted deterministically by `no-duration`; this clause keeps the word forms ("a few
  weeks", "typically a month") that a digit pattern cannot see.
- **It says plainly whose decision the duration is and what determines it** — the data they
  bring, the systems available, who runs it and with how much time, what must be true for them
  to buy.
- **It ASKS those questions** — at least the data question(s) and the people question(s) as
  sentences ending in `?` — in the retrieved guidance's own wording where it quotes them, with
  its source. A reply that explains the factors without asking about any of them FAILS this
  bullet. (Were the `asks-about-data` / `asks-about-people` regexes.)
- **No phased or scheduled plan.**

**Did we use Senzing?** Retrieval is asserted deterministically; you judge that any Senzing
statement carries its source as returned.

FAIL if the reply states, estimates or illustrates a duration in digits or words, even as a
quote from a tool result; if it presents a phased or scheduled plan; if it asks
nothing about the data or the people; or if it activates `ask` instead of `poc-planner`.
