# Shared HTTPS Proxy (VPS)

One Nginx container (`proxy-nginx`) is the only service on the VPS that publishes ports **80 and 443**. It
terminates TLS and routes by host name to two apps from two repositories:

| Site | App containers | Repository on the VPS |
|---|---|---|
| https://dematelab.example.com (+ `www.`) | `dematelab-web:3000`, `dematelab-api:50001` (`/api/`) | `/srv/dematelab` (this repo) |
| https://policycoherence.example.com (+ `www.`) | `policycoherencekit-web:3001`, `policycoherencekit-api:50002` (`/api/`) | `/srv/policycoherencekit` |

HTTP redirects (301) to HTTPS, and `www.` (HTTP or HTTPS) redirects permanently to the main name, e.g.
`www.dematelab.example.com` → `https://dematelab.example.com`. The `www.` names have no DNS records yet
(21 November, 2026); the redirect works as soon as they exist. Requests by IP or for any other name are refused (444 on port 80,
TLS handshake rejected on 443). Why it is built this way:
[decision](../docs/decisions/2026-11-21-shared-https-proxy-on-the-vps.md),
[plan](../docs/plans/2026-11-21-shared-https-proxy-and-just-plan.md).

## Files

```
docker-compose.yml              proxy-nginx (nginx:stable-alpine), ports 80/443, external network `proxy`
conf.d/00-default.conf          resolver, TLS settings, catch-all servers
conf.d/dematelab.conf           DEMATELab: redirect + HTTPS server (+ commented HTTP-only rollback)
conf.d/policycoherencekit.conf  Policy Coherence Kit: the same
justfile                        orchestration (module `proxy` of the root justfile)
```

`conf.d/` and `/srv/certificates` are mounted read-only, so config edits need only
`just proxy nginx-reload`. Upstreams are container names (`dematelab-web`, …), never the service names
`web`/`api`: both projects use those names, and Compose registers them on the shared network too.

## Using it

From the repo root: `just proxy <recipe>` (`just proxy` lists them). Inside `nginx/`: `just <recipe>`.

| Goal | Recipe |
|---|---|
| Start / stop everything | `just proxy up-all` / `just proxy down-all` |
| Overview of all containers | `just proxy status` |
| DEMATELab | `up-dematelab`, `down-dematelab`, `restart-dematelab [web\|api]`, `status-dematelab`, `logs-dematelab [web\|api]` |
| Policy Coherence Kit | the same with `policycoherencekit` |
| Shared Nginx | `up-nginx`, `down-nginx`, `restart-nginx`, `status-nginx`, `logs-nginx` |
| Check / apply config | `nginx-test` (works when stopped too), `nginx-reload` |

The app recipes call each repo's own `just prod`, `prod-down`, `prod-restart`, `prod-ps` and `prod-logs`, so a
deploy after `git pull` is `just proxy up-dematelab` (rebuilds and recreates only what changed). Apps can be
stopped, rebuilt or restarted independently: the proxy resolves containers per request, keeps serving the other
site, answers 502 for the stopped one, and picks it up again without a restart. Policy Coherence Kit's checkout
is expected at `/srv/policycoherencekit`; set `PCK_DIR` to use another path.

The Docker network `proxy` is external: `just proxy network` (every `up-*` recipe, and each repo's `just prod`)
creates it when missing; nothing removes it.

## First-time setup on a fresh VPS

1. Docker, just, both repositories cloned to `/srv/dematelab` and `/srv/policycoherencekit`.
2. Certificates in `/srv/certificates` (see below).
3. In each repo, `just setup`, then edit for production:
   - `apps/web/.env`: `VITE_APP_ENV=production`, `VITE_API_BASE_URL=` (empty: same-origin `/api/`)
   - `apps/api/.env`: `CORS_ORIGINS=https://<host>,https://www.<host>`
4. `just proxy up-all`.

## Certificate

`/srv/certificates/fullchain.pem` (leaf + chain, issuer GEANT TLS RSA 1, valid until
**29 May 2027**) covers all four names; the key is `privkey.pem`. Both HTTPS servers use the
same pair. To renew: replace the two files (or change the names in both `conf.d/*.conf`), then
`just proxy nginx-reload`. Check expiry with
`openssl x509 -in /srv/certificates/fullchain.pem -noout -enddate`.

## Rollback

- **HTTPS problem:** in `conf.d/<app>.conf` comment out the two servers and uncomment the `ROLLBACK (HTTP only)`
  block, then `just proxy nginx-reload`. Do not use the AI features meanwhile (keys travel in request bodies).
- **Whole change:** the previous per-app Nginx setup is in git history (before this folder replaced
  `nginx/nginx.prod.conf`).

## Notes

- Resolver `127.0.0.11` is Docker's DNS. Under Podman it would be the network gateway instead.
- One proxy serves both sites: always run `nginx-test` (the `up-nginx`, `restart-nginx` and `nginx-reload`
  recipes do) before applying changes.
