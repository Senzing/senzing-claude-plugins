---
title: Healthcare Exclusion Screening
use_case: compliance
difficulty: Advanced
est_time: a few hours
video: https://youtu.be/7z8HHvsPIJ0
author: Nigel DeFreitas
---

# Healthcare Exclusion Screening

**What you'll build:** the check that catches someone on a watchlist before you pay or hire them -
screening that matches people rather than strings, because names never line up exactly. In this case
every Las Vegas healthcare provider against the OIG exclusion list, built on AWS, every hit flagged.
The penalties for missing one are federal.

**What it takes:** Advanced · a few hours once you're set up · runs in your own AWS account, **real charges**

![Entity Browser dashboard showing 174,468 providers built from 223,886 records, 663 of them appearing in both sources, 1.3 records each on average, with a searchable, filterable provider list](images/nigel-healthcare-aws-entity-browser-outcome.png)

*223,886 provider records become **174,468 providers**, **663** of them appearing in both sources - browse, search, or filter straight to the **Excluded** ones flagged against the OIG list.*

▶ **[Watch the demo](https://youtu.be/7z8HHvsPIJ0)** - *"Senzing Cookbook: Excluded Las Vegas Doctors."*

## Chef's Note

I built this in a real **AWS production kitchen**, not a laptop - the goal was an operational
compliance system that keeps running, not a one-off demo. A couple of liberties: I **borrowed
Clair's network-graph** idea rather than reinvent it, and I **limited the OIG
load to last names starting "A"** to keep the walkthrough snappy (drop that filter to load them
all). The payoff was real: the exclusions overlay surfaced actual excluded Las Vegas doctors.

## Setup: What you'll need

- **Setup (one-time):** an AI coding assistant, the **Senzing MCP**, and your **Senzing license** - new to this? Start with **[Get Started](../getting-started.md)**.
- **Where it runs:** your own AWS account - production CDK/RDS/ECS/Glue/Step Functions, IAM via STS, AWS Docs MCP, creds. A substantial build that bills real charges while it runs.
- **Attach your Senzing license file to the chat now** (or drop it in your assistant's working folder).
- **Ingredients:** **NPPES NPI** + **OpenData.org** (Las Vegas), pre-staged in
  `s3://npi-public-data-input-raw/`. *(the **Plus** step adds **OIG LEIE exclusions**.)*

## Before you begin

- **Use your most capable model** (e.g. Opus for Claude), not a fast or cheap one - these recipes do real, multi-step work.
- **Yours will look different.** Your assistant builds the result fresh each run, so the layout and features vary - a chart or the graph may sit on a different tab. The demo shows the idea, not an exact target.
- **The video is illustrative** - it may show a different assistant or interface; the prompts on this page are what to follow.
- **If something looks wrong, ask the assistant before starting over.** It built this and can inspect it. Say what you expected and what you got - "the dashboard shows 0 customers, check whether the load actually finished" - and tell it to verify against Senzing rather than guess. Paste any error in full.

## Cook: Ingest and load data

**One prompt.** Map both sources, deploy the AWS pipeline, run entity resolution, export. This is the long one: CDK stacks go up, the load runs for a while, and it pauses part-way for you to approve the mappings.

**Paste this into your AI assistant:**

```
Important: Use the Senzing MCP for all Senzing work. Use the AWS Documentation MCP for any AWS CDK questions.

Goal: Map two pre-staged healthcare provider datasets, deploy a fully automated AWS CDK pipeline, run Senzing V4 entity resolution, and export the resolved entity graph.

Hard rules:
- Use the Senzing MCP's mapping_workflow for all field mappings - not training knowledge.
- Use the Senzing MCP's sdk_guide for all SDK calls and loader patterns.
- Check the Senzing MCP anti-patterns docs before implementing the loader. Use a production-grade loader - not a demo or single-threaded process.
- Process redo records so resolution is complete.
- Use CDK for all AWS infrastructure. Prefix every resource with npi-public-data-* and deploy the CDK to AWS region us-east-1. I acknowledge and accept all AWS charges for these actions.
- Deploy using IAM role npi-public-data-deploy via AWS STS. Include a CDK-aware IAM policy template.
- Split large IAM policies by domain so each is under the 6,144 character limit.

Data sources (pre-staged in s3://npi-public-data-input-raw/):
- NPPES NPI: licensed healthcare providers, Las Vegas, NV
- OpenData.org: commercial provider enrichment, Las Vegas, NV

License & Credentials: I have provided the Senzing license file - it is attached to this chat, or in your working folder; do not guess a path, ask me if you can't find it. The RDS password is in ./Credentials/creds.txt.

Steps:
1. Inspect both source files and propose field mappings using the Senzing MCP mapping_workflow. Show the mappings for my review before proceeding.
2. Once I approve, synthesize and deploy the CDK stacks (storage, networking, database, ECS, Glue ETL, Step Functions orchestration).
3. Run the Senzing V4 entity resolution pipeline. Print progress every few seconds as records load.
4. When fully loaded, export the resolved entity graph to S3 and print a summary match report.
```

**Expected outcome:** it proposes **field mappings and pauses for your review** - approve to
continue. Then CDK stacks deploy, the pipeline loads with progress printed, the graph exports to S3,
and a summary report prints. My run: **~223,000 records → ~174,000 entities; 663 cross-source overlaps.**

## Plate: Visualize the results

**One prompt.** Serve it as an Entity Browser: search, source labels, a graph, and why any two records matched.

**Paste this into your AI assistant:**

```
Important: Use the Senzing MCP's reporting_guide for this task.

Goal: Build an Entity Browser web UI that loads the resolved entity export from the previous step and lets users explore the identity graph.

Hard rules:
- Follow the Senzing MCP reporting_guide for all query patterns, graph layouts, and why-match interfaces.
- Populate the UX only from a Senzing data mart and/or the Senzing SDK. Never query Senzing's internal engine tables directly.
- Only render the network graph for a selected entity. Never the whole graph at once.

Features:
- Search across resolved entities by name, entity ID, or exclusion status (using the Senzing query interface).
- Show resolved entities with their linked source records, clearly labelled by source (NPPES NPI or OpenData.org).
- Network graph with labels to visualize the identity graph and entity-record relationships.
- "Why match?" with feature scores for any selected entity pair.
```

**Expected outcome:** an Entity Browser web UI - search by name / entity ID / exclusion status;
entities with **source-labeled** records; a labeled **network graph**; **"Why match?"** with feature
scores for a selected pair.

## Plus: Add additional data

**One prompt.** Add the exclusions list. It re-resolves against the providers already loaded, and the browser updates.

**Paste this into your AI assistant:**

```
Important: Use the Senzing MCP for this task.

Goal: Add OIG LEIE exclusions as a third data source, then flag and visually highlight any resolved entities linked to OIG exclusion records.

Steps:
1. Map and load records whose last name start with the letter A from the OIG LEIE exclusions dataset into the existing identity graph using the same production-grade loader as before (use the Senzing MCP mapping_workflow).
2. Update the Entity Browser to:
   - Show a clear exclusion flag or badge on any entity linked to an OIG exclusion record.
   - Add exclusion status as a filterable field in the search interface.
   - Visually highlight OIG-linked entities in the network graph (e.g., a distinct color or node border).
3. Print updated match statistics: how many resolved entities now have an OIG exclusion link, broken down by individual vs. organization.
```

**Expected outcome:** OIG records load and **re-resolve** against the existing providers, surfacing
**excluded doctors** (the video found **Victor C. Sutton** and **Everton's Place**, both tied to
real Nevada medical-fraud cases). The Entity Browser updates: **exclusion badges**, an
**exclusion-status filter**, **highlighted** OIG-linked nodes; updated stats print (individual vs. org).

## Wrap Up

In a few hours you built a **production** healthcare-provider compliance system on AWS: a resolved
provider repository, an Entity Browser over it, and an OIG-exclusion overlay that surfaced real
excluded providers. Not a demo that stops when you close the laptop - it keeps running.

**Next:** browse [the cookbook](../cookbook.md) for another use case.
