#!/usr/bin/env python3
"""Check a senzing-poc-plan.md against the structure downstream skills rely on.

Run this on the plan you just wrote, fix what it names, run it again. It is not a
style checker: every rule here is one that `analyze`, `doctor` or `install` depends
on when they read the plan as a handoff, or one that a plan has demonstrably got
wrong in practice.

    python3 validate_plan.py senzing-poc-plan.md

Exit 0 and "plan is well formed" means the structure is right. It cannot tell you
whether the CONTENT is honest — whether a quote is real, whether a role was
invented. That stays with the skill's own rules and with review.

Why a script and not more prose: every rule below was learned by a plan getting it
wrong, and prose rules were extended one instance at a time without ever closing
the class. A plan either satisfies these or it does not, and the answer takes
milliseconds instead of three LLM votes over 20,000 characters.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TBD_RE = re.compile(r"TBD — decided by\s+(?P<owner>[^:\n]+?)(?P<tail>:[^\n]*)?$")
SC_KEYS = {"id", "shape", "statement", "measurement", "measured_against", "decided_by", "target"}
REQUIRED_SECTIONS = [f"## {n}." for n in range(1, 10)]


def yaml_blocks(text: str) -> list[str]:
    return re.findall(r"```ya?ml\n(.*?)```", text, re.S)


def tbd_paths(text: str) -> list[str]:
    """Every TBD in the document, as a dotted path. Nested keys count separately.

    A §2 block like
        performance_required:
          throughput: TBD — decided by X
          latency:    TBD — decided by X
    is TWO open decisions. Plans have repeatedly listed only the parent in §9, so
    the children silently never get decided.
    """
    found: list[str] = []
    for block in yaml_blocks(text):
        stack: list[tuple[int, str]] = []
        for line in block.split("\n"):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = re.match(r"^(\s*)-?\s*([A-Za-z_][\w]*):(.*)$", line)
            if not m:
                continue
            indent, key, rest = len(m.group(1)), m.group(2), m.group(3)
            while stack and stack[-1][0] >= indent:
                stack.pop()
            path = ".".join([k for _, k in stack] + [key])
            if "TBD — decided by" in rest:
                found.append(path)
            stack.append((indent, key))
    return found


def section(text: str, n: int) -> str:
    m = re.search(rf"^## {n}\..*?(?=^## \d+\.|\Z)", text, re.S | re.M)
    return m.group(0) if m else ""


# Checks that could not run. Printed on success as well as failure, because
# "plan is well formed" otherwise overstates what was actually verified.
problems_skipped: list[str] = []


def check(text: str) -> list[str]:
    problems: list[str] = []
    problems_skipped.clear()

    for marker in REQUIRED_SECTIONS:
        if marker not in text:
            problems.append(f"missing section '{marker}' — downstream skills parse by these headings")

    # Every TBD appears in §9 open_decisions, nested ones included.
    sec9 = section(text, 9)
    opened = sec9.split("open_decisions:", 1)[1] if "open_decisions:" in sec9 else ""
    for path in tbd_paths(text):
        leaf = path.split(".")[-1]
        if path not in opened and leaf not in opened:
            problems.append(
                f"§9 open_decisions does not list '{path}'. Every TBD gets a line, including "
                f"nested keys — a downstream skill reads §9 to find what is still open, so one "
                f"missing here is a decision nobody ever makes."
            )

    # Nothing after the TBD literal except a §9 pointer naming WHAT is open.
    #
    # Three things are deliberately NOT flagged, because the correct fixture does
    # all three and a checker that fails correct work gets switched off:
    #   * prose and comments that merely MENTION the literal (the §2 header comment
    #     explaining the rule, a §4 question listing which fields are open);
    #   * `SC-n` in a pointer — the template's own `<field or SC-n>` form, whose
    #     digit is an identifier, not a candidate answer;
    #   * key names in a pointer (`target`, `measured_against`).
    # What IS flagged is a figure: a quantity, percentage, duration or version.
    FIGURE = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:%|k\b|m\b|gb|mb|tb|cores?|days?|weeks?|months?|"
                        r"records?|rows?|seconds?|minutes?|hours?|iops)|\b\d+\.\d+|\b\d{3,}\b")
    for i, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("#") or "`TBD" in stripped:
            continue  # a comment, or prose quoting the literal to explain it
        m = TBD_RE.search(stripped)
        if not m:
            continue
        tail = (m.group("tail") or "").lstrip(":").strip()
        if not tail:
            continue
        if line in sec9:
            if FIGURE.search(tail):
                problems.append(
                    f"line {i}: the §9 pointer carries a figure — '{tail[:60]}'. The pointer "
                    f"names WHAT is open, never a candidate answer; put the figure on its cited "
                    f"line in the section the decision lives in."
                )
        elif FIGURE.search(tail):
            problems.append(
                f"line {i}: a figure follows the TBD literal — '{tail[:60]}'. "
                f"`TBD — decided by <owner>` ends a value; a hint after it answers the question "
                f"the plan just said was open."
            )

    # §3 success criteria use the template's seven keys and no others.
    for block in yaml_blocks(section(text, 3)):
        for key in re.findall(r"^\s*-?\s*([A-Za-z_][\w]*):", block, re.M):
            if key not in SC_KEYS:
                problems.append(
                    f"§3 uses key '{key}', which is not one of the seven the template defines "
                    f"({', '.join(sorted(SC_KEYS))}). Extra keys are the plan inventing structure."
                )

    # Every yaml block must actually parse — a plan is read, not just displayed.
    try:
        import yaml

        for n, block in enumerate(yaml_blocks(text), 1):
            # Fill only LEAF keys. A bare `data_sources:` whose next line is a
            # more-indented list is a parent, and filling it invents the very
            # conflict we are checking for.
            lines = block.split("\n")
            out = []
            for idx, raw in enumerate(lines):
                mk = re.match(r"^(\s*)([A-Za-z_][\w]*:)\s*$", raw)
                if mk:
                    indent = len(mk.group(1))
                    nxt = next((l for l in lines[idx + 1:]
                                if l.strip() and not l.strip().startswith("#")), "")
                    if not (nxt and (len(nxt) - len(nxt.lstrip())) > indent):
                        raw = f"{raw} x"
                out.append(raw)
            filled = "\n".join(out)
            try:
                yaml.safe_load(filled)
            except yaml.YAMLError as e:
                problems.append(f"yaml block {n} does not parse: {str(e).splitlines()[0]}")
    except ImportError:
        # PyYAML is NOT in stock python3. Saying nothing here meant this script
        # printed "plan is well formed" having never run the yaml parse check that
        # SKILL.md promises — a validator claiming success on a check it skipped is
        # the exact failure mode this release exists to stamp out. Say so instead.
        # Deliberately NOT an install command. This printed "pip install pyyaml", and
        # the model in the eval did exactly as told -- `... || pip install --quiet pyyaml
        # 2>&1 | tail -5` -- in a planning skill whose whole contract is that it does not
        # touch the host. State the fact; the operator can act on it, the model has no
        # imperative to copy.
        problems_skipped.append(
            "yaml blocks NOT parse-checked: PyYAML is not available to this python3. "
            "Every structural check above still ran, and this is not something to go fix "
            "from inside the skill -- report it as-is."
        )

    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    try:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"cannot read {sys.argv[1]}: {e}")
        return 2

    problems = check(text)
    for n in problems_skipped:
        print(f"  ! {n}")
    if problems_skipped:
        print()
    if problems:
        print(f"{len(problems)} problem(s) in {sys.argv[1]}:\n")
        for p in problems:
            print(f"  - {p}")
        print("\nFix these and run this again. Each is something a downstream skill relies on.")
        return 1
    # The phrase "plan is well formed" stays a PREFIX in both branches on purpose:
    # SKILL.md step 8 and the validator-ran grader both key the repair loop on it as a
    # substring, so changing it outright would leave the model looping forever whenever
    # PyYAML is absent. What changes is the claim. Printing the unqualified sentence
    # after skipping a check is the same overstatement this release exists to remove --
    # the skipped-check notice was already printed, but the verdict spoke over it.
    if problems_skipped:
        print(f"plan is well formed for every check that ran: {sys.argv[1]}")
        print("(NOTE: not every check ran — see ! above)")
    else:
        print(f"plan is well formed: {sys.argv[1]}")
    print("(structure only — whether the content is honestly sourced is not checkable here)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
