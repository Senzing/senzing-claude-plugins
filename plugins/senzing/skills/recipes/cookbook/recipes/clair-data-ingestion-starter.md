---
title: Combine Data & Explore Hidden Connections in PPP Loan Data
use_case: foundational
difficulty: Beginner
est_time: ~30m
video: https://youtu.be/S1jq34SD5pE
author: Clair Sullivan
---

# Combine Data & Explore Hidden Connections in PPP Loan Data

**What you'll build:** a single view of the entities across separate data sources - and with it, the
connections nobody could see before. In this case PPP relief loans and Department of Labor
violations, with a third folded in later: the businesses that appear in more than one, and which of
those are physicians. None of these sources share a common key. Names and addresses are enough.

**What it takes:** Beginner · ~30 min once you're set up · runs on your machine · no data to find, the MCP supplies it

![Senzing dashboard for the combined PPP and labor-violation data: 6,390 records grouped into 4,937 businesses and people, 90 of them appearing in both sources, with charts by source and by records per group, a list of the multi-record ones, and a connection graph for a selected one](images/clair-data-ingestion-starter-outcome.png)

*6,390 records across PPP loans and DoL violations become **4,937 businesses and people**, **90** of them appearing in both sources - and you can open any one of them to see its records and connections.*

▶ **[Watch the demo](https://youtu.be/S1jq34SD5pE)** - *"Senzing Cookbook: Combine Data & Explore Hidden Connections in PPP Loan Data."*

## Chef's Note

I wanted the simplest possible on-ramp: prove how easy it is to combine data, with the fewest
moving parts. So I took a couple of liberties. First, I used the **pre-mapped Las Vegas CORDs** -
Collections of Relatable Data, real-world public datasets Senzing has already mapped to its entity
spec and serves straight from the MCP, so there are no files to download and no mapping to do (that
keeps it to three prompts). Second, I made the **visualizer optional** because the merge report
alone already answers the question. We tell the AI *what* we want, not *how* - the kitchen handles
the how. Cook it on your own data by swapping the CORDs for your sources.

## Setup: What you'll need

- **Setup (one-time):** an AI coding assistant, the **Senzing MCP**, and your **Senzing license** - new to this? Start with **[Get Started](../getting-started.md)**.
- **Where it runs:** the prompts stand Senzing up on your own machine. Edit them if you want it somewhere else.
- **Attach your Senzing license file to the chat now** (or drop it in your assistant's working folder).
- **Ingredients:** **PPP Loans** (Paycheck Protection Program) + **US Labor Violations** (Dept. of Labor), both Las Vegas CORD
  sources - the MCP supplies them. *(the **Plus** step adds **NPI**.)*

## Before you begin

- **Use your most capable model** (e.g. Opus for Claude), not a fast or cheap one - these recipes do real, multi-step work.
- **Yours will look different.** Your assistant builds the result fresh each run, so the layout and features vary - a chart or the graph may sit on a different tab. The demo shows the idea, not an exact target.
- **The video is illustrative** - it may show a different assistant or interface; the prompts on this page are what to follow.
- **If something looks wrong, ask the assistant before starting over.** It built this and can inspect it. Say what you expected and what you got - "the dashboard shows 0 customers, check whether the load actually finished" - and tell it to verify against Senzing rather than guess. Paste any error in full.

## Cook: Ingest and load data

**One prompt.** Map both sources, load them, and resolve them into one set of entities. It runs for a few minutes and prints progress as it goes.

**Paste this into your AI assistant:**

```
Goal: Stand up Senzing, load in 2 pre-mapped datasets and generate a merge report.

Hard rules:
- Use the Senzing MCP. Do not rely on general training.
- Do not use sleep/wakeups.
- Use multithreading for loading.
- Use complete datasets.
- Process any redo records so resolution is complete.
- I have provided the Senzing license file: it is attached to this chat, or in your working folder. Do not guess a path - ask me if you can't find it.

Preferences:
- Provide me live status updates on the data ingestion.

Steps:
1. Deploy Senzing using the license file I provided.
2. Load the PPP and Department of Labor Compliance Action snapshots from the Las Vegas Senzing CORDs.
3. When resolution is complete, generate a merge report in markdown showing what Senzing did with the data.
```

**Expected outcome:** live ingest status, then a **merge report** - record and entity
counts, compression ratios, per-source summaries, entity-size distribution, and the **cross-source
matches.** In my run, **92 entities were shared between PPP and DoL** - the cross-source connections.

## Plate: Visualize the results

**One prompt.** Serve the result as a simple web app: a dashboard, search, and a graph for whichever entity you pick. *(Optional - skip it if the merge report already answers your question.)*

**Paste this into your AI assistant:**

```
Goal: Utilizing the data already loaded into Senzing, create an interactive web visualizer including a summary dashboard and the ability to explore entities, including a network graph.

Hard rules:
- Use the Senzing MCP. Do not rely on general training.
- Don't forget the previous Hard Rules.
- If you can't start a local web server the user can open in a browser, build the same visualizer as a single self-contained static HTML file instead, keeping as many of the same features as possible.
- Only use a Senzing mart and/or the Senzing SDK to populate the UX. Never query Senzing's internal engine tables directly.
- Only present the network graph based on a selected entity. Never the whole graph at once.
- Follow the Senzing MCP reporting_guide for query patterns and graph layouts.
- Confirm the visualizer works before finishing: that the local site is responding, or (if you used the static-HTML fallback) that the file was written and opens.

Features:
- On the network graph visualization, present a list of entities - with the cross-source entities at the top - that the user can click on to select which entity to visualize in the graph.
- The UX should include a match summary screen with drill-down options.
- The UX should include a search feature, using the Senzing 'Search' method (including search by name, address, and other attributes).
- Present a network graph with labels to visualize the related entities.
- Keep visualization elements to one screen, no scrolling required, wherever possible.
- Provide a legend for the graph.
```

**Expected outcome:** a local URL → a dashboard with headline metrics, source comparison, match-key
breakdown, **search**, and a **network graph** rendered for a selected entity (with a legend),
cross-source entities at the top.

## Plus: Add additional data

**One prompt.** Bring a third source. It resolves against what is already loaded, and the report and the visualizer pick it up.

**Paste this into your AI assistant:**

```
Goal: Add one more data source to Senzing and update the visualization.

Hard rules:
- Use the Senzing MCP. Do not rely on general training.
- Don't forget the previous Hard Rules.

Steps:
1. Download the NPI (National Provider Index) snapshot from the Las Vegas Senzing CORDs.
2. Use Senzing to combine this data set with the other two data sets already loaded.
3. Refresh the output: if you built the web visualizer in the Plate step, update it; otherwise regenerate the merge report.
```

**Expected outcome:** the report refreshes to **3 sources (~76,000 records)** and **triple-merge
entities** appear - records resolving across all three (which providers took PPP loans *and* had
violations). The visualizer's legend gains NPI and new nodes show up.

## Wrap Up

In ~30 minutes and three prompts you stood up Senzing, resolved two (then three) sources, produced a
merge report, and (optionally) a visualizer - the foundation for almost everything else in the
cookbook. The same recipe works on *your* data: swap the CORDs and ask your own questions.

**Next:** browse [the cookbook](../cookbook.md) for another use case.
