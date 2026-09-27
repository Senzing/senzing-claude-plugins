---
type: tool_used
tool: Bash
input_match: 'uname|dpkg|rpm -q|/opt/senzing|libSz|senzingsdk|senzing_core|brew (list|--prefix)|scoop|SENZING_ROOT'
---

Review on 7785bfb: the previous pattern ended in a bare `senzing`, which the case's own
mandatory recipe fetch (`curl … raw.githubusercontent.com/senzing/recipes/…`) satisfied, so
a run could skip every host probe and still pass. The bare alternative is gone; the install
and SDK tokens are the specific ones (`senzingsdk`, `senzing_core`, `/opt/senzing`). Checked
against the real doctor traces of the last eval: every run still matches on `uname` /
`brew list` / `/opt/senzing`; no `curl` command and no probe-file cleanup matches.
