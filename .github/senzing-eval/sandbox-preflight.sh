#!/usr/bin/env bash
# Prove the agent's Bash tool can actually run a command in this container --
# before any real eval budget is spent.
#
# WHY THIS EXISTS
#
# The real-Senzing E2E burned two full runs reporting a plugin score of 0.44 for
# a purely environmental fault. Every Bash call the agent made died with
#
#   bwrap: Can't mount tmpfs on /newroot/run/shm: No such file or directory
#
# before the command ran, so the agent (correctly) refused to invent an entity
# count and the graders scored the refusal. Nothing asserted the sandbox, so the
# job spent the money and then reported the wrong verdict.
#
# WHAT IT ASSERTS, AND WHAT IT DOES NOT
#
# It does not model bubblewrap and does not reimplement the CLI's sandbox setup.
# It drives the real, pinned `claude` CLI with the sandbox turned ON through its
# own public settings keys (`sandbox.enabled`, `sandbox.failIfUnavailable`) and
# the same `--permission-mode dontAsk` the eval harness is observed to use, and
# asserts the OBSERVABLE: a shell command ran and its output came back.
#
# It runs under the SAME HOME SHAPE the real run uses, and that is not cosmetic.
# The first version of this script ran with the container's own HOME=/root and
# PASSED in the very job where every one of the agent's Bash calls died --
# because the harness does not use the container's HOME. It builds its own, and
# the fault lives there:
#
#   trace init:  cwd = /tmp/claude-eval-dMKT9y/home/cwd
#   every Bash:  bwrap: Can't create file at /tmp/claude-eval-dMKT9y/home/.aws:
#                Is a directory
#
# So the probe mirrors that layout exactly: a throwaway HOME at <workdir>/home
# with the working directory at <workdir>/home/cwd, under the same bind-mounted
# /tmp the harness's temp dir lands on. A preflight that cannot reproduce the
# fault it exists to catch is a gate that cannot fail.
#
# And the layout alone was STILL not enough: this probe printed "Sandbox
# preflight OK" in the job where every eval Bash call died, because the `.aws`
# fault is triggered by the eval's OWN sandbox settings (six deny paths), which
# `--settings '{"sandbox":{"enabled":true}}'` never carries. The probe now
# injects that same deny list; with it, the fault reproduces deterministically
# (and the image's bwrap shim makes it pass). See Fault 3 in the Dockerfile.
#
# The probe reads a NONCE the model cannot know. A marker quoted in the prompt
# would let a model that never touched Bash echo it straight back and turn this
# into a gate that cannot fail -- which is the defect it exists to prevent.
#
# Cost: one haiku turn, measured at ~$0.016 -- against $0.53 and 2.5 minutes for
# the run it protects. Haiku, not the eval's pinned sonnet, on purpose: this
# measures the HOST, not the plugin, so the model under test is irrelevant and
# the cheapest one that can call a tool is the right one.
#
# Verified in both directions before shipping (CLI 2.1.259): it exits 0 when the
# nonce comes back, and exits 1 when the nonce file is removed so no Bash call
# can produce it. A preflight that cannot fail is worse than none.
#
# Usage: sandbox-preflight.sh [workdir]
set -euo pipefail

: "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY must be set}"

workdir="${1:-/tmp/sz-sandbox-probe}"
rm -rf "$workdir"
mkdir -p "$workdir/home/cwd"

# Mirror the harness: HOME is a throwaway directory it builds under TMPDIR, and
# the session's cwd is <home>/cwd. Exporting HOME is the whole point -- see the
# header.
export HOME="$workdir/home"

nonce="sandbox-$(od -An -N8 -tx1 /dev/urandom | tr -d ' \n')"
nonce_file="$HOME/cwd/nonce.txt"
printf '%s\n' "$nonce" > "$nonce_file"

prompt="Use the Bash tool to run exactly this command: cat ${nonce_file}
Then reply with nothing but the command's output. Do not use any other tool."

# The eval does not run with these two keys alone. It writes its own sandbox
# settings, and those carry six AWS SSO-cache deny paths under its HOME (see
# Fault 3 in the Dockerfile). A probe without them PASSED in the very CI job
# whose every eval Bash call died on that list (run 35525396372): mirroring the
# HOME shape was not enough, the probe has to mirror the settings. The list is
# copied from the CLI's own `Vo` table, flat-mapped to [path, dirname(path)].
settings="$(python3 - "$HOME" "$workdir" <<'PY'
import json, os, sys
home, work = sys.argv[1], sys.argv[2]
sso = [".aws/sso", ".aws/cli/cache", ".aws/boto/cache"]
deny_write = [os.path.join(home, p) for n in sso for p in (n, os.path.dirname(n))]
deny_read = [os.path.join(home, n) for n in sso]
print(json.dumps({"sandbox": {"enabled": True, "failIfUnavailable": True,
  "filesystem": {"allowWrite": [home, os.path.join(work, "tmp")],
                 "denyWrite": deny_write, "denyRead": deny_read}}}))
PY
)"
mkdir -p "$workdir/tmp"

probe() {
  cd "$HOME/cwd" && claude \
    --print "$prompt" \
    --model haiku \
    --allowedTools Bash \
    --permission-mode dontAsk \
    --settings "$settings" \
    --strict-mcp-config \
    --output-format stream-json --verbose 2>&1
}

# Raw tool results, not the model's prose about them. The first failing run of
# this probe reported only the assistant's paraphrase -- "the command failed
# both within the sandbox (seccomp permission error) and when attempting to
# disable the sandbox" -- which is a summary of an error nobody can grep for,
# written by the same model whose tool access is in question. `--output-format
# json` returns just that final text; stream-json carries every tool_result, so
# the failure names itself.
tool_errors() {
  python3 - "$1" <<'PYEOF'
import json, sys
seen = []
for line in sys.argv[1].splitlines():
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        msg = json.loads(line)
    except ValueError:
        continue
    content = (msg.get("message") or {}).get("content")
    if msg.get("type") == "user" and isinstance(content, list):
        for block in content:
            if block.get("type") == "tool_result":
                text = json.dumps(block.get("content"))
                if block.get("is_error") or "Exit code" in text or "denied" in text:
                    seen.append(text[:400])
    for denial in msg.get("permission_denials") or []:
        seen.append("permission_denied: " + json.dumps(denial.get("tool_input"))[:300])
for item in dict.fromkeys(seen):
    print(item)
PYEOF
}

out=""
for attempt in 1 2; do
  out="$(probe || true)"
  if printf '%s' "$out" | grep -q "$nonce"; then
    echo "Sandbox preflight OK — the agent's Bash tool ran a command and returned its output (attempt $attempt)."
    exit 0
  fi
  if printf '%s' "$out" | grep -q 'bwrap:'; then
    break
  fi
  echo "sandbox probe attempt $attempt did not return the nonce; retrying once" >&2
done

errors="$(tool_errors "$out" || true)"

echo "---- tool errors ----" >&2
printf '%s\n' "${errors:-<none captured>}" >&2
echo "---- full probe output ----" >&2
printf '%s\n' "$out" >&2
echo "---------------------------" >&2

sandbox_marker="$(printf '%s' "$out" | grep -oE 'bwrap:[^"]{0,140}|sandbox-exec:[^"]{0,140}' | sort -u | head -3 || true)"
if [ -n "$sandbox_marker" ]; then
  printf 'sandbox backend said: %s\n' "$sandbox_marker" >&2
  echo "::error::ENVIRONMENTAL FAILURE (not a plugin verdict) — the Bash sandbox backend failed in this container, so nothing about the plugin was measured. Every Bash call the eval agent makes will fail the same way, and the ground-truth verification downstream is skipped because its input would be the preflight's own repository. Fix the image or the harness, never the plugin or the graders." >&2
  exit 1
fi

if [ -n "$errors" ]; then
  echo "::error::ENVIRONMENTAL FAILURE (not a plugin verdict) — the agent's Bash tool did not return the probe's output, and reported the raw errors printed above (no bwrap/sandbox-exec marker among them, no bwrap/sandbox-exec marker, so this is NOT the /run/shm or .aws sandbox-setup fault and should not be assumed to be). Nothing about the plugin was measured; the ground-truth verification downstream is skipped. Fix the image or the harness, never the plugin or the graders." >&2
  exit 1
fi

echo "::error::Sandbox preflight INCONCLUSIVE — the probe never returned the nonce, reported no sandbox-backend marker, and produced no tool error to quote, so nothing here proves the agent can run a shell command. Treating that as a failure is deliberate: an unproven sandbox is exactly the state that produced two runs of false plugin verdicts. The ground-truth verification downstream is skipped for the same reason." >&2
exit 1
