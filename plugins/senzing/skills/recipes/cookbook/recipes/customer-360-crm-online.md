---
title: Customer 360 from CRM + Orders (part 1)
use_case: customer-360
difficulty: Intermediate
est_time: ~45m
video: https://youtu.be/jq5x8Rtrxnc
author: Clair Sullivan
---

# Customer 360 from CRM + Orders (part 1)

**What you'll build:** a single view of customers across data sources - one customer per person,
with the complete order and account history no single system holds, duplicate review, and search. In
this case a CRM export and an online-orders feed, where the same person is two customers: counted
twice, half their history invisible, their real value anyone's guess. Afterwards, one profile each,
plus the duplicates you did not know you had.

**What it takes:** Intermediate · ~45 min once you're set up · runs on your machine · two CSVs to download and attach

![Customer 360 overview dashboard - 1,192 customers built from 1,579 records, 342 of them appearing in both CRM and online orders, and possible duplicates surfaced for review](images/customer-360-crm-online-outcome.png)

*1,579 records become **1,192 customers**, **342** of them appearing in both CRM and online orders, and **177 possible duplicates** come up for review - the whole payoff on one landing page.*

▶ **[Watch the demo](https://youtu.be/jq5x8Rtrxnc)** - *"Senzing Cookbook: Customer 360 from CRM + Orders (part 1)."*

## Chef's Note

A Customer 360 is the thing every business says it wants: one complete, trustworthy view of each
customer, pulled together from every system that knows them. The hard part typically is that the different data sets that are used for these systems are rarely compatible with each other. In addition to typically being messy, they rarely have the things that you need like a common key to bring them together. Sales knows *Edward Flores, customer since 2012, VIP*; the storefront
knows *Ed Flores, six orders, ships to Summerlin*. They are the same people but nothing in the data joins them. That's the gap
entity resolution closes, and this recipe builds the whole thing on top of it.

There are two things worth calling out in this data. First, the two files **don't share field names.** The CRM has already split things out into `first_name` and `last_name` plus a `zip`, while the orders feed hands you a single `customer_name` to break apart, a set of `ship_*` address fields, and a `contact_phone` that's formatted completely differently. That mismatch is on purpose...mapping all of it over to the Senzing spec is part of the recipe, and the MCP's `mapping_workflow` handles that piece for you. And here's a fun wrinkle...the orders feed has no birthdate at all, because an online store wouldn't ever ask for one. So a shared email ends up being the thing that carries a customer across something like a move. Second, I served the whole thing through the **Entity Browser** we set up below, stretched into a full Customer 360 app that shows useful things like each customer's profile, activity, related-customer review, and an overview dashboard.

## Setup: What you'll need

- **Setup (one-time):** an AI coding assistant, the **Senzing MCP**, and your **Senzing license** - new to this? Start with **[Get Started](../getting-started.md)**.
- **Where it runs:** the prompts stand Senzing up on your own machine. Edit them if you want it somewhere else.
- **Attach your Senzing license file to the chat now** (or drop it in your assistant's working folder).
- **Ingredients:** two synthetic source files in [`ingredients/customer360/`](../ingredients/customer360/) - download both, then **attach them to the chat now** (or drop them in your assistant's working folder):
  - **CRM** - `crm.csv`, ~1,000 customers (columnar CRM export: name, address, phone, email,
    plus `customer_since` / `segment` / `lifetime_value`).
  - **ONLINE_ORDERS** - `online_orders.csv`, ~600 accounts (~400 are the same people as CRM
    customers; ~200 are online-only), with `order_count` / `last_order` as payload.

## Before you begin

- **Use your most capable model** (e.g. Opus for Claude), not a fast or cheap one - these recipes do real, multi-step work.
- **Yours will look different.** Your assistant builds the result fresh each run, so the layout and features vary - a chart or the graph may sit on a different tab. The demo shows the idea, not an exact target.
- **The video is illustrative** - it may show a different assistant or interface; the prompts on this page are what to follow.
- **If something looks wrong, ask the assistant before starting over.** It built this and can inspect it. Say what you expected and what you got - "the dashboard shows 0 customers, check whether the load actually finished" - and tell it to verify against Senzing rather than guess. Paste any error in full.

## Cook: Ingest and load data

**Two prompts.** First stand up a local Senzing instance, then map, load and resolve the CRM export
into the customer master your 360 is built on.

**Paste this into your AI assistant:**

```
Goal: Stand up a local Senzing instance, ready to load data.

Hard rules:
- Use the Senzing MCP. Do not rely on general training.
- I have provided the Senzing license file: it is attached to this chat, or in your working folder. Do not guess a path - ask me if you can't find it.
- Deploy Senzing locally using the license file I provided; a local SQLite/in-memory datastore is fine for a POC.
- Confirm the instance is up and ready before finishing.
```

**Expected outcome:** a local Senzing instance, ready to load data into SQLite.

Now the CRM. Unlike a pre-mapped CORD this is a raw export, so **mapping is part of this step** - let
the MCP do it.

**Then paste this:**

```
Goal: Using the existing local Senzing instance, map, load, and resolve the CRM customer export into a customer master.

Hard rules:
- Use the Senzing MCP. Do not rely on general training.
- Map the source with the Senzing MCP mapping_workflow - do not hand-code the Senzing JSON.
- Build the loader with the Senzing MCP sdk_guide.
- Use multithreading for loading.
- Do not use sleep/wakeups.
- Only map and load the requested data (crm.csv). Do not load in the online_orders.csv file yet.
- Map only the fields you need.
- I have provided the source files: crm.csv and online_orders.csv are attached to this chat, or in your working folder. Do not guess a path - ask me if you can't find them.

Preferences:
- Provide me live status updates on the data ingestion.

Steps:
1. Map and load crm.csv as data source CRM. Register the data source as CRM.
2. When complete, give me a short load summary: records loaded and resolved customers.
```

**Expected outcome:** a resolved **customer master** - one entity per customer - that everything else
hangs off. On its own it's just profiles from a single system; the 360 fills in when you serve it (the Plate
step) and add behavior + relationships (the Plus step).

## Plate: Visualize the results

**One prompt.** Serve the customer master as the 360 app itself: a profile per customer, their full history, duplicate review, and search.

**Paste this into your AI assistant:**

```
Goal: Build a Customer 360 web app on the resolved data in the existing Senzing instance, giving one complete view per customer.

Hard rules:
- Keep all previous Hard Rules in force.
- Use the Senzing MCP, not general training.
- Follow the Senzing MCP reporting_guide for every query, entity view, dashboard, and graph pattern.
- Populate the app only from a Senzing data mart and/or the Senzing SDK. Never query Senzing's internal engine tables directly.
- Create a network graph but only render the graph for a selected customer, never the full graph.
- Do not label the relationships in the network graph.
- Route every entry point (search, dashboard drill through, related customer link) to one shared customer detail screen.
- Confirm the app responds before finishing.

Preferences:
- Overview dashboard from the data mart report tables: total customers, records to customers compression, count of customers in more than one source, and a relationships breakdown. Make every metric a drill through that opens the underlying customer list, then the profile.
- Search by name, address, email, or phone.
- Provide a unified customer view showing things like the best known name plus addresses, phones, and emails aggregated across all of the customer's records.
- Source lineage: show the source labelled records behind each customer and allow drilling into each raw source record.
- On the network graph, provide the ability to turn on and off the different nodes in the visualization by clicking on them.
- On the profile, show the CRM payload (customer_since or tenure, segment, lifetime_value) alongside any online payload (order_count, last_order).
- Why match: for any linked pair, show the feature scores that resolved them side by side.
- How: for any merged records, using the Senzing HOW report to show the feature scores that merged them.

Steps:
1. Build a web app to show a Customer 360 view of the resolved data in the existing Senzing instance.
2. Create a network graph that shows the linkages between all records for a selected customer, including merged records of the same person, possibly same records, and possibly related records, (i.e. linked but unmerged customers).
```

**Expected outcome:** a local URL → an overview dashboard and a searchable customer list. Open a
customer and you get the **unified customer profile** with its source-labelled records and the CRM payload
(tenure, segment, value). Right now every customer is a single CRM record and related-customer links are
sparse - a clean baseline that comes alive in the next step.

## Plus: Add additional data

**One prompt.** Adding in a new data set of a completely different nature can be really challenging. Bring the orders feed to the table; Senzing re-resolves it against the customer
master, and the flat profiles turn into true 360s. Its field names differ from the CRM - that's fine, the
`mapping_workflow` reconciles them.

**Paste this into your AI assistant:**

```
Goal: Add the online orders feed to the existing Senzing instance and re-resolve all data across both sources.

Hard rules:
- Use the Senzing MCP. Do not rely on general training.
- Don't forget the previous Hard Rules.
- Use the MCP mapping_workflow to map the data. Do not hand-code the JSON.
- Register the data source as ONLINE_ORDERS. Multithread the load, complete file, no sleep/wakeups, and process all redo records.
- I have provided online_orders.csv: it is attached to this chat, or in your working folder. Do not guess a path - ask me if you can't find it.

Steps:
1. Map and load online_orders.csv as data source ONLINE_ORDERS.
2. Re-resolve so the online accounts link into the existing customers.
3. Refresh the Customer 360 app.
```

**Expected outcome:** the 360 comes alive. Open a customer who shops online and their profile now shows
**order history** (order count, last order) sitting next to their **CRM tenure, segment, and lifetime
value** - one complete view from two systems that never shared a key. Net-new **online-only customers**
appear (coverage the CRM never had). And the **related-customer** links fill in - records the engine
flags as likely the same person (e.g. a former/maiden name) but didn't merge, surfaced as possible
duplicates to review. The overview dashboard's cross-source and relationship numbers climb.

## Wrap Up

In ~45 minutes you built a **Customer 360 database**: two mismatched source systems mapped and resolved
into one unified customer each, served as an app with unified customer profiles, complete CRM-plus-online
history, possible-duplicate review, search, and an overview dashboard. Swap in your own CRM and order data (mind the
PII) and the same three moves - cook, serve, add - give you a 360 on real customers.

**Next:** browse [the cookbook](../cookbook.md) for another use case.
