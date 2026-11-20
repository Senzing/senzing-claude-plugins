---
type: regex
pattern: '\(part 2\)|[Ss]tewardship'
target: last_message
---

# Grader: the Stewardship recipe is named from the real catalog

The catalog entry for `customer-360-stewardship.md` is titled "Customer 360 from CRM + Orders
(part 2)" and describes itself as adding "stewardship screens" to the Customer 360 app. It was
previously titled "Stewardship on CRM + Online Orders", and this grader matched the bare word
"Stewardship" — which upstream then removed from the title, so a CORRECT reply that quotes the
catalog verbatim failed 2 of 2 runs in CI with no plugin defect.

The pattern now accepts either distinctive anchor: the `(part 2)` title suffix, or the word
"stewardship" from the entry's description. Both are specific to this entry and unlikely to be
independently invented. Proven offline: a reply quoting the real entry matches, and the
hallucinated fraud/AML/KYC reply used for the sibling title graders does not.
