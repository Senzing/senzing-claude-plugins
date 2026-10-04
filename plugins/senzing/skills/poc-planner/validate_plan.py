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


LIT = "TBD — decided by"
KEY_RE = re.compile(r"^(?P<ind>\s*)(?P<dash>-\s+)?(?P<key>[A-Za-z_]\w*):(?P<rest>.*)$")


def _strip_comment(v: str) -> str:
    """Drop a trailing YAML comment. It starts at whitespace + '#', so `SC-#2` keeps its '#'."""
    return re.split(r"\s#", v, maxsplit=1)[0]


def _unquote(v: str) -> str:
    v = v.strip()
    return v[1:-1] if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'" else v


def block_tbd_paths(block: str) -> list[tuple]:
    """Each TBD value in one yaml block, as a tuple of path segments.

    A list item (`- key: v`) is its OWN node, one level below its parent key and above its keys.
    Its segment is ("item", parent, label, ordinal), labelled by the item's `id`/`name` value
    (SC-2, CRM export) or its position. So
        - id: SC-2
          target: TBD — decided by X
    is ((item SC-2), "target") -- NOT "id.target", which is what the earlier builder produced and
    why every stricter §9 check failed the correct fixture: SC-1, SC-2 and SC-3 all collapsed to
    the same path, so a plan missing only SC-2's target was indistinguishable from a complete one.
    """
    out: list[tuple] = []
    stack: list[tuple[int, object]] = []
    counters: dict[tuple, int] = {}
    for line in block.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = KEY_RE.match(line)
        if not m:
            continue
        ind, key, rest = len(m.group("ind")), m.group("key"), m.group("rest")
        if m.group("dash"):
            # `key:` followed by `- a: b` at the SAME indent is valid YAML: the item belongs to that
            # key, so only a previous sibling ITEM at this indent (or anything deeper) is popped.
            while stack and (stack[-1][0] > ind or (stack[-1][0] == ind and not isinstance(stack[-1][1], str))):
                stack.pop()
            parent = stack[-1][1] if stack and isinstance(stack[-1][1], str) else ""
            ctx = tuple(s for _, s in stack)
            counters[ctx] = counters.get(ctx, -1) + 1
            named = key in ("id", "name")
            label = _unquote(_strip_comment(rest)) if named else str(counters[ctx])
            stack.append((ind, ("item", parent, label, counters[ctx], named)))
            ind += len(m.group("dash"))
        while stack and stack[-1][0] >= ind:
            stack.pop()
        if key in ("id", "name") and not m.group("dash") and stack and isinstance(stack[-1][1], tuple) \
                and not stack[-1][1][4]:
            old_item = stack[-1][1]
            _, par, _, n, _ = old_item
            new_item = ("item", par, _unquote(_strip_comment(rest)), n, True)
            stack[-1] = (stack[-1][0], new_item)
            # A TBD seen BEFORE this item's id was recorded under the positional label: relabel it too.
            out[:] = [tuple(new_item if s == old_item else s for s in segments) for segments in out]
        segments = tuple(s for _, s in stack) + (key,)
        if LIT in rest:
            out.append(segments)
        stack.append((ind, key))
    return out


def tbd_paths(text: str) -> list[tuple]:
    """Every TBD in every yaml block of the document, nested keys counted separately."""
    return [segments for block in yaml_blocks(text) for segments in block_tbd_paths(block)]


def fmt_path(segments: tuple) -> str:
    parts: list[str] = []
    for s in segments:
        if isinstance(s, tuple):
            _, parent, label, _n, _named = s
            if parts and parts[-1] == parent:
                parts[-1] = f"{parent}[{label}]"
            else:
                parts.append(label)
        else:
            parts.append(s)
    return ".".join(parts)


def _token_in(tok: str, line: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(tok)}(?![\w-])", line, re.I) is not None


def covered(segments: tuple, lines: list[str]) -> bool:
    """A §9 line covers a path only if it names EVERY segment of it, on that one line.

    A list item is named by its label (SC-2), its position parent[N], or the all-items forms
    parent[] / parent[*]; a key is named as a whole token (so `SC-1` never matches `SC-10`, and
    `SC-1 target` cannot cover SC-2's target the way the old leaf-substring match allowed).
    """
    for line in lines:
        low = line.lower()
        ok = True
        for s in segments:
            if isinstance(s, tuple):
                _, parent, label, n, named = s
                # A positional label is a bare ordinal ("0", "1"): matching it as a word would let any
                # stray digit on a §9 line ("250K", "3 sources") cover an unlabeled item. Only a name
                # (`id`/`name`) is matched as a word; ordinals match only as parent[N] / parent[] / parent[*].
                if not ((named and _token_in(label, line))
                        or (parent and any(f"{parent}[{x}]".lower() in low for x in ("", "*", n, label)))):
                    ok = False
                    break
            elif not _token_in(s, line):
                ok = False
                break
        if ok:
            return True
    return False


def open_decision_lines(text: str) -> list[str]:
    """The list items under §9's `open_decisions:` key."""
    sec9 = section(text, 9)
    if "open_decisions:" not in sec9:
        return []
    out: list[str] = []
    for l in sec9.split("open_decisions:", 1)[1].split("\n")[1:]:
        if re.match(r"^\S", l) or l.startswith("```"):
            break
        if l.strip().startswith("- "):
            out.append(l.strip()[2:])
    return out


def prose_tbd_lines(text: str) -> list[tuple[int, str]]:
    """Lines that state a TBD in prose or a table: outside yaml fences and outside §9.

    Skips a literal wrapped in backticks (prose explaining the rule) and `#` comment lines.
    """
    inside, out = False, []
    s9 = text.find("\n## 9.")
    s9_line = text[:s9].count("\n") + 2 if s9 >= 0 else 10**9
    for i, l in enumerate(text.split("\n"), 1):
        if l.startswith("```"):
            inside = not inside
            continue
        if inside or i >= s9_line or LIT not in l or l.lstrip().startswith("#"):
            continue
        if any(l[max(0, m.start() - 1):m.start()] != "`" for m in re.finditer(re.escape(LIT), l)):
            out.append((i, l))
    return out


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

    # Every TBD appears in §9 open_decisions, nested ones included -- EXACTLY, not by leaf word.
    # The previous check searched for the leaf key anywhere in §9, so a plan missing only
    # SC-2.target passed whenever any other line said "target".
    sec9 = section(text, 9)
    od_lines = open_decision_lines(text)
    if sec9 and not od_lines and any(True for _ in tbd_paths(text)):
        problems.append("§9 has no `open_decisions:` list, but the plan carries TBDs - every one needs a line there")
    for segments in tbd_paths(text):
        if not covered(segments, od_lines):
            problems.append(
                f"§9 open_decisions does not list '{fmt_path(segments)}'. Every TBD gets a line, including "
                f"nested keys and each SC-n separately -- one line must name the item AND the key. A "
                f"downstream skill reads §9 to find what is still open, so one missing here is a "
                f"decision nobody ever makes."
            )

    # A TBD written in prose or a table is an open decision too ("anywhere in the plan"), and it
    # was the commonest way plans left decisions out of §9. Name it: put the §9 key in backticks on
    # the same line, and give that key a §9 line, so the two can be matched exactly.
    for i, l in prose_tbd_lines(text):
        keys = [k for k in re.findall(r"`([A-Za-z_][\w.\[\]*-]*)`", l) if not k.startswith("TBD")]
        if not keys:
            problems.append(
                f"line {i}: states `{LIT}` in prose but names no §9 key. Put the key it is tracked under in "
                f"backticks on this line (for example `data_subset_scope`) and add a §9 open_decisions "
                f"line naming that key -- otherwise this decision is never listed as open."
            )
        elif not any(_token_in(k, od) for k in keys for od in od_lines):
            problems.append(
                f"line {i}: names {', '.join('`'+k+'`' for k in keys)} but none of them appears in a §9 "
                f"open_decisions line. Add a line for the key this decision is tracked under."
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

    # License terms: the tools return license paths that DIFFER (the evaluation-license pointer,
    # submit_feedback, the web form), and the skill's rule is to quote each and list the discrepancy
    # in §9 -- never reconcile them. Plans repeatedly wrote "the tools agree" / "no discrepancy" and
    # left §9 without a license line (30 of 32 real plans omitted at least one path). This cannot see
    # the tool results, so it checks the two things it can: a license line exists in §9 whenever §6
    # discusses licensing, and §6 does not call the license terms consistent.
    sec6 = section(text, 6)
    if re.search(r"licens", sec6, re.I):
        if not any(re.search(r"licens", l, re.I) for l in od_lines):
            problems.append(
                "§6 discusses licensing but §9 open_decisions has no license line. The license paths the "
                "tools returned differ; list that discrepancy under §9 (`license path`) instead of choosing one."
            )
        # The §9 line names the two SOURCES that differ; each side's figures stay on its own quoted §6
        # line. A cap, a day count or a volume on the §9 line answers the question the line says is
        # open (CI caught a plan whose §9 discrepancy line restated "10-day/250K-record" and
        # "500-record sample": every judge vote failed it).
        for l in od_lines:
            if re.search(r"licens", l, re.I) and re.search(r"\d", re.sub(r"SC-\d+|§\s*\d+", "", l)):
                problems.append(
                    f"§9 license line carries a figure ('{l[:80]}'). Name the differing sources only "
                    f"(`license path: <tool> vs <tool>`); each side's numbers belong on its own quoted line in §6."
                )
        # A sentence is about license terms if it names licensing OR one of the paths the tools return:
        # "the tools agree -- no discrepancy" rarely repeats the word "license".
        lic_ctx = r"licens|submit_feedback|non-prod-license|eval_license|ask\s+senzing|sales@"
        for sent in re.split(r"(?<=[.!?])\s+|\n", sec6):
            if re.search(lic_ctx, sent, re.I) and re.search(
                    r"\bno\s+discrepanc\w+|\b(?:tools?|paths?|sources?|terms)\s+(?:all\s+)?(?:agree|are\s+consistent|match)\b"
                    r"|\bconsistent\s+(?:across|between)", sent, re.I):
                problems.append(
                    f"§6 says the license terms agree ('{sent.strip()[:80]}'). The tools returned differing "
                    f"license paths; quote each with its tool and list the discrepancy in §9 -- do not reconcile them."
                )

    # §3 success criteria, one pass per block: (1) only the template's seven keys; (2) every SC-n target is
    # exactly `TBD — decided by <owner>` (or the user's own words, marked `per user`) -- a measured target the plan
    # invented is the plan deciding what only the user can.
    for block in yaml_blocks(section(text, 3)):
        item = "?"
        for l in block.split("\n"):
            mk = KEY_RE.match(l)
            if not mk or l.lstrip().startswith("#"):
                continue
            k, rest = mk.group("key"), _strip_comment(mk.group("rest")).strip()
            if mk.group("dash"):
                item = "?"            # a new item: never report under the previous one's id
            if k == "id":             # `id` need not be the first key of the item
                item = _unquote(rest)
            if k not in SC_KEYS:
                problems.append(
                    f"§3 uses key '{k}', which is not one of the seven the template defines "
                    f"({', '.join(sorted(SC_KEYS))}). Extra keys are the plan inventing structure."
                )
            if k == "target":
                v = _unquote(rest)
                # An owner may contain digits ("team 2", "SRE-1"); what is rejected is a ':' tail or a
                # percent -- a figure after the owner. `per user ...` is also allowed: the user's own
                # words, which is wider than "every target is the literal" and intended (rule 4b).
                if not re.fullmatch(r"TBD — decided by [^:\n%]+?", v) and not v.startswith("per user"):
                    problems.append(
                        f"§3 {item}: target is '{v[:70]}'. A target is `TBD — decided by <owner>` or the user's "
                        f"own words marked `per user`; the plan does not set one."
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
