---
type: tool_used
tool: Read
input_match: 'cookbook/cookbook\.md'
---

# Grader: the catalog was actually READ from the bundle, not recalled

The cookbook ships inside the plugin (`plugins/senzing/skills/recipes/cookbook/`) because the
Claude directory refuses a plugin that downloads what it executes. The skill therefore opens the
catalog with `Read`; it never fetches it. A model that answers from training data makes zero
matching `Read` calls, so this grader has `min: 1` (the default) and fails that run.

This replaced `catalog-fetched`, which required `Bash` `curl[\s\S]*cookbook\.md`. That grader would
now fail every CORRECT run, because the skill no longer has any `curl` to make — see
`no-recipe-curl` and `no-recipe-webfetch`, which assert the opposite on purpose.
