# A Shared HTTPS Proxy Serves The App On The VPS

**Status:** Accepted
**Date:** 21 November, 2026
**Deciders:** Youpele Michael (with Claude Code)

## Decision

On the VPS (192.0.2.10), DEMATELab and Policy Coherence Kit run side by side behind **one** containerised
Nginx (container `proxy-nginx`, image `nginx:stable-alpine`) whose configuration and orchestration live in the
DEMATELab repository's `nginx/` folder (`/srv/dematelab/nginx` on the VPS). It is the only service
publishing ports 80 and 443, terminates TLS with the institutional certificate whose SAN covers
`dematelab.example.com`, `policycoherence.example.com` and their `www.` names, redirects HTTP to HTTPS, and
routes by host name straight to each app's containers: `/` to `dematelab-web:3000`, `/api/` to `dematelab-api:50001`.
`just prod` starts only `web` and `api`; the per-app Nginx (service `nginx`, Dockerfile and `nginx.prod.conf`)
is removed from both repositories. `nginx/justfile` in DEMATELab (the module `just proxy …`) starts, stops and
inspects each app, the proxy, or everything.

## Context

- Both apps used to publish their own HTTP-only Nginx (DEMATELab on 80, PCK on 8081), and HTTPS had to be
  enabled before the AI feature is used, because users send provider keys in request bodies.
- Both domains resolve to this VPS and one certificate (`/srv/certificates/fullchain.pem`, GEANT
  TLS RSA 1, valid until 29 May 2027) covers both.
- Research: `docs/research/2026-11-18-shared-vps-and-nginx-research.md`. Plan: DEMATELab
  `docs/plans/2026-11-21-shared-https-proxy-and-just-plan.md`.

## Alternatives Considered

- **Two-tier (edge Nginx in front of each app's Nginx)**, recommended by the research: keeps routing in each
  repo, but adds a hop and needs the app Nginx to pass through `X-Forwarded-Proto`. Rejected in favour of the
  simpler single-tier setup used by DAC Atlas; routes are few and identical in shape.
- **Proxy attached to each project's own network:** `just prod-down` deletes that network and the proxy
  silently loses it. Rejected for one external network, `proxy`.
- **A separate repository or an unversioned folder on the VPS** (`/srv/proxy`, the first version): the
  proxy should be in git, but a repository of its own was not wanted.
- **Each repo keeps its own site file, mounted into the proxy:** each app would own its routes, but a routing
  change would touch two repositories and the proxy would depend on both checkouts' layout.
- **Keeping the per-app Nginx as a standalone fallback:** two configs per app to keep in sync.

## Consequences

- DEMATELab hosts the proxy for both apps: PCK's routes are changed and committed in the DEMATELab repository
  (`nginx/conf.d/policycoherencekit.conf`), and PCK's docs point there.
- No production-like single-app Nginx on a laptop any more (the proxy needs the certificate files); use
  `just dev`, or `just prod` for web and api without a public entry.
- `web` and `api` also join the external Docker network `proxy` (`just prod` creates it when missing). The
  proxy addresses them by **container name**; the service names `web`/`api` exist in both projects and are
  ambiguous on that network, so nothing may rely on them there.
- Routes and limits live in DEMATELab's `nginx/conf.d/dematelab.conf`.
- `apps/api/.env` on the VPS: `CORS_ORIGINS=https://dematelab.example.com,https://www.dematelab.example.com`; `apps/web/.env`:
  `VITE_APP_ENV=production`, `VITE_API_BASE_URL` empty.
- Requests by IP address or unknown host are refused (444 on HTTP, TLS handshake rejected on HTTPS).
- Renewing the certificate updates both sites at once; after replacing the files run `just proxy nginx-reload`.
- Revisit if a third app joins (ice2kg), if the certificate source changes (for example Let's Encrypt), or if
  the VPS moves to rootless Podman (the resolver `127.0.0.11` is Docker-specific).

## Related Work

- Supersedes: [Docker Compose With Nginx As The Only Public Entry](./2026-11-16-docker-compose-with-nginx-as-only-public-entry.md)
- Research: [Shared VPS and Nginx](../research/2026-11-18-shared-vps-and-nginx-research.md)
