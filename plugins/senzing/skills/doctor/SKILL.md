---
name: doctor
description: >
  Check whether this machine can do the Senzing task at hand — SDK, engine config, database,
  license, network reachability, AND what kind of result this host can actually deliver (a live
  app the user drives, a self-contained artifact, or information only). Every skill that runs or
  builds something calls this FIRST, so it fails early with a fix instead of late with a
  traceback. Use when the user asks "is my Senzing set up?", "check my Senzing environment", "why
  won't Senzing start", "does my Senzing actually work?", or when a script fails to import or
  initialize with no Senzing error code in hand. Not for a specific SENZ error code or message
  (use troubleshoot), not for installing Senzing (use install), and not for showing that Senzing
  works on sample data (use demo).
allowed-tools: Bash, Read, Skill, mcp__plugin_senzing_senzing__*
---

# Senzing doctor — environment preflight

The most common friction in the generate-and-run model is a broken environment — a blocked
network, a missing SDK, or an **outcome the host can't actually deliver**. Diagnose it **once, up
front**, before the user hits a cryptic failure or invests in a long run. Grounded by the
**Senzing MCP server**. This is the shared preflight — other skills (`analyze`, `demo`, `report`,
`recipes`, `build`) run `doctor` first and act on its verdict, so the checks live here, not
duplicated in each skill.

**Inputs.** Takes no arguments — run the probe directly (any `$ARGUMENTS` are ignored). If invoked
because the user asked to *install* Senzing, skip straight to the install path below.

**If `./senzing-poc-plan.md` exists, read it before asking the user anything.** It is the handoff
artifact `/senzing:poc-planner` writes, and its header declares a consumer contract. Parse by the
`## N.` headings and take `platform_id`, `languages` and `database` from the `## 2.` yaml block
rather than re-asking or choosing for them. **Any value you need whose text begins
`TBD — decided by` is an undecided row: stop, name the row and its owner, and send the user back
to `/senzing:poc-planner` — never fill it in yourself.** If the user wrote the plan somewhere
else, they must tell you the path.

## Division of labor — do not duplicate the MCP

This skill owns **workflow and host mechanics**: what to probe, in what order, on this machine —
platform detection, package-manager layout, loader paths, SIP behavior, and how to grade the
result. The MCP server cannot know those about the host in front of you.

**The MCP owns every Senzing fact** — install commands, config keys and their correct values,
database prerequisites, error meanings, limits. When you need one, **call the tool**
(`sdk_guide`, `explain_error_code`, `search_docs`) instead of restating it here. Senzing facts
copied into this file go stale silently and then confidently mislead; the MCP's do not.

## Status vocabulary — read this FIRST

Emit exactly one glyph per row. The difference between "broken" and "not applicable" is the
entire point of this skill; a preflight that cries wolf on a healthy host trains people to
ignore it.

| | Meaning |
|---|---|
| ✅ | Works. |
| ⚠️ | Works, but degraded, unsupported-by-policy, or not persisted. |
| ❌ | **Present and misbehaving, AND the user can act on it.** |
| ➖ | **Not applicable, not installed, or not reached.** Not a failure. |

**Rules that override any instinct to report a failure:**

- **Not installed is ➖, never ❌.** ❌ is reserved for something that IS there and IS misbehaving.
- **Cascade: if a prerequisite is ➖ or ❌, every check downstream of it is ➖** — never repeat the
  same failure as a second ❌. Dependency chain: 4 → 5 → 6 → {6b, 9}; 7 → 8. So when 4 is ➖,
  cascade **5, 6, 6b and 9** to ➖ — but **7–8 still grade**: a config can exist on a host with
  no SDK, and it is graded on its own terms. **Check 9 (license) depends only on 6, NOT on
  7/8** — a license is readable with the in-process, no-database connection (check 6b) and no
  user config.
- **Broken but NOT user-fixable** (no admin rights, locked-down host) → ⚠️ with the blocker named.
  ❌ promises the user an action; do not promise one that does not exist.
- **Never report ❌ from an absence you did not verify in the platform-correct location.** That
  single mistake produced a false "there is no Senzing on this Mac" on a machine with Senzing
  4.5.0 installed via Homebrew.

## Step 0 — establish the ground truth before any check

```bash
uname -s        # Darwin | Linux | MINGW*/MSYS*/CYGWIN*
uname -m        # arm64 | x86_64 | aarch64
```

Nothing below is meaningful until you know this. **Do not use the macOS row on Linux, and do not
default to Python because it is the usual choice.** Then make **two deliberate `sdk_guide`
calls** — one cannot do it, because the platform id and the language-scoped facts come from
different responses:

1. **Platform id.** `sdk_guide(topic="install")` with **no** arguments returns the platform
   decision tree. Map the host onto one of *its* ids — `uname` alone cannot: it says `Linux`,
   not which package manager, and its output is not a valid id. If the host matches none
   cleanly (a distribution the tree does not name, an ambiguous package manager, an
   architecture the tree says has no native build), ask the user or take the tree's Docker
   option — do not guess an id. (`install` step 1 does exactly this; keep the two in lockstep.)
2. **Language-scoped facts.** `sdk_guide(topic="install", platform=<id>, language=<l>)` for the
   language the user named. If none was named yet, pick a **provisional** candidate without
   running check 6: call `sdk_guide(topic="initialize", platform=<id>)` with **no** `language`
   — it returns the language decision tree — and take the first option not labeled community
   whose `blocked_platforms` does not list this platform id. Check 6's toolchain scan and
   tiebreak may revise the choice; if it does, re-call this step for the revised language
   before grading 4–9. Keep the response: `install.platform.env_vars`, `.default_paths`,
   `.gotchas` and `.post_install`, plus `install.engine_config` / `install.engine_config_notes`
   and any `compatibility_notes`, are the Senzing facts checks 4–9 read — loader variables, the
   library verify command, config keys, the license probe. Never read them from this file or
   from memory.

   **If the response has no `install` block** (only `compatibility_notes` + `next_steps`), that
   binding is unsupported on this platform — the server withholds paths and env vars rather
   than hand you facts for a combination it does not support. Record that verdict for check 6,
   then **re-call with a language the notes mark supported** so you still hold the platform's
   `install` block for checks 4–9. Do not fill the gap from memory — that is exactly the
   failure this preflight exists to remove.

   **If the `sdk_guide` call itself fails** — a tool error, a timeout, or a shape with none of
   `install`, `compatibility_notes`, or a `needs_input` decision tree — retry once; if it still
   fails, report it as its **own** row, **Step 0 ⚠️** "grounding tool `sdk_guide` failed —
   <error or the top-level keys you got>" (not user-fixable, so ⚠️ per the rule above — and not
   check 1's verdict: check 1 grades reachability by its own `curl` + `get_capabilities`
   probes, which can be healthy while one tool misbehaves). Grade checks 1–3 normally (they
   need no Senzing facts) and mark 4–9 ➖ "not reached — no grounding". Do **not** continue on
   remembered paths or filenames; a preflight that guesses is worse than one that stops.

Host-kind signals (for check 3): `CLAUDECODE=1` / `CLAUDE_CODE_ENTRYPOINT=cli` → Claude Code on
the user's machine (or a Claude Code **cloud/remote** session — the same variables are set but
the shell is a cloud VM; ask if unsure). `/.dockerenv` present, or `/proc/version` containing
`microsoft` → container or WSL2. Neither → likely a cloud sandbox.

## The checks

1. **Grounding reachable.** Two DIFFERENT networks — do not conflate them:
   - *MCP connectivity*: a successful `get_capabilities` call. This is the one that matters for
     grounding, and it can work while Bash egress is blocked (and vice versa). **Call it, every
     run, and do not substitute another tool for it.** A later `sdk_guide` or `search_docs`
     answering does prove the server is up, but it is not this probe: check 1 is graded on the
     one call, it is the cheapest of them, and a run that infers connectivity from whatever it
     happened to need next leaves the row resting on an accident of what it wanted anyway.
   - *Bash egress*: `curl -fsSI https://mcp.senzing.com/` and `https://raw.githubusercontent.com/`.
     Treat **any HTTP response as reachable** — only DNS failure, connection refused, or timeout
     is unreachable. (A bare root returning 3xx/4xx is fine; `-f` fails only on ≥400, and
     `raw.githubusercontent.com` currently answers 301.)

   `mcp.senzing.com` unreachable → ❌ "allowlist mcp.senzing.com" and **stop** — SDK downloads,
   sample data and resources all need it. `raw.githubusercontent.com` unreachable → ⚠️ only;
   examples and recipes fall back to each response's `access_steps` / `download_resource`. **Do
   not stop for it.**

2. **Host shell + writable workspace.** Two questions, one probe each. *Shell:* Step 0's
   `uname` already answered it — it ran, or it did not; do not run a second command to re-ask.
   No shell → ➖ everything below; say so plainly (a spawned sub-agent with a trimmed tool set
   cannot run the SDK path). *Workspace:* the question is whether the file tools write the
   **current project directory** — the only place `build`, `analyze` and `demo` ever write — so a
   `mktemp -d` in a system temp dir answers nothing. The probe is exactly one `Write` of a small
   file into the project directory and one `Read` back. **Name that file exactly
   `.senzing-doctor-probe.tmp`** and delete it as soon as you have read it back. The name is
   pinned, not stylistic: `doctor` is invoked by skills whose eval cases assert that the run wrote
   no file, and those cases exclude this one exact path so they can still fail on any other
   `Write` — see `plugins/senzing/evals/recipes-named/graders/no-file-written.md`, which carries
   the matching note. A probe under any other name is indistinguishable from a deliverable and
   will fail them. Landed → the file tools write the project. Did not land → they do not. Both
   are answers; neither is a reason to keep looking. Do NOT go hunting through `$TMPDIR`,
   `/private/tmp`, `~/.claude`, `mktemp -d`, or a `python3` open() as a second opinion — a probe
   that failed in the project directory has already told you what the other skills need to know.
   **Probe budget: ONE attempt per question** — the rule, and why, is stated once under
   *Probe budget* in **Reporting** below.

3. **Interactive-outcome capability.** Using the Step 0 signals: Claude Code on the user's machine
   can serve a live `localhost` app ✅. Container/WSL2 → ⚠️ "reachable only via port-forward".
   Cloud sandbox (Claude Desktop / Chat, Cowork) → ⚠️ "artifact only, cannot expose localhost" —
   **not ❌; nothing is broken.** Report it so `recipes` / `build` / `demo` offer the
   self-contained HTML artifact, or recommend Claude Code, *before* a long run.


4. **Locate the install — IN THE PLATFORM'S OWN LOCATION.**

   | Platform | Where |
   |---|---|
   | macOS (arm64) | Homebrew: `brew list \| grep -i senzing`, `$(brew --prefix)/opt/senzing` |
   | macOS (x86_64) | Check `sdk_guide`'s platform tree / `compatibility_notes` for whether a native build exists for this architecture. If it says none → ➖ "no native build for this architecture"; offer Docker. Do NOT hunt `/usr/local/opt/senzing`. |
   | Windows | Scoop: `scoop list`, `scoop prefix senzingsdk` |
   | Linux | `/opt/senzing`; `dpkg -l 'senzingsdk*'` or `rpm -qa 'senzingsdk*'` |

   Also honour whatever install-root environment variable `sdk_guide`'s `env_vars` names for this
   platform (an already-set one on the host is a strong hint where the install is).

   Confirm by **running the verify command from the Step 0 response** — the `post_install` line
   that lists the library, and, where present, the `gotchas` entry that says what to `test -f`
   (some platforms carry only the `post_install` line) — never by the absence of one directory.

   **You may not grade this check without having RUN the row above for this platform.** Not
   finding Senzing is a finding that requires evidence exactly as much as finding it does: ➖
   "not installed" asserts that you looked in the platform's own location and it was not there.
   Concluding it from the Step 0 response, from the absence of an environment variable, or from
   a failed import is inference, not a probe — and it is wrong on precisely the hosts that matter
   (an install under a non-default prefix, or one whose env vars are simply not exported into
   this shell). Run the command, then report the glyph.
   Those carry the library filename and where it sits under the install root; do not supply
   either from memory, they change with the SDK. Read the
   **version from the package manager** (`brew list --versions`, `dpkg-query -W 'senzingsdk*'`,
   `rpm -q 'senzingsdk*'`, `scoop list`) — host mechanics, legitimately ours.

   **Which build is active:** `$(brew --prefix)/opt/senzing` is a *symlink* overwritten by
   whichever cask installed last. `readlink` it — the target names the cask — and compare with
   `brew list --versions` for each installed cask; `brew info` is per-cask and can disagree with
   the symlink. ⚠️ if the active cask is `senzingsdk-staging` (pre-release) or if both casks are
   installed — report both versions.

   Nothing found → **➖ "not installed"**, offer the **`install`** skill (it owns the install
   workflow, including the license agreement), cascade **5, 6, 6b and 9** to ➖ (7–8 still
   grade — a config can exist on a host with no SDK), and do not attempt resolution.

5. **Loader path.** Derive it, never hardcode it (`sdk_guide` flags a hardcoded path as an
   **error**-severity anti-pattern). The variable names and their values for this platform come
   from the `sdk_guide` response's `env_vars` — including which are required and which are only
   needed when the loader cannot find the library on its own. On macOS, root the value in the
   resolved cask symlink from check 4 (`$(brew --prefix)/opt/senzing/…`), not a literal path; on
   Windows, Scoop already puts the library directory on `PATH`.

   > ⚠ **macOS SIP strips `DYLD_*` from Apple-signed binaries.** `/usr/bin/python3`, `/bin/bash`,
   > `/bin/sh`, `/usr/bin/java` — and anything launched *through* them — never see it. So:
   > probe with the interpreter that **owns the package**
   > (`python3 -c 'import senzing_core, sys; print(senzing_core.__file__)'`; if that resolves to
   > `/usr/bin/python3`, switch to the Homebrew/pyenv/venv one), set the loader variable **on the
   > same command line**, and **never wrap the probe in `bash -c`**. A `dlopen` failure that
   > survives *that* is real; one that does not is ⚠️ "loader path not persisted — add the export
   > to `~/.zshrc`".

6. **SDK importable — support and function are SEPARATE facts.**
   - *Support*: the Step 0 language-scoped call, `sdk_guide(topic="install", platform=<p>,
     language=<l>)`, one per candidate language → `compatibility_notes`. ⚠ That field appears
     only **when `language` is passed and there is a caveat**: a supported binding comes back
     with the `install` block and no `compatibility_notes` at all; an unsupported one comes back
     with `compatibility_notes` and **no `install` block**. Its wording is deliberately
     discouraging ("not supported on macOS… use Docker or WSL2"); it settles **support**, not
     **function**.
   - *Function*: the actual import, with check 5 applied. The Python probe below is the one
     example this file carries; for Java, C#, Rust and TypeScript the minimal load/import is a
     Senzing fact — take it from `sdk_guide(topic="initialize", platform=<p>, language=<l>)` or
     `generate_scaffold(workflow="initialize", language=<l>)`, never invent an import line or
     class name.

   | Support | Probe | Report |
   |---|---|---|
   | supported | passes | ✅ |
   | unsupported | passes | ⚠️ "loads, but not a shipped binding on this platform — unsupported" — **not ❌** |
   | unsupported | fails | ➖ "unsupported binding; use \<supported language\> or Docker" |
   | supported | fails | ❌ with the fix |

   **Determine which bindings exist by listing what the install actually ships — do not infer it
   from a table or from memory:** `ls` the SDK directory the Step 0 response points at — for
   Python the path its `env_vars` gives for `PYTHONPATH`; for Java the jar path in its Java
   `gotchas` entry, where one exists; for other bindings whatever `env_vars` / `gotchas` name.
   If the response names no SDK directory for a binding (not every platform's response carries
   a Java-specific `env_vars` or `gotchas` entry), say so rather than inventing a path — this
   listing step is then not executable for that binding, and function is settled by the import
   probe alone. What is listed
   there is what the SDK ships on this platform; anything importable that is *not* listed there
   arrived some other way (typically a package manager such as pip).

   ⛔ **A binding that imports but is not shipped by the install is not a working Senzing setup.**
   A package-manager-installed binding can load the SDK library and appear to work while
   `compatibility_notes` says the platform is unsupported for that language. Report it as ⚠️
   **"package-installed binding, not shipped by the SDK on this platform — unsupported"** and
   steer to a language `compatibility_notes` marks supported, or Docker/WSL2.

   Tell the two apart by where the module resolves — e.g. for Python,
   `python3 -c 'import senzing_core; print(senzing_core.__file__)'`: inside the install tree
   `sdk_guide` located ⇒ shipped by the SDK; under `site-packages` (or the equivalent for another
   language's package manager) ⇒ package-installed.

   Conversely, when the binding **is** shipped by the install, do not package-install a second
   copy: expose the shipped one with the variable `sdk_guide`'s `env_vars` names for it (for
   Python that failure looks like `ModuleNotFoundError`, not a `dlopen` error).

   Which bindings are supported on which platforms is `compatibility_notes`' answer, per language
   — do not keep a matrix here.

   **Check the toolchain too** — choosing a language with no compiler yields an unusable ✅:
   Java `java -version` + the jar(s) in the shipped Java SDK directory · C# `dotnet --version` +
   the shipped .NET SDK directory · TypeScript `node -v` · Rust `cargo -V`.

   **No language named?** Pick an *officially supported* one with a working toolchain, and say
   which you chose. Tiebreak when both Java and C# qualify: prefer whichever the user's project
   already has a build file for (`pom.xml`/`build.gradle` vs `*.csproj`); absent that, Java.

6b. **Engine self-test — the check that separates "install healthy" from "user config wrong".**
   Use the in-process, no-database connection that `sdk_guide`'s `engine_config_notes` describe
   (take the exact connection string and its version floor from there): it **needs no database
   and no `SENZING_ENGINE_CONFIGURATION_JSON`**. Build the factory, register a data source, add two
   records, read the entity back — code via the `generate_scaffold` workflows `initialize` **+
   `add_records` + `query`** (the primary route; `initialize` alone returns factory, priming,
   purge and config-registry snippets and has **no** add-record or get-entity code — take the
   add and the read-back from the other two). `sdk_guide(topic="full_pipeline", …)` is a
   fallback only: it ignores `record_count` and returns the threaded production loader plus a
   REDO snippet that is a **continuous daemon** (an endless loop that sleeps when the queue is
   empty) with no get-entity read-back — take only its per-record redo call from the loop body,
   never run it as-is, or the self-test hangs. Never hand-written. ✅ on success; on failure run
   `explain_error_code` against the returned SENZ code and report that, never a raw traceback.

7. **Engine configuration.** Grade `SENZING_ENGINE_CONFIGURATION_JSON` as a *convention*, not a
   requirement — the Step 0 response's `engine_config_notes` say why; do not restate it here.
   Grades independently of checks 4–6 (a config can exist on a host with no SDK):
   - unset → **➖** (expected on a machine nobody has pointed at a repository yet — never ❌)
   - set but not valid JSON → ❌
   - set and parseable → verify every path-valued key in its pipeline section **exists on disk**
     (the Step 0 response's `default_paths` / `engine_config` name the keys and the correct
     values for this platform — do not hardcode either here). A wrong support-data path passes
     every other check and then fails at engine init while the product API still works.
   > ⛔ **Do not copy the shipped `sz_engine_config.ini` as-is** — `sdk_guide`'s `gotchas` for
   > this platform say why and give the correct `SUPPORTPATH`. Grade a config derived from it by
   > the on-disk check above, not by where it came from.

8. **Database reachable.** ➖ when check 7 is ➖, or when the connection is the in-process one from
   check 6b (nothing to reach). Otherwise parse the connection string from the config and test
   it with the matching client — `sqlite3 <path> .tables` for a SQLite file (proves the file
   exists *and* has a schema), `psql` for PostgreSQL, `mysql` for MySQL; the clients are host
   mechanics, legitimately ours. ⚠ A SQLite repository file is **not** auto-created. The
   connection-string formats, the schema-creation step and the per-database prerequisites are
   Senzing facts — read them from `engine_config_notes` or
   `sdk_guide(topic="configure", platform=…, language=…)` rather than reproducing them here;
   they change with the SDK, this file does not.

9. **License.** Depends on check 6 only. Probe the license through the product API using the
   minimal in-process config from check 6b — no database, no user config required. Get the call
   from `sdk_guide(topic="information", language=…)` and the response's field names from
   `get_sdk_reference(topic="response_schemas", filter="license")` — do not name the method or
   its fields from memory.
   > ⚠ The tools describe the response's **shape** (`get_sdk_reference` lists its fields), not
   > what the SDK does when no license is configured — do not assert that here. Grade by the
   > record the probe returns; it is the observable.

   No customer on the record → ⚠️ built-in eval; report the record limit it returns. **Do not
   prompt for a license unless the user actually has more records than that limit.** Expiry in the
   past → ❌; offer `submit_feedback(category="license_request")` for a free eval. Otherwise ✅,
   stating the record limit and expiry. For what happens at the limit call
   `explain_error_code(9000)` rather than restating it.

## Reporting

One row per check, in order, each with a glyph and a one-line status. For any ❌ or ⚠️, map the
cause through `explain_error_code` / `sdk_guide` and give a **specific, runnable fix** — never a
raw stack trace. Checks 1–3 are host-level and resolve independently of whether Senzing is
installed: **a green host with no SDK is a valid, healthy state** (the caller may only need
grounding or code generation).

### Who asked — and where the turn goes next

**Establish this before you report, because it decides whether the table is the answer or a
footnote.**

- **The user asked for `doctor`** ("is my Senzing set up?", `/senzing:doctor`) → the table IS
  the deliverable. Report it and stop.
- **Another skill invoked you as its preflight** (`analyze`, `demo`, `report`, `recipes`,
  `build`, `install`) → the table is an **intermediate result, not a destination**. Post it and
  **carry straight on with the caller's procedure in the same turn.** Do not end the turn on the
  verdict, do not close with a question, and do not offer `install` — the caller's own procedure
  already decides what a missing SDK means for it, and in `analyze`'s case the answer is
  explicitly "map anyway, offer install at the end".

**This is the most expensive way this skill fails, and it does not look like a failure.** In the
eval suite it showed up as `mapping_workflow called 0x` on `analyze`, `analyze-multi-file-join`
and `routing-negative-dedupe` — 19 failing assertions across the CI runs on record. The trace is
always the same: `analyze` fires, invokes `doctor`, `doctor` probes the host, finds no SDK, and
the run's final message is this skill's status table. The user asked to dedupe a file and got an
environment report. Nothing errored, every row was correct, and the actual job never started.

A no-SDK verdict is the caller's cue to take its degraded path — **never** a reason to stop
short of it. When you hand back, say so in one line ("preflight done — SDK not installed;
continuing with the mapping") so the next step is visibly yours to take, then take it.

### Probe budget

**ONE attempt per question, then record the answer and move on** — one command per question, not
one per doubt. The whole preflight is a handful of shell calls: Step 0's `uname`, the
reachability curl, one write probe (check 2's rule — in the project directory, once), the
platform's own install-location command (check 4), and the SDK/engine/license probes once an
install is found. A question that resists its one probe is reported ⚠️
with what you saw, and you hand back.

**`doctor` is a preflight, not the task.** It runs before real work and its whole value is being
fast. A caller invoked `analyze` or `build`, not `doctor`; spending the turn budget on
environment forensics means the actual job never happens, which is a worse outcome than any
verdict you could have refined. A preflight that spends a dozen Bash calls re-asking the same
question — five ways to find a writable directory, three ways to list Homebrew casks — has
burned the caller's turn budget on forensics. That is not thoroughness; it is how `demo` reached
the end of its turns having probed the host beautifully and never called `sdk_guide`.

## Installing

If there is no Senzing here, or the user asked to install one, hand off to the **`install`**
skill — it owns the install workflow. Come back to `doctor` afterwards to verify: an installer
exiting zero is not proof the SDK loads.

**Only when the user asked for `doctor`.** Invoked as another skill's preflight, "no SDK" is a
row in the table you hand back, not an offer you make — see *Who asked* above. `analyze` in
particular has its own rule that installing is never the question put before the mapping, so
relaying the offer from here derails it.
