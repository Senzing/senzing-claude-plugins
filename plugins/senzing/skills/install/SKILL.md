---
name: install
description: >
  Install and set up Senzing on this machine — the SDK, a database, and a license — using the
  official platform-specific steps, with the license agreement surfaced before anything runs. Use
  when the user asks to "install Senzing", "set up Senzing on this machine", "get me started with
  Senzing", or when doctor, demo or analyze finds no Senzing present. Not for checking an install
  that already exists (use doctor).
argument-hint: "[platform] [language]"
allowed-tools: Bash, Read, mcp__plugin_senzing_senzing__*
---

# Install Senzing

Install steps are **Senzing facts and change with the SDK**, so they live in the MCP, not in this
file. This skill owns the *workflow*: work out the host, get the official steps, run them, and
prove the result. It deliberately reproduces none of the commands.

## Procedure

1. **Establish the host — never assume it.**
   ```bash
   uname -s    # Darwin | Linux | MINGW*/MSYS*/CYGWIN*
   uname -m    # arm64 | x86_64 | aarch64
   ```
   Map to an MCP platform id: `macos_arm`, `linux_apt`, `linux_yum`, `windows`, `docker`.
   ⚠ On an **Intel Mac** (`x86_64` + Darwin) there is no native build — go to `docker`.
   Ask which language they intend to use; it changes what gets installed.

2. **Get the official steps.** `sdk_guide(topic="install", platform=…, language=…)`. Use what it
   returns verbatim — install commands, environment variables, and the `direct_download` URLs it
   provides for firewalled environments. Do not hand-write install commands.

3. **Surface the license agreement before running anything.** If the returned steps include a
   EULA prompt, show it and get explicit agreement first. Do not auto-accept on the user's behalf.

4. **Run the steps** with Bash, showing each command before you run it.

5. **Verify — a zero exit code is NOT proof it installed.** `sdk_guide` returns the verification
   commands for the platform; run them. Then hand off to the **`doctor`** skill for the real
   check: it confirms the library actually loads, the config resolves, and the license is valid.
   Installation is not complete until `doctor` is green.

6. **Configure a repository.** `sdk_guide(topic="configure", platform=…)` for the engine config
   and data-source registration. For quick single-process prototyping on v4.3+ a
   `"CONNECTION": "internal://"` needs no database at all.

## Licensing

Senzing runs out of the box under a built-in evaluation license with a record cap. **Do not ask
the user for a license unless their dataset actually exceeds that cap** — `doctor` reports the
limit. If they do need more, `submit_feedback` with `category='license_request'` requests a free
evaluation license.

## If it cannot be installed here

A sandboxed host, an unsupported architecture, or a locked-down machine are all legitimate
outcomes — say so plainly and offer the Docker path instead of half-installing. Never report an
install as successful without step 5.
