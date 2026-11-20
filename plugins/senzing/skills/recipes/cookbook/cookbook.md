# The Senzing Cookbook

**Identity intelligence, hands-on: entity resolution demos you can build yourself this afternoon.**

Every recipe solves a real use case - hidden connections across datasets, a customer 360, compliance screening - and leaves you with a running application, not a slide about one. You don't write the code: you paste a few plain-English prompts into the AI coding assistant you already use, and watch it build.

Three things do the work. **Senzing** finds the records that refer to the same person or organization, even when the sources share no common key. The **Senzing MCP** teaches your assistant how to drive Senzing properly, instead of inventing its own approach. And **your favorite LLM** turns each prompt into a working application. The license is free, the quickest recipe takes about 30 minutes, and every one of them works the same way on your own data.

Your result won't look identical to the demo - the assistant builds it fresh each run - but it will do the same job.

> **First time?** Do the one-time [setup](getting-started.md) - an AI coding assistant, the **Senzing MCP**, and a free **Senzing license**. Once. After that, every recipe is paste-and-go.

**Levels:**

- **Beginner** needs nothing but the one-time setup.
- **Intermediate** adds data files to attach, or an earlier recipe first.
- **Advanced** means production infrastructure and real cloud charges.

Every recipe says what it takes at the top. Times are elapsed, start to finish, including the time your AI assistant spends building.

## The recipes

### [Combine Data & Explore Hidden Connections in PPP Loan Data](recipes/clair-data-ingestion-starter.md)
*Foundational · Beginner · Local · ~30m · Clair Sullivan*

**What you'll build:** a single view of the entities across separate data sources - and with it, the connections nobody could see before. In this case PPP relief loans, Department of Labor violations and a third set folded in later: the businesses that appear in more than one, and which of those are physicians.

### [Customer 360 from CRM + Orders (part 1)](recipes/customer-360-crm-online.md)
*Customer 360 · Intermediate · Local · ~45m · Clair Sullivan*

**What you'll build:** a single view of customers across data sources - one customer per person, with the complete order and account history no single system holds, duplicate review, and search. In this case a CRM export and an online-orders feed, where the same person is two customers.

### [Customer 360 from CRM + Orders (part 2)](recipes/customer-360-stewardship.md)
*Customer 360 · Intermediate · Local · ~20m · Clair Sullivan*

**What you'll build:** add stewardship screens to the Customer 360 app - where a person makes the calls that need human judgment, with each verdict recorded and surviving the next reload. Do the Customer 360 recipe first.

### [Patient Fraud Detection in UK Private Healthcare](recipes/patient-fraud-uk.md)
*Fraud · Intermediate · Local · ~45m · Jeff Butcher*

**What you'll build:** a fraud investigation app - sources resolved into who is really who, fraud patterns described in plain English found in them, and an investigator's queue with the evidence behind every suspect. In this case GP, pharmacy, private clinic billing and provider data hiding medical identity theft, ghost patients and a reused NHS number.

### [Healthcare Exclusion Screening](recipes/nigel-healthcare-aws-entity-browser.md)
*Compliance · Advanced · AWS · a few hours · Nigel DeFreitas*

**What you'll build:** the check that catches someone on a watchlist before you pay or hire them, matching people rather than strings. In this case every Las Vegas healthcare provider against the OIG exclusion list, every hit flagged. The penalties for missing one are federal.
