---
type: regex
pattern: '(?:license\s+file|evaluation\s+(?:one|license)|ready\s+to\s+cook\s+once)'
match: not_contains
flags: i
target: last_message
---

# Grader: the install hand-off asks nothing about a license file and does not say the cook is waiting

On a host with no Senzing SDK the reply is `install`'s message: the plan, the EULA, one question. A run (CI run
37994167572, `with[1]`) re-read the recipe after `Skill(install)`, counted ~1,600 records, and ended "it's ready to cook
once Senzing is installed ... this recipe needs a real Senzing license ... have your license file ready; if not, I can
request a free evaluation one". `criteria` failed it 3 of 3. Whether a license is needed is `doctor`'s call after a
verified install (`install/SKILL.md`, Licensing); before that the EULA is the only license matter. This is the
deterministic backstop for the phrasing, not a new rule.

Fixtures: `pattern-fixtures/no-license-ask.yaml`.
