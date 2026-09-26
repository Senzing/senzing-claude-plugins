---
type: tool_used
tool: mcp__plugin_senzing_senzing__reporting_guide
min: 1
---

# Grader: a REPORT run consulted the reporting guide

Every skill has one MCP tool that **is** the work it claims to do — `install`
needs `sdk_guide`, anything that maps needs `mapping_workflow`, anything that
reports needs `reporting_guide`. Before this, `report-empty-instance` asserted
that `mapping_workflow` was **not** called (correct — report is read-only and
must never load) and asserted nothing at all about where its reporting method
came from. A run that answered the question out of the model's own knowledge of
SQL and the SDK passed.

`report/SKILL.md:35-36,51` mandates it: the entity count comes from
`reporting_guide`'s `export` pattern, and analytics/quality work comes from its
`reports`/`entity_views`/`data_mart` topics. So an ungrounded report is not a
different route to the same answer — it is a different answer, assembled from
recall, about a product whose reporting surface changes between versions.

Not vacuous, and that was checked: the four existing graders in this case are
`Skill:report` fired, `Write` = 0, `mapping_workflow` = 0, and a regex on the
final message. None of them causes `reporting_guide` to be called, and the
run that prompted this work reached its answer without it.

Deliberately `min: 1` and no `input_match`: which topic a run needs depends on
what was asked, and pinning one would be a route assertion. The obligation is
that the reporting method came from Senzing rather than from memory — any topic
satisfies that.

Note this case's repository is EMPTY, and that does not excuse the call:
`report/SKILL.md` is explicit that "the repository is empty" is a reason to RUN
this skill, never a reason to answer without it. Establishing the count and
refusing to invent one IS the work.
