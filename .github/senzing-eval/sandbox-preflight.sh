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

settings='{"sandbox":{"enabled":true,"failIfUnavailable":true}}'

probe() {
  cd "$HOME/cwd" && claude \
    --print "$prompt" \
    --model haiku \
    --allowedTools Bash \
    --permission-mode dontAsk \
    --settings "$settings" \
    --strict-mcp-config \
    --output-format json 2>&1
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

echo "---- probe output ----" >&2
printf '%s\n' "$out" >&2
echo "----------------------" >&2

if printf '%s' "$out" | grep -q 'bwrap:'; then
  echo "::error::ENVIRONMENTAL FAILURE (not a plugin verdict) — the Bash sandbox is broken in this container, so nothing about the plugin was measured. Every Bash call the eval agent makes will fail the same way. Fix the image or the harness, never the plugin or the graders." >&2
  exit 1
fi

echo "::error::Sandbox preflight INCONCLUSIVE — the probe never returned the nonce and reported no sandbox error, so nothing here proves the agent can run a shell command. Treating that as a failure is deliberate: an unproven sandbox is exactly the state that produced two runs of false plugin verdicts." >&2
exit 1
