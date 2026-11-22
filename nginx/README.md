# Shared HTTPS Proxy (VPS)

One Nginx container (`proxy-nginx`) is the only service on the VPS that publishes ports **80 and 443**. It
terminates TLS and routes by host name to two apps from two repositories:

| Hostname setting | Upstreams |
|---|---|
| `PROXY_DEMATELAB_HOST` | `dematelab-web:3000`, `dematelab-api:50001` |
| `PROXY_PCK_HOST` | `policycoherencekit-web:3001`, `policycoherencekit-api:50002` |

HTTP redirects to HTTPS. The `www.` names send a permanent redirect (301) to the corresponding main name,
preserving path and query. Configure DNS for all names you want to accept. Unknown hosts and bare-IP requests
are rejected. The templates are mounted read-only and rendered at container startup. The default template
replaces the stock Nginx site; upstream container names are unique on the shared `proxy` network.

## Using it

From the repo root: `just proxy <recipe>` (`just proxy` lists them). Inside `nginx/`: `just <recipe>`.

| Goal | Recipe |
|---|---|
| Start / stop everything | `just proxy up-all` / `just proxy down-all` |
| Overview of all containers | `just proxy status` |
| DEMATELab | `up-dematelab`, `down-dematelab`, `restart-dematelab [web\|api]`, `status-dematelab`, `logs-dematelab [web\|api]` |
| Policy Coherence Kit | the same with `policycoherencekit` |
| Shared Nginx | `up-nginx`, `down-nginx`, `restart-nginx`, `status-nginx`, `logs-nginx` |
| Check / apply config | `nginx-test`, then `up-nginx` (recreates only the proxy) |

The app recipes call each repo's own `just prod`, `prod-down`, `prod-restart`, `prod-ps` and `prod-logs`, so a
deploy after `git pull` is `just proxy up-dematelab` (rebuilds and recreates only what changed). Apps can be
stopped, rebuilt or restarted independently: the proxy resolves containers per request, keeps serving the other
site, answers 502 for the stopped one, and picks it up again without a restart. Policy Coherence Kit's checkout
defaults to a sibling of the DEMATELab checkout named `policycoherencekit`; export `PCK_DIR` to override it.

The Docker network `proxy` is external: `just proxy network` (every `up-*` recipe, and each repo's `just prod`)
creates it when missing; nothing removes it.

## Deployment settings

1. Install Docker and just, and clone both repositories.
2. Copy the tracked proxy env example into a private `.env` in the Nginx directory (`umask 077` before copying).
   Set both DNS names, the host certificate directory, and the certificate and key filenames. The private key
   stays outside Git; the certificate must cover the two main and two www names. Record the public DNS target as `PROXY_PUBLIC_IP`; this is not a listener setting. Compose reads the private
   file via `--env-file` in the just recipes. Only set `PROXY_BIND_IP` if you want Docker to listen on a
   specific local interface. Leave it empty for all interfaces, including when the public IP is routed
   to the host but not assigned directly to it. DNS is configured separately.
3. In each app, run `just setup`. Set `VITE_APP_ENV=production` and leave `VITE_API_BASE_URL` empty in the web
   environment. Set `CORS_ORIGINS` in the API environment to the app's configured HTTPS origin.
4. Run `just proxy up-all` from the DEMATELab root.

`just proxy nginx-test` validates a fresh render without binding ports, even if the proxy is running.
After changing a template or deployment setting, run `just proxy up-nginx` to validate and recreate the proxy
(a brief interruption for both sites). If you renew the certificate at the same paths, run
`just proxy nginx-reload` to reload the running proxy without recreation.

The HTTP-only rollback blocks are retained in the templates for reference. Do not enable an HTTP-only
fallback while accepting AI provider keys.
