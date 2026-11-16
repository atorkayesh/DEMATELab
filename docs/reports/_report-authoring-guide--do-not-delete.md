# DO NOT DELETE THIS FILE

This file is the required guide for agents and developers creating or updating reports in `docs/reports/`.

## Purpose

A report records the findings of an investigation, assessment, or evaluation so that plans and decisions can rely on evidence rather than memory. Typical reports include:

- assessments of a technology, library, or external data source (for example a publication API or Scopus);
- audits of existing code, such as what `qt-app/` does and what must be ported to `apps/`;
- data-quality findings about harvested or integrated metadata;
- evaluations of query or chat quality, performance measurements, and debugging investigations.

Reports cover this repository, its graph, and its data. Knowledge from outside the project (papers, external tools, approaches) belongs in `docs/research/` instead.

A report describes what was found. It does not by itself decide or schedule work: link it from a decision in `docs/decisions/` or a plan in `docs/plans/` when it leads to action.

## File Naming

- Use an ISO date prefix: `YYYY-MM-DD`, the date of the investigation.
- Use a short lowercase kebab-case subject.
- Use the suffix `-report.md`.
- Example: `2026-11-16-qt-app-inventory-report.md`.
- Use `--do-not-delete.md` only for repository guidance files like this one.

## Required Structure

```markdown
# Report Title Stated As The Main Finding Or Question

**Date:** 26 October, 2026
**Author:** Agent, developer, or team name
**Scope:** What was examined, and the commit, data snapshot, or versions it applies to

## Summary

The direct answer or main findings first, in a few sentences.

## Questions

The specific questions the report set out to answer.

## Method

What was inspected or run: files, commands, queries, datasets, external documentation, and versions.

## Findings

Findings grouped by question or theme. Each finding states the evidence behind it.

## Limitations

What was not checked, assumptions made, and what could change the conclusions.

## Recommendations

Suggested next steps, with links to any plans or decisions they produced.

## References

Links to sources, code paths, issues, and related plans or decisions.
```

## Writing Standards

- Answer first. Put the conclusion in the summary, then support it.
- Pin evidence: name the commit, file paths and line ranges, dataset or graph snapshot, library and API versions, and dates of external sources.
- Separate observed facts, interpretation, and recommendations. Do not present a hypothesis as a finding.
- State confidence honestly. Say what was verified by running or querying something, and what was only read in documentation.
- Bound claims to what the evidence supports. A sample of records is not the whole graph; one successful API call is not a guarantee.
- Use tables when comparing options, sources, or fields.
- Do not include secrets, credentials, or personal data beyond what is necessary; summarize people data rather than pasting it.
- Do not invent links, numbers, or citations.

## Updating Reports

- Reports are snapshots. When findings become outdated, add a dated note at the top or write a new report and link it, rather than silently rewriting old conclusions.

## Protected Files

- Never delete this guide.
