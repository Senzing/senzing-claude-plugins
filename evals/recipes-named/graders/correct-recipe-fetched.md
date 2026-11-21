---
type: tool_used
tool: Bash
input_match: 'customer-360-crm-online\.md'
---

# Grader: the CORRECT recipe was fetched, not a wrong or hallucinated one

The catalog carries two Customer 360 entries — `customer-360-crm-online.md` (the one the user
named, verified live against `senzing/recipes@main`) and `customer-360-stewardship.md` (an add-on
recipe for a different, later step). This grader fails a run that fetches the wrong id, fetches
nothing and improvises the recipe from memory, or invents a plausible-but-nonexistent id — proven
offline: a synthetic fetch of `customer-360-stewardship.md` does not match, nor does a
non-fetching `{"command": "echo starting the customer 360 recipe"}`.
