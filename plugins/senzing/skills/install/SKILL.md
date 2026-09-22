---
name: install
description: >
  Install and set up Senzing on this machine — the SDK, a database, and a license — using the
  official platform-specific steps, with the license agreement surfaced before anything runs. Use
  when the user asks to "install Senzing", "set up Senzing on this machine", "get me started with
  Senzing", or when doctor, demo or analyze finds no Senzing present. Not for checking an install
  that already exists (use doctor).
argument-hint: "[platform] [language]"
allowed-tools: Bash, Read, Skill, mcp__plugin_senzing_senzing__*
---

# Install Senzing

Install steps are **Senzing facts and change with the SDK**, so they live in the MCP, not in this
file. This skill owns the *workflow*: work out the host, get the official steps, run them, and
prove the result. It deliberately reproduces none of the commands.

## Inputs

**If `./senzing-poc-plan.md` exists, read it before asking the user anything.** It is the handoff
artifact `/senzing:poc-planner` writes, and its header declares a consumer contract. Parse by the
`## N.` headings and take `platform_id`, `languages` and `database` from the `## 2.` yaml block
rather than re-asking or choosing for them. **Any value you need whose text begins
`TBD — decided by` is an undecided row: stop, name the row and its owner, and send the user back
to `/senzing:poc-planner` — never fill it in yourself.** If the user wrote the plan somewhere
else, they must tell you the path.

## Procedure

0. **Is this shell the user's machine?** Reuse `doctor`'s Step-0 host-kind signals before anything
   else: `CLAUDECODE=1` / `CLAUDE_CODE_ENTRYPOINT=cli` → Claude Code on the user's machine —
   proceed (or a Claude Code **cloud/remote** session, which sets the same variables while the
   shell is a cloud VM — ask if unsure). `/.dockerenv` present, or `/proc/version` containing
   `microsoft` → a container or WSL2;
   the install lands *there* — say so. **Neither signal → a cloud sandbox** (Claude Desktop / Chat,
   Cowork). There the Bash tool is a throwaway Linux VM: `uname` says Linux, the package install
   "succeeds", and `doctor` goes green **inside the sandbox** while the user's actual machine has
   nothing. Say plainly: *"This shell is not your machine — I would be installing Senzing into a
   disposable sandbox. Run `/senzing:install` in Claude Code on the host you want Senzing on."*
   **No shell at all** → the same answer. Never report an install you could not run on the target
   host.
   **"Stop" here means stop RUNNING, not stop working.** Whatever the host verdict, you still owe
   the user the official steps and the license agreement: carry on through steps 1-3 — call
   `sdk_guide(topic="install", …)` and surface the EULA — and hand them the commands to run
   themselves on the right machine. Skip only step 4 (running them) and step 5 (verifying). A
   host verdict is never a reason to skip `sdk_guide`: the steps are Senzing facts that live in
   the MCP, so answering "run it elsewhere" without them leaves the user with nothing to run and
   an unsurfaced license.
   **Never END THE TURN on the host question.** "Ask if unsure" means carry the question
   alongside the work, not instead of it: do steps 1-3 first, then close with the question and
   what changes depending on their answer. Stopping to ask before you have fetched anything
   leaves the user with a question and nothing else — and in any non-interactive context (a
   scripted run, an eval, a queued job) no answer is coming, so the install simply never
   happens. When the signals are ambiguous, state the assumption you are proceeding under,
   deliver the steps, and let them correct you.

1. **Establish the host — never assume it.**
   ```bash
   uname -s    # Darwin | Linux | MINGW*/MSYS*/CYGWIN*
   uname -m    # arm64 | x86_64 | aarch64
   ```
   Call `sdk_guide(topic="install")` with **no** platform to get the platform decision tree and
   pick the platform id from that tree — do not carry the ids from memory. If the host matches none
   of them cleanly (a distribution the tree doesn't name, an ambiguous package manager, an
   architecture the tree says has no native build), **ask the user or take the tree's Docker option
   — do not guess an id.** Ask which language they intend to use; it changes what gets installed,
   and the `compatibility_notes` that come back (only when `language` is passed) settle whether
   that binding is supported on this platform.

2. **Get the official steps.** `sdk_guide(topic="install", platform=…, language=…)`. Use what it
   returns verbatim — install commands, environment variables, and the `direct_download` URLs it
   provides for firewalled environments. Do not hand-write install commands.

3. **Surface the license agreement before running anything — unconditionally.** Name it as the
   Senzing **End User License Agreement (EULA)**, in those words, with the URL the tool returned,
   show what `sdk_guide` returned about it, and ask for explicit agreement. Do not auto-accept on
   the user's behalf.
   **This is not conditional on the returned steps carrying a EULA prompt, and not conditional on
   the install going ahead.** Every reply that ends your turn owes the user the license
   agreement — including the ones that end on a blocker rather than on an install: an
   unsupported platform/language pair, a missing prerequisite (no Docker, no admin rights), a
   sandboxed host, or a choice of paths you are putting to them. Those are exactly the turns
   that have shipped without it, because "we are not installing yet" reads as "the license is
   not due yet". It is due: the user is being asked to choose an install path, and
   the license is one of the terms they are choosing under. Put the EULA question in the SAME
   message as the options, not after the choice.

4. **Run the steps** with Bash, showing each command before you run it.

5. **Verify — a zero exit code is NOT proof it installed.** `sdk_guide` returns the verification
   commands for the platform; run them.
   **If any verification command fails, STOP.** Do not re-run the installer and do not hand off to
   `doctor`. The installer exiting 0 while installing nothing is a documented failure on some
   platforms (macOS `brew install --cask senzingsdk` with the EULA variable unset exits 0, purges
   the download and installs nothing) — quote the matching entry from the platform's `gotchas` and
   report it. Re-running loops: `install` → verify fails → `doctor` → "not installed, offer
   install" → `install` → … Break the loop here and tell the user what to correct.
   Only when verification passes, hand off to the **`doctor`** skill for the real check: it
   confirms the library actually loads, the config resolves, and the license is valid.
   Installation is not complete until `doctor` is green — **on the target host** (step 0), not in
   a sandbox.

6. **Configure a repository.** `sdk_guide(topic="configure", platform=…)` for the engine config
   and data-source registration. It also describes the zero-setup connection option for
   single-process prototyping — use what it returns rather than restating it here.

## Licensing

Whether a license is needed is `doctor`'s call: its license row reports the active license and the
record limit it carries, read from the SDK itself. **Do not ask the user for a license unless their
dataset actually exceeds that limit.** If they do need more, `submit_feedback` with
`category='license_request'` requests a free evaluation license (its description states the
current terms — do not quote a duration or record count from memory). What happens at the limit
is `explain_error_code`'s answer, not this file's.

## If it cannot be installed here

A sandboxed host, an unsupported architecture, an unsupported platform/language pair, a missing
prerequisite, or a locked-down machine are all legitimate outcomes — say so plainly and offer the
Docker path instead of half-installing. Never report an install as successful without step 5.

**A blocker does not shorten the turn, it only removes step 4.** You still owe the user steps 1-3
in that same reply: the host you established, the official steps from `sdk_guide` for the path
you are recommending, and **the EULA** (step 3). An answer that names a blocker and asks "which
option would you like?" without the steps and the license leaves them with a question and
nothing to act on — and in any non-interactive context no answer is coming, so that is where the
run ends.
