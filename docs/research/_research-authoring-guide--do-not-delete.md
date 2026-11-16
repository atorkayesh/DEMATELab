# DO NOT DELETE THIS FILE

This file is the required guide for agents and developers creating or updating research notes in `docs/research/`.

## Purpose

A research note collects and evaluates knowledge from **outside** this repository so that plans and decisions can build on it. Typical research notes include:

- literature and prior work, for example DEMATEL variants, fuzzy and grey number arithmetic, threshold methods such as MMDE;
- surveys of approaches, for example natural-language-to-Cypher querying, retrieval-augmented chat over graphs, or graph visualization libraries;
- comparisons of external tools, libraries, standards, or services (charting libraries, AI providers, spreadsheet formats);
- background a reader needs to understand the domain before a plan can be written.

### Research, reports, and decisions

| Folder | Answers | Evidence comes from |
| --- | --- | --- |
| `docs/research/` | What is known or possible out there? | Papers, documentation, standards, external tools, small experiments |
| `docs/reports/` | What did we find in our system or data? | This repository, the graph, our logs and measurements |
| `docs/decisions/` | What did we choose and why? | Research notes, reports, and discussion |

A research note does not decide or schedule work. When it leads to action, link it from a decision in `docs/decisions/` or a plan in `docs/plans/`. If the work turns into an investigation of this codebase or its data, write a report instead.

## File Naming

- Use an ISO date prefix: `YYYY-MM-DD`, the date the research was started.
- Use a short lowercase kebab-case topic.
- Use the suffix `-research.md`.
- Example: `2026-10-26-natural-language-to-cypher-approaches-research.md`.
- Use `--do-not-delete.md` only for repository guidance files like this one.

## Required Structure

```markdown
# Research Topic Stated As The Question

**Date:** 26 October, 2026
**Author:** Agent, developer, or team name
**Status:** In progress | Complete | Outdated
**Scope:** What is covered and what is deliberately left out

## Summary

The short answer or current state of knowledge first, in a few sentences, with how confident it is.

## Question

The question being researched and why it matters for DEMATELab.

## Sources And Method

How sources were found and selected: search terms, databases, documentation versions, experiments run, and the date each source was accessed.

## Findings

Findings grouped by theme or by option. Each finding names its source.

## Comparison

A table comparing options against the criteria that matter here, when the research compares alternatives.

## Relevance To DEMATELab

What the findings mean for this project: what could be reused, what does not fit, and what is still unknown.

## Open Questions

What remains unanswered and what would answer it.

## References

Full references: authors, title, venue or publisher, year, and DOI or URL.
```

Leave out the Comparison section when the research does not compare options.

## Writing Standards

- Answer first. Put the current state of knowledge in the summary, then support it.
- Cite every factual claim. Prefer primary sources (papers, official documentation, standards) over blog posts and summaries.
- Record versions and access dates for software, APIs, and web pages; they change.
- Separate what a source states, what you infer from it, and what you tested yourself.
- State confidence honestly, and bound claims to what the sources support. One benchmark or one paper is not a consensus.
- Prefer DOIs for papers. Do not invent links, citations, authors, or numbers. If a source cannot be verified, say so.
- Keep quotations short and attributed; summarize instead of copying long passages.
- Do not include secrets, credentials, or personal data.

## Updating Research

- Research notes can be extended while `Status` is `In progress`.
- When a note is superseded by newer findings, set `Status: Outdated`, add a dated note at the top linking the newer note, and keep the old one.

## Protected Files

- Never delete this guide.
