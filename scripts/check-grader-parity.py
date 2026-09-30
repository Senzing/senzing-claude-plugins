#!/usr/bin/env python3
"""Offline parity check: does each skill pin what its surviving regex graders demand?

The suite grades two kinds of thing. FACTS ABOUT THE TRACE OR A LITERAL — which tools
ran, how often, in what order, whether a file exists, whether a URL / catalog title /
glyph / template key with exactly one correct spelling is present — stay deterministic
(`tool_used`, `tool_order`, `file_exists`, and the `regex` graders that are left).
JUDGMENTS ABOUT CONTENT — did the plan carry the user's database, was a role invented,
was the hand-off named, did a schedule word creep in — belong to the llm judge, because a
regex there is a lossy proxy for meaning and repeatedly failed correct output
(`constraints-carry-user-database` failed three correct plans that wrote
`per user - PostgreSQL`; `redirects-to-analyze` failed a correct refusal that named the
command earlier in the session; `no-schedule-words` made the skill enumerate vocabulary).
Those regexes were folded into each case's `criteria.md` on 2026-09-29.

What is left to check, without spending a $20 eval run:

  A. LITERAL PARITY — a positive regex grader requires a literal string in the
     model's output. If the SKILL.md that must produce it never spells that
     literal, the model free-styles and the assertion fails on some fraction of
     runs. Survivors this applies to are template identifiers the skill dictates:
     `retrieval-counted` wants `poc_guidance_chunks_retrieved:`, `constraints-block-keys`
     wants the `platform_id:` and `languages:` keys, `not-installed-glyph-present`
     wants `➖`. A literal that can only come from a tool result or the prompt's own
     test data is exempt below, with a reason.

  B. CLOSING-MESSAGE CONTRACT — a grader whose target is `last_message` demands
     the literal be in the FINAL message, not merely somewhere in the session.
     `demo-no-simulation/install-invoked` failed that way: the final message read
     "run `/senzing:install` … (steps and EULA link are above)" — the user HAD
     been shown the agreement, and the closing message pointed backwards instead
     of repeating the URL. A skill that grades `last_message` must say so.

  C. NO VOCABULARY BANS — a `not_contains` regex that enumerates words is a content
     judgment wearing a regex costume, and is exactly the class that left. The
     surviving negated regexes forbid identifiers (`G2*` names, `❌`, an unknown
     `recipes/*.md` path, a `TBD` without its owner), not English. This check fails
     the moment someone adds a word-list ban again, so the argument is had offline,
     before the grader fails a correct run.

None of these can reason about semantics, and none replaces the judge. They catch
the mechanical class: a grader asking for a shape nothing ever taught, or a grader
asking a regex to do a judge's job.

Exit 1 on any gap.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
SKILLS = ROOT / "plugins" / "senzing" / "skills"

# Cases with no skill of their own (harness self-tests).
NO_SKILL = {"canary"}

# A grader may legitimately require a literal the skill does not spell when the
# literal comes from a TOOL result or the prompt rather than the skill's own prose.
# Each entry needs a reason: this list is for "the skill cannot spell it", never for
# "the skill ought to and we did not get round to it".
LITERAL_EXEMPT = {
    # case/grader: why
    "recipes-catalog/title-customer360": "titles come from the live cookbook, not the skill",
    "recipes-catalog/title-healthcare": "titles come from the live cookbook, not the skill",
    "recipes-catalog/title-ppp": "titles come from the live cookbook, not the skill",
    "recipes-catalog/title-stewardship": "titles come from the live cookbook, not the skill",
    "ask-routing/source-url-cited": "the URL is whatever the MCP tool returned",
    "ask-license-request/payload-shown": "the name and address are the prompt's test persona, echoed back",
    "install-eula/eula-surfaced": "the EULA URL comes from sdk_guide's result, not the skill's prose",
    "recipes-named/install-invoked": "same EULA URL, surfaced from the tool by the install hand-off",
}

# `last_message` graders whose literal is exempt above may still need the closing
# contract, so the two checks are exempted separately.
CLOSING_EXEMPT: set[str] = set()

# Phrases that count as telling the model its CLOSING message must carry something.
CLOSING_CUES = (
    "last message",
    "final message",
    "closing message",
    "end your reply",
    "end with",
    "close with",
    "your reply ends",
    "the reply must end",
)


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    body = text.split("---", 2)[1]
    out: dict[str, str] = {}
    for line in body.split("\n"):
        m = re.match(r"^([a-z_]+):\s*(.*)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def case_skill(case: Path) -> str | None:
    fm = frontmatter(case / "prompt.md")
    tags = fm.get("tags", "")
    m = re.match(r"\[?\s*([A-Za-z0-9_-]+)", tags)
    return m.group(1) if m else None


def literals(pattern: str) -> list[str]:
    """Literal runs a regex requires: >=4 chars, no metacharacters, outside a negative lookahead."""
    if not pattern:
        return []
    # Drop escaped metacharacters so `\\b` etc. do not split a word.
    cleaned = re.sub(r"\\[bBdDwWsSAZ]|\\[nrt]", " ", pattern)  # \n etc. are separators, not letters
    cleaned = re.sub(r"\(\?![^)]*\)", " ", cleaned)  # negative lookahead = forbidden, not required
    cleaned = re.sub(r"\[[^\]]*\]", " ", cleaned)  # a character class is a shape, not a literal
    cleaned = re.sub(r"\\.", " ", cleaned)  # any remaining escape
    out = []
    for run in re.split(r"[^A-Za-z0-9 :_./-]+", cleaned):
        run = run.strip()
        # A run spanning an alternation is not a single required literal.
        # Require a real word: at least one alphabetic run of 4+, not a regex fragment.
        if len(run) >= 6 and re.search(r"[A-Za-z]{4}", run) and not run.isdigit():
            out.append(run)
    return out


def banned_words(pattern: str) -> list[str]:
    """English words or phrases a not_contains pattern bans, e.g. `\b(gantt|timeline|go-live date)\b`.

    Identifiers are not words: anything carrying a digit, a path separator, an
    underscore, or a non-ASCII glyph is a spelling, not vocabulary. Alternations
    that are regex structure (`(?: … )`, lookahead groups) are skipped.
    """
    out: list[str] = []
    # Collapse inner groups to their first branch so `kick-?off (date|meeting)` is seen
    # by the outer scan as one phrase.
    flat = re.sub(r"\(([^()|]*)\|[^()]*\)", r"\1", pattern)
    for group in re.findall(r"\(([^()]*\|[^()]*)\)", flat):
        if group.startswith("?"):
            continue
        for alt in group.split("|"):
            word = re.sub(r"\\[bBdDwWsS]|\?:|\\", "", alt.strip()).strip()
            if re.fullmatch(r"[A-Za-z][A-Za-z '-]{2,}", word):
                out.append(word.lower())
    return sorted(set(out))


def main() -> int:
    problems: list[str] = []
    checked = 0
    negated_checked = 0

    for case in sorted(p for p in EVALS.iterdir() if p.is_dir()):
        if not (case / "prompt.md").exists():
            continue  # fixture/helper directory, not an eval case
        skill_name = case_skill(case)
        if not skill_name or skill_name in NO_SKILL:
            continue
        skill_file = SKILLS / skill_name / "SKILL.md"
        if not skill_file.exists():
            problems.append(f"{case.name}: tags name skill '{skill_name}' but {skill_file} is missing")
            continue
        skill_text = skill_file.read_text(encoding="utf-8")
        skill_lower = skill_text.lower()

        for g in sorted((case / "graders").glob("*.md")):
            fm = frontmatter(g)
            if fm.get("type") != "regex":
                continue
            key = f"{case.name}/{g.stem}"
            pattern = fm.get("pattern", "").strip().strip('"')
            target = fm.get("target", "")
            # `match:` is authoritative. The old stem heuristic (`no-*`, `not-*`) also
            # caught `not-installed-glyph-present`, a POSITIVE grader, and silently
            # skipped it.
            negated = fm.get("match") == "not_contains"

            if negated:
                # CHECK C — a prohibition is a regex's job only when it forbids a
                # spelling. A word list is a judge clause; say so before it fails a
                # correct run for phrasing.
                negated_checked += 1
                words = banned_words(pattern)
                if words:
                    problems.append(
                        f"{key}: a not_contains regex bans English ({words[:4]}). That is a "
                        f"judgment about content, not a fact about the trace — put it in "
                        f"criteria.md as a checkable clause; regexes here are for identifiers."
                    )
                continue

            checked += 1
            if "last_message" in target and key not in CLOSING_EXEMPT:
                if not any(cue in skill_lower for cue in CLOSING_CUES):
                    problems.append(
                        f"{key}: grades `last_message`, but {skill_name}/SKILL.md never states a "
                        f"closing-message contract. A run that says it mid-session and summarizes "
                        f"without it fails a correctly-behaving skill."
                    )

            if key in LITERAL_EXEMPT:
                continue
            missing = [lit for lit in literals(pattern) if lit.lower() not in skill_lower]
            # Require ALL literal runs to be absent before complaining: one present
            # run means the skill does spell the shape somewhere.
            if missing and len(missing) == len(literals(pattern)) and literals(pattern):
                problems.append(
                    f"{key}: requires literal(s) {missing[:3]} that {skill_name}/SKILL.md never "
                    f"spells. The model has to invent the shape, so it will vary run to run."
                )

    print(f"checked {checked} positive and {negated_checked} negated regex grader(s) across the suite")
    if problems:
        print("\ngrader/skill parity gaps:\n")
        for p in problems:
            print(f"  ✗ {p}")
        print(f"\n{len(problems)} gap(s). Pin the shape in the skill, add a reasoned "
              f"LITERAL_EXEMPT entry if the literal can only come from a tool result, or move "
              f"a content judgment into criteria.md.")
        return 1
    print("ok   every surviving regex grader asserts a spelling the skill pins or a tool supplies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
