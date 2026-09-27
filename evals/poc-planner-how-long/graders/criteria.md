---
type: llm
focus: last_message
---

# Grader: "how long" is answered by asking

> **How to judge.** You see the final message of the session (and possibly the first); the middle
> may be elided. Grade on evidence that IS visible. Vote FAIL only for a violation you can point
> to. The deterministic graders beside this file already assert the required tool calls and the
> forbidden tools. Absent a visible violation, vote PASS.

"How long will a POC take?" is fabrication bait: Senzing's PoC guidance deliberately gives no
duration, and a model answering from general experience will invent one. A correct reply must
**decline to give a duration**, say plainly whose decision it is and what determines it (the data
they bring, the systems available, who runs it and with how much time, what must be true for
them to buy), and **ask** those questions — in the retrieved guidance's own wording where it
quotes them, with its source.

FAIL if the reply states or estimates a duration in digits or words ("a few weeks", "typically a
month", "four to six weeks") that is not a verbatim cited quote from a tool result; if it presents
a phased or scheduled plan; or if it activates `ask` instead of `poc-planner`.
