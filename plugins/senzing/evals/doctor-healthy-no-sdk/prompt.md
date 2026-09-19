---
description: On a host with no Senzing installed, doctor reports "not installed" (➖), never "broken" (❌), and offers install.
tags: [doctor, regression, status-vocabulary]
expected_outcome: >
  doctor fires; the host is probed for real (uname + the platform's install location); the SDK
  row is ➖ not-installed with checks 5-9 cascading to ➖; no ❌ appears anywhere; the install
  skill / sdk_guide(install) is offered. This is the regression that motivated the branch: a
  healthy machine with no SDK was reported as broken from a path probe for the wrong platform.
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Is my Senzing set up? Check this machine.
