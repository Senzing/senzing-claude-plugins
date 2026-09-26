# Every skill has a tool that IS its work

A skill that produces its result without the tool that grounds it is not a
faster route to the same answer — it is a different answer, assembled from the
model's recall, about a product whose surface changes between versions. That is
the failure the MUST tier caught: given "dedupe my customer list", opus fired no
skill, deduped six rows by inspection, labeled the method honestly, and was
completely wrong to do it.

So each case asserts the tool that is the substance of its skill. Not the route
— `min: 1`, no `input_match` on the topic, because which topic or dataset a run
needs is its own business.

| Skill | The tool that IS the work | Why |
|---|---|---|
| `install` | `sdk_guide` | install steps are per-platform and versioned; recalled ones rot |
| `analyze` | `mapping_workflow` | the mapping must come from the Entity Specification |
| `demo` | `get_sample_data` | the data is half the claim — invented rows demo nothing |
| `report` | `reporting_guide` | the reporting surface changes between versions |
| `troubleshoot` | `explain_error_code` | an error's cause is a fact, not an inference |
| `ask` | `search_docs` | the answer must carry a source the user can open |
| `build` | `generate_scaffold` / `get_sdk_reference` | argument shapes diverge per binding |
| `poc-planner` | `search_docs` | the plan quotes Senzing's own PoC guidance |
| `recipes` | the live cookbook fetch | a recipe is chef-authored, not reconstructed |

## What this does NOT assert

**That an engine ran.** These are MCP tools. Calling `mapping_workflow` proves
the model asked the server for guidance; it does not prove Senzing started. The
behavioral-eval environment has no `senzingsdk-runtime` installed at all, so a
correct run there ends at the mapping-only exit by design, and demanding engine
evidence would assert something the environment makes impossible.

The other half is gated in `../evals-real/verify_truthset.py` on a host that
really has Senzing: `engine_identified` requires `SzProduct.get_version()` to
answer with a version and a build number — the one check that cannot be
satisfied by a well-formed database somebody else wrote — plus the engine's own
workload counters (records added, redo processed, redo remaining), because
"loaded" and "resolved" are not the same claim.

**Both halves are required and neither substitutes for the other.** MCP without
an engine is what opus did. An engine without the MCP is ungrounded code.

## Before adding one of these, check it can fail

`install-steps-from-mcp` was deleted for asserting `sdk_guide` on a case where
`doctor`'s Step 0 calls it unconditionally — it passed in runs where `install`
was never invoked at all. A grounding assertion on a tool some earlier step
always calls proves nothing. Check what the case's other graders already force
before adding one.
