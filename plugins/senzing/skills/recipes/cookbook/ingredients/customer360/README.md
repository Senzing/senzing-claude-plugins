# Customer 360 — synthetic ingredient set

Two synthetic source systems for a **big-ticket electronics retailer**, built for the
[Customer 360 from CRM + Orders](../../recipes/customer-360-crm-online.md) recipe.

**Synthetic — no real people, no PII.** Las Vegas-flavored addresses, generated from a fixed seed.

| File | Rows | What it is |
|---|---|---|
| `crm.csv` | 992 | CRM export (columnar). One row per customer. |
| `online_orders.csv` | 590 | Online-orders feed. One row per order — a repeat buyer has several. |

The two files deliberately **don't share field names** — mapping them to the Senzing spec is part
of the recipe.
