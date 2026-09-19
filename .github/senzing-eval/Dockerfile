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
RUN mkdir -p /dev/shm && ln -sfn /dev/shm /run/shm

WORKDIR /work
