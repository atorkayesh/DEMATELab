# Serve DEMATELab And Policy Coherence Kit Through One HTTPS Proxy, And Switch Both Repos To just

**Date:** 21 November, 2026
**Status:** Implemented
**Owner:** Claude Code for Youpele Michael

## Summary

One containerised Nginx (`proxy-nginx`) on the VPS publishes ports 80 and 443 for both apps, terminates TLS with
the institutional certificate, and routes by host name. Its configuration and orchestration live in this
repository's `nginx/` folder, which replaces the old single-app Nginx. Both repositories move from a root
`Makefile` to a root `justfile` with the same recipe names.

## Related Work

- Decision: [A Shared HTTPS Proxy Serves The App On The VPS](../decisions/2026-11-21-shared-https-proxy-on-the-vps.md)
- Decision: [just Entrypoint With Container-First Checks](../decisions/2026-11-21-just-entrypoint-with-container-first-checks.md)
- Research: [Shared VPS and Nginx](../research/2026-11-18-shared-vps-and-nginx-research.md)
- Reference: DAC Atlas production Nginx (resolver + `set $upstream`, HTTP to HTTPS redirects), shared by the DAC
  Atlas session on 21 November, 2026.
- No JuGit issue identified.

## Problem

Both apps shipped their own HTTP-only Nginx (DEMATELab on port 80, PCK on 8081), so only one could own port 80,
and HTTPS (needed because users send AI provider keys in request bodies) was commented out in both.

## Goals

- `https://dematelab.example.com` and `https://policycoherence.example.com` (and `www.`) served by one Nginx;
  HTTP redirects to HTTPS.
- Each app can be started, stopped, restarted and inspected on its own without affecting the other.
- The proxy configuration is versioned in git (this repository), not in a separate repository.
- Both repositories use `just` instead of `make`, with unchanged recipe names.

## Non-Goals

- Automatic certificate renewal (the certificate is institutional, valid until 29 May 2027).
- Converting the legacy `qt-app/` and `tk-app/` Makefiles.
- Serving ice2kg from this proxy.

## Current State (before)

- `docker-compose-prod.yml`: `web`, `api`, `nginx` (`dematelab-nginx`, `${HTTP_PORT:-80}:80`), all on
  `app-network`. PCK the same with `8081` and ports 3001/50002.
- `nginx/nginx.prod.conf` + `nginx/Dockerfile.prod` in both repos; HTTPS block commented out.
- Root `Makefile` in both repos (`make dev`, `make check`, `make prod`, …).

## Phases

### Phase 1: Shared proxy in `nginx/`

- `nginx/docker-compose.yml` (Compose project `proxy`, container `proxy-nginx`, `nginx:stable-alpine`, ports
  80/443, templates and the configured certificate directory mounted read-only, external network `proxy`).
- `nginx/templates/default.conf.template` (resolver `127.0.0.11`, TLS settings, catch-all: 444 on HTTP, handshake
  rejected on HTTPS), `nginx/templates/dematelab.conf.template`, `nginx/templates/policycoherencekit.conf.template` (redirect, HTTPS
  server, commented HTTP-only rollback). Upstreams by container name (`dematelab-web:3000`, …), because both
  projects name their services `web`/`api`.
- `nginx/justfile`, loaded by the root justfile as the module `proxy` (`just proxy up-all`), or run directly
  with `cd nginx && just up-all`. PCK's location is `PCK_DIR` (default a sibling checkout).
- Both repos: `web` and `api` join the external network `proxy`; the per-app `nginx` service and PCK's
  `nginx/` folder are removed.

### Phase 2: just in both repos

- Port each root `Makefile` to a root `justfile` with the same recipe names. `S=<service>` and `T=<args>`
  become recipe arguments (`just logs api`, `just test-api tests/x_test.py -v`). Delete the Makefiles.
- Update living docs (README, AGENTS, apps READMEs/AGENTS). Historical plans, reports and research stay as
  written.

## Risks And Decision Gates

- One proxy is a single point of failure for both sites: config is validated with `nginx -t` before every start
  or reload.
- No laptop "prod" setup any more: the proxy needs the certificate files. Production-like runs on a laptop use
  `just prod` (web and api without public entry) or `just dev`.
- `just` must be installed on every machine (it was not required before).

## Testing And Validation

- `just --list` in both repos, `just proxy nginx-test`.
- `just proxy up-all`, then `curl --resolve` all four names over HTTP (301) and HTTPS (200), `/api/v1/is-alive`,
  certificate SAN; bare IP refused.
- Stop and start each app alone: the other stays 200, the stopped one answers 502, and recovers without an
  Nginx restart.
- `just proxy down-all` and `up-all` exit 0.
- Dev recipes: `just setup`, `just help`, `just dev` guard messages (`just check-api` refuses without dev
  containers).

## Acceptance Criteria

- All checks above pass; no `Makefile` at either repo root; no living doc tells the reader to run `make` for
  `apps/`.

## Open Questions

- Reachability from outside the institute network was not tested from the VPS.
