# Stateless API With Server-Rendered Charts

**Status:** Accepted
**Date:** 16 November, 2026
**Deciders:** Youpele Michael (with Claude Code)

## Decision

The API stores nothing. Every endpoint that needs results (analysis, summary, XLSX export, charts, AI
explanation) receives the full analysis request and recomputes it; solving takes milliseconds at the Qt
limits (100 factors, 50 experts). Charts are rendered on the server with matplotlib in the Qt style (the
same drawing code, colours, and Inter font) and returned as PNG: an 8 x 6 figure, `dpi=100` as shown in
the Qt tab, or `dpi=300` cropped tight as the Qt PNG export.

## Context

The Qt app draws its causal diagram and heatmaps with matplotlib; reproducing them in the browser would
re-implement the layout and risk visual drift. A stateless API needs no database, cache, or session
store, and scales by adding gunicorn workers.

## Alternatives Considered

- **Cache results by id:** saves recomputation, but adds state, expiry, and memory limits for no
  measurable gain at these sizes.
- **Client-side charts:** more interactive, but not the Qt look and a second implementation of the plots.

## Consequences

- Charts use matplotlib's object-oriented `Figure` API only (no pyplot global state), so concurrent
  requests are safe; gunicorn workers add process isolation.
- Request bodies can reach about 10 MB; Nginx allows 20 MB.
- Results are not shareable by link; the frontend keeps the request to re-run it.

## Related Work

- Plan: [Port The DEMATELab Backend To A Dockerised FastAPI `apps/api`](../plans/2026-11-16-port-backend-to-fastapi-api-plan.md)
