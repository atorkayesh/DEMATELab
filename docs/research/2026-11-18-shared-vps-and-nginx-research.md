# How Can DEMATELab, Policy Coherence Kit And ice2kg Share One VPS Behind One Dockerised Reverse Proxy?

**Date:** 18 November, 2026
**Author:** Claude Code (planning agent) for Youpele Michael
**Status:** Complete
**Scope:** Running the DEMATELab, Policy Coherence Kit (PCK) and possibly ice2kg production stacks on one VPS
behind one reverse-proxy container: proxy choice (Nginx, Traefik, Caddy, nginx-proxy), routing by host name or
path prefix, separate Compose projects joined by an external network vs one shared Compose file, TLS with
Let's Encrypt, ports, healthchecks, zero-downtime deploys, and what changes in each repository's `nginx/` and
`make prod`. Out of scope: Kubernetes, Swarm, managed load balancers, backups, monitoring stacks. Nothing was
run on the VPS; VPS facts come from ice2kg's reports and decisions. The same core text is in both
repositories; only "Relevance" differs.

## Summary

The lowest-risk setup is **two-tier**: one small **edge proxy** container (Nginx with a static config) is the
only service publishing ports 80 and 443 on the VPS, terminates TLS, and routes **by host name** to each app's
**existing Nginx**, which stays inside its own Compose project and keeps its `/` and `/api/` routing (and
ice2kg's `/api/auth/` and `/sandbox/` rules). The app Nginx containers join one external Docker/Podman network
(for example `edge`); the apps' `web` and `api` containers do not, so their generic service names cannot
collide. The edge config lives in a **new small infrastructure repository**, not inside one of the apps.

Host-name routing needs one DNS name per app. Path prefixes (`/dematelab/`, `/pck/`) are not recommended:
all three web apps call root-relative `/api/` and route from `/`, so a prefix would need base-path changes in
each app and would put all apps on one browser origin (shared cookies and storage). Without DNS names, the
fallback is one public port per app (80, 8080, 8081), which needs no shared proxy at all.

Traefik, Caddy with `caddy-docker-proxy`, and `nginx-proxy` automate routes and certificates from container
labels but need the container engine's API socket; on the rootless Podman VPS that is extra setup and grants
the proxy control over all containers. **Caddy with a static Caddyfile** is the best alternative to Nginx if
automatic HTTPS is valued over keeping one proxy technology.

Blocking facts to settle first: which VPS, the DNS names, who issues certificates (Let's Encrypt or the
institution), and how rootless Podman may bind ports 80/443. Confidence: high for the documented proxy and
Compose behaviour; medium for Podman specifics, which ice2kg verified only partly on the VPS.

## Question

How should the three apps share one VPS and possibly one Dockerised Nginx, given that each repository today
ships its own production Nginx as the only public entry on `${HTTP_PORT:-80}` (PCK proposed `8081`), and what
changes in each repository?

## Sources And Method

- Repository files read on 18 November, 2026: DEMATELab `docker-compose-prod.yml`, `nginx/`, `Makefile`,
  decisions `2026-11-16-docker-compose-with-nginx-as-only-public-entry.md` and
  `2026-11-16-stateless-api-with-server-rendered-charts.md`; ice2kg `docker-compose-prod.yml`, `nginx/`,
  `Makefile`, decision `2026-11-10-serve-the-sandbox-at-sandbox-path-through-the-main-nginx.md`, report
  `2026-10-27-vps-resources-report.md`; PCK reports `2026-11-18-dematelab-conventions-inventory-report.md`.
- Official documentation (accessed 18 November, 2026): Docker Compose networking, nginx upstream module,
  Traefik Docker provider (v3.7 docs), Caddy automatic HTTPS, caddy-docker-proxy README, nginx-proxy
  acme-companion README, docker-rollout README, Podman rootless notes, Let's Encrypt challenge types and the
  15 January, 2026 announcement of short-lived and IP-address certificates.
- Not done: no test on the VPS, no DNS or certificate request, no load test.

## Findings

### 1. Current state (facts from the repositories)

| | DEMATELab | PCK (planned) | ice2kg |
|---|---|---|---|
| Prod Compose project | `dematelab` | `policycoherencekit` | `ice2kg` (+ `ice2kg-sandbox`) |
| Public service | `dematelab-nginx`, `${HTTP_PORT:-80}:80` | `policycoherencekit-nginx`, `${HTTP_PORT:-8081}:80` proposed | `ice2kg-nginx`, `${HTTP_PORT:-80}:80` |
| Internal upstreams | `web:3000`, `api:50001` | `web:3001`, `api:50002` | `web:3000`, `api:50001`, `/api/auth/` to web, `/sandbox/` to `ice2kg-sandbox-viewer:3847` |
| State | None (stateless API) | None (stateless API) | Neo4j, auth SQLite and log volumes |
| HTTPS | Commented-out server block | Copied from DEMATELab | Commented-out server block |
| Same-origin API | `VITE_API_BASE_URL` empty in production | Same | Same |

- All three Nginx configs resolve upstreams per request through `resolver ${NGINX_LOCAL_RESOLVERS}` and
  `set $upstream`, so Nginx starts while an upstream is missing and does not keep stale container IPs.
- ice2kg already joins two Compose projects through an external network (`ice2kg-sandbox-link`, created by
  `make prod` when missing) and verified on the VPS (Podman 4.9.4, netavark) that a container on two networks
  resolves containers of both by name (ice2kg sandbox decision).
- The ice2kg VPS (`metadb`, Rocky Linux 9.4) runs **rootless Podman 4.9.4** with podman-compose 1.6.0, where
  `ip_unprivileged_port_start` was 1024, so binding port 80 needed a change (ice2kg VPS report). It has 4 vCPUs
  and 24-31 GiB RAM since 10 November, 2026; both ice2kg stacks used about 2.1 GB. It is reached by IP address;
  no domain is recorded. Whether DEMATELab and PCK will run on this VPS is not recorded.

### 2. Proxy options

| Option | How routes are configured | TLS | Needs engine socket | Notes |
|---|---|---|---|---|
| **Nginx (static)** | Hand-written `server` blocks per host | Separate ACME client (certbot or acme.sh) writing to a shared volume, then `nginx -s reload` | No | Same image and patterns as the apps; open-source Nginx has passive failure detection only; active `health_check` is commercial; `server ... resolve` in an `upstream` is open source since 1.27.3 (nginx docs). |
| **Caddy (static Caddyfile)** | A few lines per host (`reverse_proxy`) | Automatic: Let's Encrypt with ZeroSSL fallback, HTTP-01 (port 80) and TLS-ALPN-01 (port 443); certificates in a data directory that must persist (Caddy docs) | No | New tool for the team; for IP addresses Caddy uses its own local CA, which browsers do not trust (Caddy docs). |
| **Traefik v3** | Container labels (`traefik.http.routers…`) | Built-in ACME | Yes: "Accessing the Docker API without any restriction is a security concern"; recommends a socket proxy (Traefik docs) | `exposedByDefault` is true unless set false; `network` option picks the network to reach containers. |
| **caddy-docker-proxy** | `caddy.*` labels turned into a Caddyfile | Caddy automatic | Yes, for the controller (README) | `CADDY_INGRESS_NETWORKS` selects the networks. |
| **nginx-proxy + acme-companion** | `VIRTUAL_HOST`, `VIRTUAL_PORT`, `ACME_HOST` env vars | acme.sh, HTTP-01 default, DNS-01 for wildcards | Yes, both containers (README) | Generated config makes per-app rules (ice2kg's sandbox allow-list) harder; keep them in the app Nginx. |

On rootless Podman, socket-based discovery needs the user's Podman API socket service enabled and mounted into
the proxy (inference from the socket requirement; not tested on the VPS).

### 3. Topology: two-tier vs single-tier, shared vs separate Compose

- **Single Compose file for all apps:** couples deploys, `down` stops everything, mixes env files. ice2kg
  rejected the same for its sandbox ("`make prod-down` would stop the lab"). Not recommended.
- **Separate Compose projects + one external network:** Compose does not create external networks: "The
  external network must exist before you run `docker compose up`" (Docker docs). Each app keeps its own
  lifecycle; this is the pattern ice2kg already uses.
- **Single-tier** (edge proxy routes straight to each app's `web`/`api`): one hop less, but the apps' `web`
  and `api` containers would join the shared network, where service names `web` and `api` exist in several
  projects (DNS aliases collide; edge config would need container names), and ice2kg's `/api/auth/` and
  `/sandbox/` rules would move into the shared config.
- **Two-tier** (edge proxy routes to `dematelab-nginx`, `policycoherencekit-nginx`, `ice2kg-nginx`): only the
  app Nginx containers join the shared network, under unique container names; app routing stays in each repo;
  each app can still run standalone on a laptop. Cost: one more hop and about 4 MB RAM per app Nginx
  (`ice2kg-nginx` used 4 MB, ice2kg VPS report). Recommended.

### 4. Routing: host name vs path prefix

- **Host name** (`dematelab.<domain>`, `pck.<domain>`, `ice2kg.<domain>`): no app changes beyond
  `CORS_ORIGINS`; each app keeps its own browser origin, so cookies (ice2kg's Better Auth sessions) and
  `localStorage` are not shared between apps. Needs DNS records (or a wildcard) pointing at the VPS.
- **Path prefix** (`<vps>/dematelab/`): every web app needs a router base path and asset base, every browser
  call to `/api/` must become prefixed, Better Auth's base URL changes, and all apps share one origin. ice2kg's
  `/sandbox/` decision shows how much allow-listing a prefixed app needs. Not recommended.
- **Separate ports** (`:80`, `:8080`, `:8081`): works with an IP address only and needs no shared proxy, but
  each port needs a firewall opening and its own TLS setup; a fallback while DNS is missing.

### 5. TLS

- Let's Encrypt challenges: HTTP-01 "can only be done on port 80"; DNS-01 supports wildcards but needs DNS API
  credentials on the server; TLS-ALPN-01 uses port 443 with limited client support (Let's Encrypt docs).
- Let's Encrypt made short-lived (160-hour) certificates and **IP-address certificates** generally available on
  15 January, 2026; IP certificates must use the `shortlived` profile (Let's Encrypt announcement). This makes
  TLS possible before DNS exists, with renewals every few days; client support for the profile must be checked.
- With a static Nginx edge: certbot or acme.sh in a sidecar container uses the webroot method on port 80
  (`/.well-known/acme-challenge/`), stores certificates in a named volume shared read-only with Nginx, and a
  scheduled renew followed by `nginx -s reload` (standard practice; exact tooling to be chosen).
- An institutional certificate (for example from the hosting institution's CA service) is an alternative if the
  domain belongs to the institution; whether that applies is unknown.
- Both apps need HTTPS before AI features are used publicly, because users send provider API keys in request
  bodies (DEMATELab decisions and `nginx/nginx.prod.conf` comments; same in PCK by design).

### 6. Ports

- With the edge proxy only 80 and 443 are public. App Nginx containers publish nothing (or only on
  `127.0.0.1` for debugging through an SSH tunnel). Internal ports (3000/50001 in two apps) do not clash, because
  each Compose project has its own network namespace and DNS.
- Rootless Podman cannot bind ports below 1024 unless `net.ipv4.ip_unprivileged_port_start` is lowered, for
  example to 80 (Podman rootless notes). This needs root once on the VPS (or a firewall redirect from 80/443 to
  high ports). How ice2kg's Nginx serves port 80 today is not recorded in its repository.
- Development ports stay as decided: DEMATELab and ice2kg both use 3000/50001 (one at a time), PCK 3001/50002.
  ice2kg's localhost-only ports (Neo4j 7476/7689, sandbox 3847/7475/7688) are unaffected.

### 7. Healthchecks and failure behaviour

- The apps' API containers have healthchecks; the app Nginx and web containers do not. An edge proxy with
  per-request resolution answers 502 while an app is down; a small `error_page 502 504 =503` page per host (the
  pattern ice2kg uses for `/sandbox/`) makes "app is restarting" distinguishable from a broken edge.
- Adding a healthcheck to each app Nginx (for example `wget -q -O- http://127.0.0.1/` or a `/healthz`
  location returning 200) lets `make prod`'s `--wait` and `ps` show the full chain.

### 8. Zero-downtime deploys

- `make prod` runs `compose up -d --build --wait`, which recreates changed containers; with one container per
  service there is a short window of 502s (DEMATELab decision: "/ answers 502 meanwhile").
- Building first (`compose build`, then `up -d`) shrinks the window to container restart time. True zero
  downtime needs two instances behind the proxy: `docker-rollout` scales a service to two, waits for health and
  removes the old one, but requires no `container_name` and no published `ports`, and needs a proxy such as
  Traefik or nginx-proxy that picks up new containers (docker-rollout README); Podman support is not stated.
  With static Nginx, blue/green needs two named services and an edge config switch plus reload.
- For three low-traffic research apps, a few seconds of 503 with a clear message during deploys is the
  pragmatic target (inference; traffic levels were not measured).

### 9. Risks

- One edge container is a single point of failure for all apps; keep its config tiny, validated with
  `nginx -t` before reload, and its image pinned.
- A config error in one app's server block can stop the edge from reloading for all apps; per-app files plus a
  pre-reload `nginx -t` contain this.
- Real client IPs: the edge must pass `X-Forwarded-For`/`X-Real-IP`, and the app Nginx must keep
  `X-Forwarded-Proto` from the edge instead of overwriting it with its own `$scheme` (`http`). Whether rootless
  Podman's port forwarding preserves client source addresses at the edge must be checked on the VPS.
- Request limits must be set at the edge as well: DEMATELab needs `client_max_body_size 20m`; all apps need
  `proxy_read_timeout 300s` and `proxy_buffering off` on streamed or slow AI routes.
- Resource contention: DEMATELab and PCK are stateless and small (memory not measured); ice2kg's two Neo4j
  instances dominate (about 1.9 GB together, ice2kg VPS report).

## Comparison

| Criterion | Edge Nginx (static), two-tier | Edge Caddy (static), two-tier | Traefik (labels) | nginx-proxy + acme-companion | One shared Compose | Separate public ports, no edge |
|---|---|---|---|---|---|---|
| App repos change | Small (network, ports, forwarded headers) | Small | Labels in each app | Env vars in each app | Large | Port default only |
| TLS automation | Sidecar ACME client | Built in | Built in | Built in | Any | Per app |
| Engine socket needed | No | No | Yes | Yes | No | No |
| Team familiarity | Same as apps | New | New | New | Same | Same |
| Independent deploys | Yes | Yes | Yes | Yes | No | Yes |
| Works without DNS | Only with IP cert or plain HTTP | Same | Same | Same | Same | Yes |
| Recommended | **Yes** | Alternative | No | No | No | Interim fallback |

## Relevance To DEMATELab

- DEMATELab's decision says "The VPS runs only DEMATELab"; a shared VPS supersedes that context and the
  "Nginx on `${HTTP_PORT:-80}` is the only public service" part of the decision (a new decision record is needed).
- `docker-compose-prod.yml`: `dematelab-nginx` joins the external edge network and stops publishing port 80
  publicly (bind to `127.0.0.1` or drop `ports`); `web` and `api` stay on `app-network` only.
- `nginx/nginx.prod.conf`: keep `/` and `/api/` routing and `client_max_body_size 20m`; take
  `X-Forwarded-Proto` and the client address from the edge; remove the commented HTTPS block (TLS moves to the
  edge); optionally add a `/healthz` location.
- `Makefile`: `prod` creates the external network when missing (as ice2kg's `_sandbox-network` does);
  `HTTP_PORT` keeps working for a standalone run.
- `apps/api/.env` on the VPS: `CORS_ORIGINS=https://<dematelab host>`; `apps/web/.env` keeps
  `VITE_API_BASE_URL` empty.
- Stateless: rollback is a redeploy of the previous commit; no data migration.

## Open Questions

- Which VPS hosts the shared setup, and does the hosting institution allow public 80/443 and DNS names for it?
- DNS names and certificate source (Let's Encrypt or institutional)?
- Can root lower `ip_unprivileged_port_start` on the VPS (or should Podman run rootful for the edge only)?
- Is a few seconds of 503 during deploys acceptable?

## References

- Docker, "Networking in Compose", https://docs.docker.com/compose/how-tos/networking/, accessed 18 November, 2026.
- nginx, "Module ngx_http_upstream_module", https://nginx.org/en/docs/http/ngx_http_upstream_module.html,
  accessed 18 November, 2026.
- Traefik Labs, "Docker provider" (v3.7 docs),
  https://doc.traefik.io/traefik/reference/install-configuration/providers/docker/, accessed 18 November, 2026.
- Caddy, "Automatic HTTPS", https://caddyserver.com/docs/automatic-https, accessed 18 November, 2026.
- L. Lorentz, caddy-docker-proxy README, https://github.com/lucaslorentz/caddy-docker-proxy, accessed
  18 November, 2026.
- nginx-proxy, acme-companion README, https://github.com/nginx-proxy/acme-companion, accessed 18 November, 2026.
- wowu, docker-rollout README, https://github.com/wowu/docker-rollout, accessed 18 November, 2026.
- Podman, "Shortcomings of Rootless Podman", https://github.com/containers/podman/blob/main/rootless.md,
  accessed 18 November, 2026.
- Let's Encrypt, "Challenge Types", https://letsencrypt.org/docs/challenge-types/; announcement of general
  availability of short-lived and IP-address certificates (15 January, 2026),
  https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability; accessed 18 November, 2026.
- ice2kg repository: `docs/reports/2026-10-27-vps-resources-report.md`,
  `docs/decisions/2026-11-10-serve-the-sandbox-at-sandbox-path-through-the-main-nginx.md`,
  `docker-compose-prod.yml`, `nginx/nginx.prod.conf` (commit `3d91fc6`), read 18 November, 2026.
