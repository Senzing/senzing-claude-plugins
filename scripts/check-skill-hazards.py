#!/usr/bin/env python3
"""Offline checks for the defect classes that produced this week's eval failures.

Each check exists because a specific failure got through. None of them needs an
eval run; all of them run in a second. The eval is for behavior we cannot
predict — not for catching a template that does not parse or a rule written
where the model never reads it.

  A. TEMPLATE PARSES — a skill that hands the model a YAML template must hand it
     one that is valid once filled in. We asked for `database: per user: PostgreSQL`,
     which is a second colon in a plain scalar; the model substituted a dash, then
     a comma, to keep the document parseable, and failed the grader three times
     across ~$24 of eval runs before anyone read the YAML spec.

  B. SUBSTITUTION BAN IS IN THE DESCRIPTION — the rule that a skill must not
     produce its answer by other means has to be in `description:`, because that
     is what is in context when the model decides whether to fire the skill at
     all. Opus deduped six rows by hand and fired no skill; the rule forbidding
     it was in the body, which never loaded.

  C. FETCH HOST NAMED CORRECTLY — a skill that fetches over the network must name
     the host it fetches FROM, not the one a human browses. `recipes` said
     recipes come from github.com, fetched from raw.githubusercontent.com, and a
     run probed github.com, got 000, and gave up on a host it never uses.

  D. PROMPT PREMISES SURVIVE THE SANDBOX — an eval prompt asserting an
     environment fact the sandbox contradicts measures premise-handling, not the
     skill. `report-empty-instance` claimed doctor confirmed an SDK that is not
     installed; opus probed, found none, corrected the user, and failed.

Exit 1 on any finding.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins" / "senzing" / "skills"
EVALS = ROOT / "evals"

# Skills whose deliverable can be faked by doing the work another way. Each needs
# the ban in its description. A skill absent here produces no result a model
# could substitute for (doctor reports, install acts).
SUBSTITUTION_SKILLS = {
    "analyze": "resolving records by inspection instead of the engine",
    "demo": "describing a resolution it did not run",
    "report": "reporting entities it did not read",
    "recipes": "assembling a recipe's result by other means",
    "build": "writing SDK code from memory instead of from indexed snippets",
    "troubleshoot": "answering an error code from memory",
    "poc-planner": "supplying a duration, target or size of its own",
}

# Phrases that actually express a prohibition. NOT a list of words that merely
# appear in one: an earlier draft accepted "not " and "no ", which occur in almost
# any English sentence, so the check could never fail — the same vacuous-assertion
# defect this script exists to catch elsewhere.
BAN_MARKERS = (
    "failure of this skill",
    "never",
    "do not",
    "rather than",
    "instead of",
    "is not a reason",
)


def frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    return text.split("---", 2)[1] if text.count("---") >= 2 else ""


def check_templates(problems: list[str]) -> int:
    """A. every fenced yaml block in a skill must parse."""
    try:
        import yaml
    except ImportError:
        print("   (PyYAML absent — template parse check skipped)")
        return 0
    checked = 0
    for skill in sorted(SKILLS.glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        for block in re.findall(r"```ya?ml\n(.*?)```", text, re.S):
            # Comments carry the instructions; the keys carry the shape. A template is
            # a skeleton with empty values, so fill them to make it parseable — but ONLY
            # the leaves. A bare `data_sources:` whose next line is a more-indented list
            # is a parent, and filling it invents the very conflict we are looking for.
            lines = block.split("\n")
            filled_lines = []
            for idx, line in enumerate(lines):
                m = re.match(r"^(\s*)([A-Za-z_][\w]*:)\s*$", line)
                if m:
                    indent = len(m.group(1))
                    nxt = next(
                        (l for l in lines[idx + 1:] if l.strip() and not l.strip().startswith("#")),
                        "",
                    )
                    child = nxt and (len(nxt) - len(nxt.lstrip())) > indent
                    line = line if child else f"{line} x"
                filled_lines.append(line)
            filled = "\n".join(filled_lines)
            checked += 1
            try:
                yaml.safe_load(filled)
            except yaml.YAMLError as e:
                first = str(e).split("\n")[0]
                problems.append(
                    f"A {skill.relative_to(ROOT)}: a yaml template does not parse once filled "
                    f"in — {first}. The model will repair it and fail whatever reads it."
                )
    return checked


def check_substitution_bans(problems: list[str]) -> int:
    for name, mode in sorted(SUBSTITUTION_SKILLS.items()):
        f = SKILLS / name / "SKILL.md"
        if not f.exists():
            problems.append(f"B {name}: SKILL.md missing")
            continue
        # Descriptions are YAML folded scalars, so a phrase wraps across lines with
        # indentation. Collapse whitespace or every multi-word marker misses.
        desc = re.sub(r"\s+", " ", frontmatter(f.read_text(encoding="utf-8")).lower())
        if not any(m in desc for m in BAN_MARKERS):
            problems.append(
                f"B {name}/SKILL.md: description states no prohibition. This skill can be "
                f"faked by {mode}, and the routing decision is made from the description "
                f"alone — a ban in the body loads only after the skill has already fired."
            )
    return len(SUBSTITUTION_SKILLS)


def check_fetch_hosts(problems: list[str]) -> int:
    checked = 0
    for skill in sorted(SKILLS.glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        fm = frontmatter(text)
        granted = set(re.findall(r"WebFetch\(domain:([^)]+)\)", fm))
        if not granted:
            continue
        checked += 1
        body = text[len(fm) + 6 :] if fm else text
        # Hosts named in prose, ignoring the ones actually granted.
        named = set(re.findall(r"`?\b([a-z0-9-]+\.[a-z0-9.-]+\.(?:com|org|io))\b", body))
        stray = {h for h in named if h not in granted and h.endswith(("github.com",))}
        for host in sorted(stray):
            if not re.search(rf"do not probe|not a prerequisite|human reader", body, re.I):
                problems.append(
                    f"C {skill.relative_to(ROOT)}: names `{host}` but fetches only from "
                    f"{sorted(granted)}. Say which host the fetch uses and that the other is "
                    f"not a precondition, or a run will probe the wrong one and give up."
                )
    return checked


def check_prompt_premises(problems: list[str]) -> int:
    claims = re.compile(
        r"doctor (confirms|already ran|is green)|SDK (loads|is installed)|is configured",
        re.I,
    )
    exempt = re.compile(r"do not re-probe|not the Senzing host|take .{0,30}as given", re.I)
    checked = 0
    for prompt in sorted(EVALS.glob("*/prompt.md")):
        text = prompt.read_text(encoding="utf-8")
        checked += 1
        if claims.search(text) and not exempt.search(text):
            problems.append(
                f"D {prompt.relative_to(ROOT)}: asserts an environment fact the sandbox "
                f"contradicts (it has no SDK) without telling the model not to re-probe. A "
                f"skill that probes will correct the premise and fail for the wrong reason."
            )
    return checked


def main() -> int:
    problems: list[str] = []
    a = check_templates(problems)
    b = check_substitution_bans(problems)
    c = check_fetch_hosts(problems)
    d = check_prompt_premises(problems)
    print(f"checked {a} yaml template(s), {b} skill description(s), {c} fetching skill(s), {d} prompt(s)")
    if problems:
        print("\nskill hazards:\n")
        for p in problems:
            print(f"  ✗ {p}")
        return 1
    print("ok   templates parse, bans are in descriptions, fetch hosts named, premises safe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
