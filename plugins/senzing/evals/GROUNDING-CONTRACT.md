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

## A real run has a MINIMUM number of calls, and a faked one does not

The strongest form of this check is not "was the tool called" but **"was it
called as many times as the work requires"**. You cannot load N records without
N `add_record` calls, and you cannot drain a redo queue without
`process_redo_record` calls. Those counts are a property of the work, not of the
route — so a run that invented its result will be short of them no matter how
good the prose is.

That is why `min:` matters more than the tool name here, and why a few of these
carry a floor above 1:

| Work | Minimum it cannot be under |
|---|---|
| loading N records | N `add_record` calls (or a batch whose own count is N) |
| a drained redo queue | ≥1 `process_redo_record`, and `count_redo_records()` == 0 after |
| an 8-step mapping workflow | one `start` plus an `advance` per step reached |
| resolving anything at all | entities < records, which needs the engine, not arithmetic |

The counterpart in `evals-real/verify_truthset.py` is `engine_identified`:
`SzProduct.get_version()` must answer with a VERSION and BUILD_NUMBER, and
`get_license()` reports recordLimit / expireDate / licenseType. Those field
names come from the MCP's own `get_sdk_reference(topic="response_schemas")`,
not from memory — an earlier version of that check invented `addedRecords` and
`redoTriggers`, which appear in no documented schema. **The MCP publishes
schemas for `get_version`, `get_license` and the `with_info` response and none
for `get_stats`**, so call-count evidence belongs in the run's transcript,
where it is observable, rather than in a scrape of an undocumented shape.

Values are reported, never gated: pinning a build number fails the day Senzing
ships a new one, and pinning a license fails on anybody else's entitlement.
What is gated is that the calls answer at all — the difference between "the data
looks right" and "an engine of a known build was running in this process".

## Make the run report its own work — and never tell it the number

The transcript is one place call counts are observable; the run's own report is
the other, and it is the one a user actually reads. The `analyze`, `demo` and
`recipes` skills each require their deliverable to carry `add_record` calls,
`process_redo_record` calls, and the engine's version and build number, read
off the counter in the loop that made the calls.

Two constraints do the work, and dropping either one makes the requirement
theatre:

1. **Read the counter, do not restate the row count.** A file's line count is
   available without an engine; a call counter is not.
2. **Never state the expected number anywhere the skill can see it.** A number
   the skill is told to produce is fabricable and proves nothing. A number it
   must obtain and that is then checked independently is evidence.

`verify_truthset.py` check 7 (`engine_work_reported`) is the grading half. It
derives the truth from the engine and compares — the reported `add_record`
count against the engine's own record count, using the floor above (N records
cannot be loaded with fewer than N calls). It is never compared against a
literal, for the same reason build numbers are reported and not gated: a
literal is a thing that goes stale, and staleness reads as a failure that isn't
one. A run that invented its result has no counter to read, so it comes up
short — or silent, which check 7 treats the same way.
