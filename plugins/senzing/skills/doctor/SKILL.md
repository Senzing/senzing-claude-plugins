---
name: doctor
description: >
  Diagnose a Senzing environment before anything runs. Use automatically before the first Senzing
  operation of a session, and whenever an SDK script fails to import/init/connect, or the user
  asks "is my Senzing set up?", "check my Senzing environment", "why won't Senzing start". The
  shared up-front preflight for every skill: checks network/allowlist reachability
  (mcp.senzing.com + raw.githubusercontent.com), the host shell, the SDK install, engine
  configuration, database reachability, license, AND whether this host can serve a live interactive
  app or only a self-contained artifact — returning grounded, actionable fixes instead of a raw
  traceback — or wants Senzing installed or set up in the first place — e.g. "install Senzing",
  "set up Senzing on this machine", "get me started with Senzing".
allowed-tools: Bash, Read, mcp__plugin_senzing_senzing__*
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
  same failure as a second ❌. Dependency chain: 4 → 5 → 6 → {6b, 9}; 7 → 8. **Check 9 (license)
  depends only on 6, NOT on 7/8** — a license is readable with `internal://` and no database.
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
default to Python because it is the usual choice.**

Host-kind signals (for check 3): `CLAUDECODE=1` / `CLAUDE_CODE_ENTRYPOINT=cli` → Claude Code on
the user's machine. `/.dockerenv` present, or `/proc/version` containing `microsoft` → container
or WSL2. Neither → likely a cloud sandbox.

## The checks

1. **Grounding reachable.** Two DIFFERENT networks — do not conflate them:
   - *MCP connectivity*: a successful `get_capabilities` call. This is the one that matters for
     grounding, and it can work while Bash egress is blocked (and vice versa).
   - *Bash egress*: `curl -fsSI https://mcp.senzing.com/` and `https://raw.githubusercontent.com/`.
     Treat **any HTTP response as reachable** — only DNS failure, connection refused, or timeout
     is unreachable. (A bare root returning 3xx/4xx is fine; `-f` fails only on ≥400, and
     `raw.githubusercontent.com` currently answers 301.)

   `mcp.senzing.com` unreachable → ❌ "allowlist mcp.senzing.com" and **stop** — SDK downloads,
   sample data and resources all need it. `raw.githubusercontent.com` unreachable → ⚠️ only;
   examples and recipes fall back to each response's `access_steps` / `download_resource`. **Do
   not stop for it.**

2. **Host shell + writable workspace.**
   ```bash
   d=$(mktemp -d) && echo ok > "$d/probe" && cat "$d/probe" && rm -rf "$d"
   ```
   No shell → ➖ everything below; say so plainly (a spawned sub-agent with a trimmed tool set
   cannot run the SDK path).

3. **Interactive-outcome capability.** Using the Step 0 signals: Claude Code on the user's machine
   can serve a live `localhost` app ✅. Container/WSL2 → ⚠️ "reachable only via port-forward".
   Cloud sandbox (Claude Desktop / Chat, Cowork) → ⚠️ "artifact only, cannot expose localhost" —
   **not ❌; nothing is broken.** Report it so `recipes` / `build` / `demo` offer the
   self-contained HTML artifact, or recommend Claude Code, *before* a long run.

4. **Locate the install — IN THE PLATFORM'S OWN LOCATION.**

   | Platform | Where |
   |---|---|
   | macOS (arm64) | Homebrew: `brew list \| grep -i senzing`, `$(brew --prefix)/opt/senzing` |
   | macOS (x86_64) | **No native SDK exists** — casks are `arch: :arm64`. → ➖ "no native build for this architecture"; offer Docker. Do NOT hunt `/usr/local/opt/senzing`. |
   | Windows | Scoop: `scoop list`, `scoop prefix senzingsdk` |
   | Linux | `/opt/senzing`; `dpkg -l 'senzingsdk*'` or `rpm -qa 'senzingsdk*'` |

   Also honour **`$SENZING_ROOT`** (macOS/Linux) and **`%SENZING_DIR%`** (Windows). ⚠ Both already
   point at the **`er`** directory — so the library is `$SENZING_ROOT/lib/libSz.dylib` and the
   version file `$SENZING_ROOT/szBuildVersion.json`. (There is no `SENZING_PATH` convention.)
   Define `<install>` as the parent holding both `er/` and `data/`.

   Confirm by **finding the library** — `libSz.dylib` (macOS) / `libSz.so` (Linux) / `Sz.dll`
   (Windows) — never by the absence of one directory. Version: `er/szBuildVersion.json`, falling
   back to `data/szBuildVersion.json` (Windows puts it there).

   **Which build is active:** `$(brew --prefix)/opt/senzing` is a *symlink* overwritten by
   whichever cask installed last. `readlink` it. `brew info` is per-cask and can disagree;
   `szBuildVersion.json` is authoritative. ⚠️ if the active cask is `senzingsdk-staging`
   (pre-release) or if both casks are installed — report both versions.

   Nothing found → **➖ "not installed"**, offer `sdk_guide(topic="install", platform=…)` and the
   `request-eval-license` path, cascade 5–9 to ➖, and do not attempt resolution.

5. **Loader path.** Derive it, never hardcode it (`sdk_guide` flags a hardcoded path as an
   **error**-severity anti-pattern):
   ```bash
   export SENZING_ROOT="$(brew --prefix)/opt/senzing/er"   # macOS
   export DYLD_LIBRARY_PATH="$SENZING_ROOT/lib"
   ```
   Linux: usually unnecessary (the package registers the lib); use `LD_LIBRARY_PATH=/opt/senzing/er/lib`
   if you see `libSz.so: cannot open shared object file`. Windows: Scoop already puts `er\lib` on PATH.

   > ⚠ **macOS SIP strips `DYLD_*` from Apple-signed binaries.** `/usr/bin/python3`, `/bin/bash`,
   > `/bin/sh`, `/usr/bin/java` — and anything launched *through* them — never see it. So:
   > probe with the interpreter that **owns the package**
   > (`python3 -c 'import senzing_core, sys; print(senzing_core.__file__)'`; if that resolves to
   > `/usr/bin/python3`, switch to the Homebrew/pyenv/venv one), set the variable **on the same
   > command line**, and **never wrap the probe in `bash -c`**. A `dlopen` failure that survives
   > *that* is real; one that does not is ⚠️ "loader path not persisted — add the export to
   > `~/.zshrc`".

6. **SDK importable — support and function are SEPARATE facts.**
   - *Support*: `sdk_guide(topic="install", platform=<p>, language=<l>)` → `compatibility_notes`.
     ⚠ That field only appears **when `language` is passed**. Its wording is deliberately
     discouraging ("not supported on macOS… use Docker or WSL2"); it settles **support**, not
     **function**.
   - *Function*: the actual import, with check 5 applied.

   | Support | Probe | Report |
   |---|---|---|
   | supported | passes | ✅ |
   | unsupported | passes | ⚠️ "loads, but not a shipped binding on this platform — unsupported" — **not ❌** |
   | unsupported | fails | ➖ "unsupported binding; use \<supported language\> or Docker" |
   | supported | fails | ❌ with the fix |

   **Determine which bindings exist by listing what the install actually ships — do not infer it
   from a table or from memory:**
   ```bash
   ls "$SENZING_ROOT/sdk/"     # macOS 4.5.0 => c  dotnet  java   (NO python)
   ```

   ⛔ **The SDK ships NO Python bindings on macOS or Windows.** On macOS `er/sdk/` contains only
   `c`, `dotnet` and `java`. Python is therefore **not a shipped binding on those platforms** —
   the only way to get one is `pip install senzing senzing_core`, which publishes a **Linux**
   package. It will install happily and can even `dlopen` the macOS `libSz.dylib`, so it may
   appear to work — but it is not part of the SDK, not supported, and must never be presented as
   a working Senzing setup. Report it as ⚠️ **"pip-installed binding, not shipped by the SDK on
   this platform — unsupported"** and steer to Java, C#, or Docker/WSL2.

   Tell the two apart by where the module resolves:
   ```bash
   python3 -c 'import senzing_core; print(senzing_core.__file__)'
   # site-packages/...  => pip-installed (macOS/Windows: unsupported)
   # /opt/senzing/er/sdk/python/... => shipped by senzingsdk-runtime (Linux: supported)
   ```

   Conversely on **Linux, do NOT pip install**: the modules ship inside `senzingsdk-runtime` at
   `/opt/senzing/er/sdk/python` — set `PYTHONPATH` instead. Failure there looks like
   `ModuleNotFoundError`, not `dlopen`.

   Matrix (confirm with `sdk_guide`): **Python — Linux only**; **Java and C#** official on
   macOS/Windows; **Rust and TypeScript** community.

   **Check the toolchain too** — choosing a language with no compiler yields an unusable ✅:
   Java `java -version` + `ls $SENZING_ROOT/sdk/java/*.jar` · C# `dotnet --version` +
   `ls $SENZING_ROOT/sdk/dotnet` · TypeScript `node -v` · Rust `cargo -V`.

   **No language named?** Pick an *officially supported* one with a working toolchain, and say
   which you chose. Tiebreak when both Java and C# qualify: prefer whichever the user's project
   already has a build file for (`pom.xml`/`build.gradle` vs `*.csproj`); absent that, Java.

6b. **Engine self-test — the check that separates "install healthy" from "user config wrong".**
   Use `"CONNECTION": "internal://"` (v4.3+): in-memory, single-process, **needs no database and
   no `SENZING_ENGINE_CONFIGURATION_JSON`**. Build the factory, register a data source, add two
   records, read the entity back. ✅ on success; on failure run `explain_error_code` against the
   returned SENZ code and report that, never a raw traceback.

7. **Engine configuration.** ⚠ `SENZING_ENGINE_CONFIGURATION_JSON` is a **naming convention** used
   by POC tools and examples — **NOT required by the SDK**, which simply receives a config string
   an application may build any way it likes.
   - unset → **➖** (expected on a machine nobody has pointed at a repository yet — never ❌)
   - set but not valid JSON → ❌
   - set and parseable → verify `CONFIGPATH`, `RESOURCEPATH`, `SUPPORTPATH` **exist on disk**; a
     wrong `SUPPORTPATH` passes every other check and then fails engine init with SENZ7426 while
     `SzProduct` still works. macOS `SUPPORTPATH` is `$(brew --prefix)/opt/senzing/data` — a
     **sibling** of `er/`, not under it.
   > ⛔ **Never derive config from the shipped `er/etc/sz_engine_config.ini` on macOS/Windows** —
   > cask 4.5.0.26245 ships Linux paths (`/opt/senzing/...`) that do not exist there.

8. **Database reachable.** ➖ when check 7 is ➖, or when the connection is `internal://` (nothing
   to reach). Otherwise parse the connection string from the config and test it: SQLite → the file
   (⚠ it is **not** auto-created; fix is
   `sqlite3 <db> < <install>/er/resources/schema/szcore-schema-sqlite-create.sql`);
   PostgreSQL/MySQL/MSSQL → connect with the matching client. ⚠ PostgreSQL on macOS needs
   `brew install libpq && brew link libpq --force`, otherwise the errors are misleading
   `.dylib` failures.

9. **License.** Depends on check 6 only. Probe `SzProduct.get_license()` using a minimal
   `internal://` config — no database, no user config required.
   > ⚠ **There is always a license.** With none configured this returns a built-in EVAL record,
   > so "no license" is not an observable state and must not be reported as one.

   `customer` empty + `recordLimit` 500 → ⚠️ built-in eval (500 DSRs; `SENZ9000|LIMIT` at record
   501). **Do not prompt for a license unless the user actually has >500 records.** `expireDate`
   in the past → ❌ with the fix (`submit_feedback(category="license_request")`, ask.senzing.com,
   or add `LICENSESTRINGBASE64`). Otherwise ✅, stating `recordLimit` and `expireDate`.

## Reporting

One row per check, in order, each with a glyph and a one-line status. For any ❌ or ⚠️, map the
cause through `explain_error_code` / `sdk_guide` and give a **specific, runnable fix** — never a
raw stack trace. Checks 1–3 are host-level and resolve independently of whether Senzing is
installed: **a green host with no SDK is a valid, healthy state** (the caller may only need
grounding or code generation).

## Install path

If the user asked to *install* Senzing, go straight to
`sdk_guide(topic="install", platform=<from Step 0>)` and follow its commands, including its EULA
prompt before running anything.

> ⛔ **A zero exit code from `brew install` does NOT mean the SDK installed.** Verify:
> `test -f "$(brew --prefix)/opt/senzing/er/lib/libSz.dylib"` and
> `ls "$(brew --prefix)/opt/senzing/data"/*TransRules.sz`.
