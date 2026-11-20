# Patient Fraud - synthetic ingredient set

Four synthetic source systems from **UK private healthcare in London**, built for the
[Patient Fraud Detection in UK Private Healthcare](../../recipes/patient-fraud-uk.md) recipe.

**Synthetic - no real people, no PII.** NHS numbers use the 999 test prefix, phone numbers come from
Ofcom's drama ranges, and every person, clinic, company number and bank account is invented.

| File | Rows | What it is |
|---|---|---|
| `gp_registrations.jsonl` | 511 | NHS GP practice registrations. One record per registered patient; the most trusted source. |
| `pharmacy.jsonl` | 241 | Community pharmacy dispensing records, with the item and last dispensed date. |
| `clinic_billing.jsonl` | 240 | Private clinic claims billed to an insurer. One record per claim, with the treatment, amount and sometimes a refund bank account. |
| `providers.jsonl` | 28 | The private clinics (company number, business details), their directors and other clinicians (GMC number, home details). `PROVIDER_TYPE` says which. |

The files are already in Senzing JSON format, one record per line, so there is no mapping to do.
Seeded in the data: medical identity theft, ghost patients billed by a colluding clinic, and one NHS
number used by two different people, alongside innocent lookalikes (households, house moves,
nicknames) that should not be flagged.
