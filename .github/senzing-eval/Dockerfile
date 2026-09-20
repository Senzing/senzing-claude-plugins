# Image for the `real-senzing-e2e` job: a Linux host that can actually run Senzing.
#
# Why build one instead of pulling a Senzing image: the Senzing MCP's own install
# guidance (sdk_guide topic='install', platform='docker') is explicit that the
# pre-built images (senzing/senzingsdk-runtime, senzing/senzingsdk-tools,
# senzing/init-database) REQUIRE PostgreSQL and do not support SQLite, and that the
# supported way to get a SQLite-capable host is "a plain Linux container (e.g.
# debian:bookworm-slim) and follow the linux_apt guide inside it". This eval wants
# a throwaway on-disk SQLite scratch repository, exactly as the `analyze` skill
# builds one on a user's machine, so it follows that guidance.
#
# Node base because `claude plugin eval` ships as an npm package; the Senzing
# packages go on top via the official apt repository.
# Two Trivy misconfig findings are suppressed for this file in .trivyignore,
# with the reasons recorded there and repeated here:
#
# DS-0002 (no non-root USER) and DS-0026 (no HEALTHCHECK) are suppressed here
# deliberately, with reasons, rather than silenced globally:
#
# DS-0002 - this image is an ephemeral CI test fixture. It is never deployed,
#   never network-facing, and is run `--privileged` by necessity: the sandbox
#   `claude plugin eval` needs for its Bash grant requires an unprivileged user
#   namespace, and clearing that was the whole reason the sibling job had to
#   leave ubuntu. It also apt-installs the Senzing SDK at build time. Switching
#   to a non-root USER is a real improvement and is tracked as a follow-up, but
#   it changes /work ownership and the sandbox's HOME, and there is no Docker
#   daemon available to verify it -- shipping an untested container change to
#   satisfy a scanner would trade a documented risk for an undocumented one.
#
# DS-0026 - a HEALTHCHECK is meaningless for a batch container that runs one
#   command and exits. Adding a no-op probe to turn a scanner green is exactly
#   the kind of gate-that-cannot-fail this PR exists to remove.
FROM node:22-bookworm-slim

# Senzing EULA. Installing the SDK requires accepting it, and the only correct way
# to do that unattended is to state it in the open:
#   https://senzing.com/end-user-license-agreement/
# There is deliberately NO default — a build must pass
#   --build-arg SENZING_ACCEPT_EULA=I_ACCEPT_THE_SENZING_EULA
# so that acceptance is an explicit act recorded in the workflow that does it,
# and a fork cannot accept Senzing's EULA by accidentally running `docker build`.
ARG SENZING_ACCEPT_EULA
# Pinned, and kept in step with the sibling behavioral-eval job in ci.yml. An
# unpinned CLI silently made local and CI two different measurements once already.
ARG CLAUDE_CLI_VERSION=2.1.259
# The apt-source package. Per sdk_guide: always use senzingrepo, never a
# hand-written dists/stable URL (that one only serves libssl1.1 builds).
ARG SENZING_REPO_DEB=senzingrepo_2.0.2-1_all.deb

ENV DEBIAN_FRONTEND=noninteractive

# bubblewrap + socat are the Linux sandbox backend `claude plugin eval` needs for
# the Bash tool grant; sqlite3 creates the Senzing schema; the rest is what the
# eval and the verifier use.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      bubblewrap \
      curl \
      git \
      jq \
      less \
      procps \
      python3 \
      socat \
      sqlite3 \
      wget \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    if [ "${SENZING_ACCEPT_EULA}" != "I_ACCEPT_THE_SENZING_EULA" ]; then \
      echo "ERROR: build with --build-arg SENZING_ACCEPT_EULA=I_ACCEPT_THE_SENZING_EULA" >&2; \
      echo "       (see https://senzing.com/end-user-license-agreement/)" >&2; \
      exit 1; \
    fi; \
    cd /tmp; \
    wget -q "https://senzing-production-apt.s3.amazonaws.com/${SENZING_REPO_DEB}"; \
    apt-get update; \
    apt-get install -y --no-install-recommends "./${SENZING_REPO_DEB}"; \
    apt-get update; \
    SENZING_ACCEPT_EULA="${SENZING_ACCEPT_EULA}" \
      apt-get install -y --no-install-recommends senzingsdk-runtime senzingsdk-setup; \
    rm -f "/tmp/${SENZING_REPO_DEB}"; \
    rm -rf /var/lib/apt/lists/*; \
    test -f /opt/senzing/er/lib/libSz.so

# Per sdk_guide(platform='linux_apt'): the senzing and senzing-core Python packages
# ship inside senzingsdk-runtime. Do NOT pip install them.
ENV PYTHONPATH=/opt/senzing/er/sdk/python \
    LD_LIBRARY_PATH=/opt/senzing/er/lib

RUN npm install -g "@anthropic-ai/claude-code@${CLAUDE_CLI_VERSION}" \
    && claude --version

# Fault 2 of the three that killed the ubuntu behavioral-eval attempt: the runner
# image had no /run/shm, so the sandbox could not mount its tmpfs. Give it one.
#
# It must be a real DIRECTORY, not a symlink to /dev/shm. A symlink looks like it
# works and does not:
#
#   bwrap: Can't mount tmpfs on /newroot/run/shm: No such file or directory
#
# bwrap's ensure_dir() on the target does stat() (follows the link -> fails) then
# mkdir() (the link exists -> EEXIST, treated as success), so setup sails past the
# only check that would have caught it and dies at the mount(2) instead. The link
# target is ABSOLUTE, and by the time bwrap populates the new root its own "/" is
# the staging tmpfs holding newroot/ and oldroot/ -- which has no /dev at all -- so
# /newroot/run/shm resolves to a /dev/shm that does not exist there. A plain
# directory has no indirection to resolve. 1777 matches /dev/shm's own mode.
RUN mkdir -p /dev/shm /run/shm && chmod 1777 /dev/shm /run/shm

WORKDIR /work
