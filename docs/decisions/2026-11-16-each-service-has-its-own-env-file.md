# Each Service Has Its Own Env File

**Status:** Accepted
**Date:** 16 November, 2026
**Deciders:** Youpele Michael (with Claude Code)

## Decision

Each service reads only its own env file, created from the `.env.example` next to it (`make setup`):
`apps/api/.env` (`APP_ENV`, `CORS_ORIGINS`, `WEB_CONCURRENCY`) and, with the frontend, `apps/web/.env`.
There is no root `.env`. Compose overrides only what Docker decides (`APP_ENV`). The legacy Qt app keeps
`qt-app/DEMATELab/.env`.

## Context

A shared env file leaks settings into services that do not need them, and makes it unclear which
service a variable belongs to. ice2kg follows the same rule.

## Alternatives Considered

- **One root `.env` for every service:** simpler to create, but every container receives every value.

## Consequences

- `make setup` skips files whose `.env.example` does not exist yet.
- AI provider keys are never in an env file (see the AI keys decision).
- `.env` files are never committed.

## Related Work

- Plan: [Port The DEMATELab Backend To A Dockerised FastAPI `apps/api`](../plans/2026-11-16-port-backend-to-fastapi-api-plan.md)
- Decision: [AI keys are supplied per request](./2026-11-16-ai-keys-supplied-per-request.md)
