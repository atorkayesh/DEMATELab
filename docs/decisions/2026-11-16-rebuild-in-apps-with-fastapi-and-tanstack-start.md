# Rebuild DEMATELab In `apps/` With FastAPI And TanStack Start

**Status:** Accepted
**Date:** 16 November, 2026
**Deciders:** Youpele Michael (with Claude Code)

## Decision

DEMATELab is rebuilt as a web app in `apps/`: a FastAPI service in `apps/api` (Python 3.13) holds every
non-UI capability of the Qt app, and a TanStack Start app in `apps/web` provides the interface. The
PySide6 desktop app stays in `qt-app/` as the legacy app and the numerical reference; `apps/` never
imports from or reads `qt-app/`. For the same input every number equals the Qt app's, proven by frozen
fixtures generated from `qt-app/` (`scripts/generate_parity_fixtures.py`).

## Context

All logic ran inside the Qt desktop app, served over noVNC in Docker: no HTTP API, no tests, and part of
the business logic (weight correction, summary numbers, XLSX export, heatmaps, workbook mapping) lived in
GUI files. The same layout (FastAPI + TanStack Start in `apps/`, Docker, Nginx, Make) is already in use in
ice2kg, so its conventions and tooling are copied.

## Alternatives Considered

- **Keep the Qt app behind noVNC:** one shared session per URL, unencrypted VNC, no API for other clients.
- **Wrap the Qt modules in an API without porting:** the logic is mixed with widgets, and the API would
  depend on PySide6 and on the legacy package layout.
- **A single full-stack framework:** would drop the Python numerical stack (numpy, pandas, scikit-learn,
  matplotlib) the solvers and charts depend on.

## Consequences

- Maths changes need regenerated parity fixtures and a decision; the parity tolerance is `atol=1e-12`.
- `qt-app/` changes are not picked up by `apps/`; the port names its Qt source files and lines.
- The frontend depends on the API contract in the backend plan.

## Related Work

- Plan: [Port The DEMATELab Backend To A Dockerised FastAPI `apps/api`](../plans/2026-11-16-port-backend-to-fastapi-api-plan.md)
- Plan: [Rebuild The DEMATELab UI In TanStack Start](../plans/2026-11-16-rebuild-ui-in-tanstack-start-plan.md)
