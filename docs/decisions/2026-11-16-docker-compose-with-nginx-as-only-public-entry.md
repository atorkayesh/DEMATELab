# Docker Compose With Nginx As The Only Public Entry

**Status:** Superseded by [A Shared HTTPS Proxy Serves The App On The VPS](./2026-11-21-shared-https-proxy-on-the-vps.md)
**Date:** 16 November, 2026
**Deciders:** Youpele Michael (with Claude Code)

## Decision

The app runs with Docker Compose: `docker-compose-dev.yml` (api and web with hot reload, ports 50001 and
3000) and `docker-compose-prod.yml` (api with gunicorn, web, and Nginx). In production only Nginx is
published (`${HTTP_PORT:-80}`): `/api/` goes to `api:50001`, `/` to `web:3000`. Nginx resolves its
upstreams per request, so a restarted `web` does not need an Nginx restart (`/` answers 502 meanwhile).
`web` is a regular service in both files (no Compose profile) and Nginx depends on it with
`condition: service_started`, so `make dev` and `make prod` build and start api and web together.

## Context

The VPS runs only DEMATELab, so the fixed ports do not clash there. ice2kg uses the same layout.

## Alternatives Considered

- **Publishing api and web directly:** two public ports, CORS between them, and no single place for TLS.
- **A separate reverse proxy outside Compose:** another piece to configure on the VPS.

## Consequences

- `client_max_body_size 20m` (a 100-factor, 50-expert request is about 10 MB of JSON);
  `proxy_read_timeout 300s` covers AI provider calls (120 s).
- HTTPS is prepared but commented out; it must be enabled before the AI explanation is used on the VPS.
- Ports 50001 and 3000 are fixed on development machines too: another app using them (for example
  ice2kg) must be stopped first; `make dev` checks this and stops with a clear message.

## Related Work

- Plan: [Port The DEMATELab Backend To A Dockerised FastAPI `apps/api`](../plans/2026-11-16-port-backend-to-fastapi-api-plan.md)
- Decision: [Make entrypoint with container-first checks](./2026-11-16-make-entrypoint-with-container-first-checks.md)
