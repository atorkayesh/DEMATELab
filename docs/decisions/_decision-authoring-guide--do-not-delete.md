# DO NOT DELETE THIS FILE

This file is the required guide for agents and developers creating or updating decision records in `docs/decisions/`.

## Purpose

A decision record captures one significant architectural or technical choice, the reasons for it, and its consequences. It lets a later reader understand why the system is shaped the way it is without reconstructing old discussions, and prevents settled questions from being reopened by accident.

Write a decision record when a choice:

- constrains future work across more than one module or app (for example the API boundary between `apps/api` and `apps/web`);
- selects a technology, library, data model, or external service;
- defines a rule others must follow (for example "the API is stateless");
- is expensive to reverse, or has been debated and should not be re-litigated without new evidence.

Do not write a decision record for routine implementation detail. Put that in a plan or in code comments.

Before writing one, inspect the relevant code, existing decisions, plans, and reports. Do not record a decision from assumptions alone.

## File Naming

- Use an ISO date prefix: `YYYY-MM-DD`, the date the decision was made.
- Use a short lowercase kebab-case subject that names the decision, not the problem.
- Example: `2026-10-26-neo4j-single-source-of-truth.md`.
- Use `--do-not-delete.md` only for repository guidance files like this one.

## Required Structure

```markdown
# Decision Title Stated As The Choice

**Status:** Proposed | Accepted | Superseded by [title](<file>.md) | Deprecated
**Date:** 26 October, 2026
**Deciders:** People or agents who made the decision

## Decision

The choice in a few direct sentences. State what is done and what is not done.

## Context

The problem, the constraints, and the evidence that forced a decision. Reference code paths, plans, and reports.

## Alternatives Considered

- **Alternative A:** what it was and why it was rejected.
- **Alternative B:** what it was and why it was rejected.

## Consequences

- What becomes easier, what becomes harder, and what must now be maintained.
- Rules that code, plans, and reviews must follow because of this decision.

## Related Work

- Plans, reports, JuGit issues, or merge requests that led to or implement this decision.
```

Add extra sections, such as tables of rules, security boundaries, or rollout conditions, when they make the decision easier to apply.

## Writing Standards

- Lead with the decision. A reader should know the outcome from the first paragraph.
- Keep one decision per record. Split unrelated choices into separate records.
- Separate facts, the decision itself, and assumptions that could invalidate it later.
- Name the conditions under which the decision should be revisited.
- Be concrete: name the libraries, versions, paths, ports, and boundaries involved.
- Do not invent links or evidence. Record missing evidence as an assumption.

## Changing A Decision

- Accepted decisions are not rewritten to say something different. Create a new record and mark the old one `Superseded by` with a link to the new one.
- Small clarifications that do not change the outcome may be edited in place; note the date of the clarification.
- A plan that needs to break an accepted decision must call that out and link a new or superseding decision record.

## Protected Files

- Never delete this guide.
- Do not delete superseded or deprecated decisions; they are the history of why the system changed.
