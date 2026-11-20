---
type: tool_used
tool: Read
input_match: 'cookbook/recipes/customer-360-crm-online\.md'
---

# Grader: the CORRECT recipe was read from the bundle, not a wrong or hallucinated one

The catalog carries two Customer 360 entries — `customer-360-crm-online.md` (the one the user
named) and `customer-360-stewardship.md` (an add-on recipe for a different, later step). This
grader fails a run that opens the wrong id, opens nothing and improvises the recipe from memory,
or invents a plausible-but-nonexistent id: a `Read` of `customer-360-stewardship.md` does not
match, nor does a non-reading `{"command": "echo starting the customer 360 recipe"}`.

The recipe is read from the plugin's bundled `cookbook/recipes/`, not downloaded — this replaced
`correct-recipe-fetched`, which matched a `Bash` command containing the filename and so required
the very `curl` the directory objected to.
