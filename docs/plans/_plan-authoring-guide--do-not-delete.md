# DO NOT DELETE THIS FILE

This file is the required guide for agents and developers creating or updating plans in `docs/plans/`.

## Purpose

Plans should preserve the reasoning behind non-trivial work so another agent or developer can implement, review, or resume it without reconstructing the entire conversation.

Before creating a plan, inspect the relevant code, existing documentation, decisions in `docs/decisions/`, reports in `docs/reports/`, issues, tests, and recent changes. Do not write a plan from assumptions alone.

## File Naming

- Use an ISO date prefix: `YYYY-MM-DD`.
- Use a short lowercase kebab-case subject.
- Use the suffix `-plan.md` for normal plans.
- Use `--do-not-delete.md` only for files that must remain as repository guidance or fixtures.
- Example: `2026-10-26-fastapi-graph-endpoint-plan.md`.

## Required Plan Structure

Every plan must contain these sections in this order unless a section is genuinely not applicable:

```markdown
# Descriptive Plan Title

**Date:** 26 October, 2026
**Status:** Proposed | In progress | Implemented | Deferred
**Owner:** Agent, developer, or team name

## Summary

Short explanation of the change and its expected user or developer impact.

## Related Work

- Issue or merge request: [Reference](<link to the issue>)
- Decision: [Decision title](../decisions/<file>.md)
- Report: [Report title](../reports/<file>.md)
- Note or Kanban card, if one exists: [Title](bigbud-note://<note-id>)

## Problem

Evidence-backed description of the current behavior, affected users, and why it matters.

## Goals

- Observable outcomes this plan must achieve.

## Non-Goals

- Explicitly excluded behavior and scope.

## Current State

Relevant architecture, code paths, constraints, and existing behavior with file and line references.

## Phases

### Phase 1: ...

Implementation steps, dependencies, and expected result.

### Phase 2: ...

Implementation steps, dependencies, and expected result.

## Risks And Decision Gates

Risks, unresolved decisions, and conditions that must be satisfied before later phases begin.

## Testing And Validation

Unit tests, integration tests, manual checks, and required repository commands.

## Acceptance Criteria

- Specific conditions that demonstrate the plan is complete.

## Open Questions

Questions that need user, stakeholder, or domain-owner decisions.
```

## Related Work Links

Link the plan to the source of the work whenever one exists. Prefer a stable reference over copying the entire discussion into the plan.

- Link JuGit issues and merge requests for tracked work.
- Link the decisions in `docs/decisions/` that constrain the plan, and the reports in `docs/reports/` that supplied its evidence.
- Include the title and purpose of each reference, not only an opaque identifier.
- If no related reference exists, write `None identified` and explain why.
- Do not invent IDs or links. Record the missing reference as an open question when the work should have one.

## Project Rules Every Plan Must Respect

- **Numerical parity with the Qt app.** For the same input, every number the new app computes equals the legacy Qt app's. Maths changes need regenerated parity fixtures from `qt-app/` (`scripts/generate_parity_fixtures.py`) and an explicit decision; never loosen the parity tolerance to make a test pass.
- **`qt-app/` is read-only.** It is the legacy PySide6 app and the reference implementation. Do not change it as part of `apps/` work.
- **`apps/` must not depend on `qt-app/`.** Do not import from, read files in, or start scripts from `qt-app/`. Copy or rewrite what is needed into `apps/` and name the original file in the plan. Only `scripts/generate_parity_fixtures.py` runs against `qt-app/`.
- **Backend:** Python with FastAPI in `apps/api` (stateless). **Frontend:** TypeScript with TanStack Start in `apps/web`.
- Respect the decisions recorded in `docs/decisions/`. If a plan needs to change one, say so explicitly and add or supersede a decision record.

## Writing Standards

- Write for the next engineer who must implement the work, not only for the original requester.
- Separate observed facts, decisions, hypotheses, and open questions.
- Reference exact repository paths and line ranges for important behavior.
- Describe user-visible behavior before implementation details.
- Prefer the smallest safe change and state why broader alternatives were rejected.
- Preserve existing working behavior and name the tests or checks that protect it.
- Make phase dependencies explicit. A later phase must not silently assume an unverified earlier phase.
- Include rollback or failure behavior for operations that change persisted state, such as graph writes, schema or constraint changes, and bulk imports.
- Define how retries, partial completion, duplicate input, and uncertain outcomes behave for harvesting and integration steps; graph writes should be idempotent where practical.
- Record data-quality, privacy, authorization, and data-loss considerations when they can affect the feature, especially for people data.
- Use past-tense or imperative action language consistently in implementation steps.
- Keep plans current: update `Status`, dates, completed phases, validation results, and links when implementation changes.

## Phase Guidance

Each phase should identify its goal, exact scope, dependencies, files or modules likely to change, tests, and exit criteria.

- Start with investigation or observability when the root cause is uncertain.
- Make the first implementation phase independently safe to ship whenever possible.
- Keep risky migrations, destructive graph operations, bulk deletes, and broad refactors behind explicit decision gates.
- Do not claim an external source (for example a publication database, Scopus, or an LLM provider) supports a capability until its documentation or a real response proves it.
- When porting behavior from `qt-app/`, name the original file and line range and state what is kept, changed, or dropped.
- State what must not change.

## Testing And Validation Guidance

Plans must identify tests at the layer where each failure can occur:

- Schema tests for request and response models and serialized data.
- Unit tests for pure parsing, normalization, matching, and query-building logic.
- Parity tests against fixtures generated from `qt-app/`, and integration tests for API endpoints.
- Frontend tests for user-visible controls, loading and error states, and accessibility.
- Manual checks for features that need a live external service or a populated graph.

Use the commands documented for each app (`apps/api` and `apps/web`). Record the exact commands that passed, and any failures that are unrelated, pre-existing, or blocked by unavailable services.

## Protected Files

- Never delete this guide.
- Before removing old plans, confirm they are implemented or intentionally superseded, and preserve any user-designated exceptions.
