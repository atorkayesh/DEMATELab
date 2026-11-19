# Draw DEMATELab's Charts In The Browser And Prepare For A Shared VPS Behind One Reverse Proxy

**Date:** 18 November, 2026 (created 18:33 CET; last modified 18 November, 2026, 18:33 CET)
**Status:** Draft (owner decisions D1-D12 are open; becomes Proposed once they are answered)
**Owner:** Youpele Michael (plan written by Claude Code)

## Summary

Two independent parts:

- **Part A, browser charts.** Replace the matplotlib PNGs of the causal diagram and the standard/cluster
  heatmaps with interactive Apache ECharts charts drawn in the browser. The API keeps every computation and
  returns chart data (positions, filtered edges, widths, curvature, threshold, matrix, cluster codes) instead of
  images; the browser only maps data to visuals and produces the PNG/SVG downloads from the same chart options.
  Matplotlib leaves the API at the end.
- **Part B, shared VPS.** Make DEMATELab's production stack ready to sit behind one shared, Dockerised edge
  reverse proxy that also serves Policy Coherence Kit (PCK) and possibly ice2kg: DEMATELab's Nginx stops being
  publicly published, joins an external `edge` network, and trusts the edge for TLS and forwarded headers. The
  edge proxy lives in a new small infrastructure repository.

User impact: tooltips, zoom/pan and crisp charts at any size instead of zoomable images; vector (SVG) downloads
in addition to PNG; HTTPS on a host name when Part B is deployed.

## Related Work

- Research: [Which browser chart library could replace the server-rendered matplotlib charts?](../research/2026-11-18-browser-chart-libraries-research.md)
- Research: [How can DEMATELab, PCK and ice2kg share one VPS behind one Dockerised reverse proxy?](../research/2026-11-18-shared-vps-and-nginx-research.md)
- Decision (superseded in part by A0): [Stateless API with server-rendered charts](../decisions/2026-11-16-stateless-api-with-server-rendered-charts.md)
- Decision (superseded in part by B2): [Docker Compose with Nginx as the only public entry](../decisions/2026-11-16-docker-compose-with-nginx-as-only-public-entry.md)
- Decision: [Each service has its own env file](../decisions/2026-11-16-each-service-has-its-own-env-file.md)
- Plans: [Port the backend to FastAPI](./2026-11-16-port-backend-to-fastapi-api-plan.md) (API contract),
  [Rebuild the UI in TanStack Start](./2026-11-16-rebuild-ui-in-tanstack-start-plan.md)
- Sibling plan: `docs/plans/2026-11-18-browser-charts-and-shared-vps-plan.md` in the PCK repository
  (`policycoherencekit`), same structure.
- Issue or merge request: none identified (no JuGit issue was given); see Open Questions.

## Problem

- Charts are PNGs rendered by matplotlib per request (`apps/api/features/causal_diagram_chart_feature.py`,
  `apps/api/features/heatmap_chart_feature.py`, `apps/api/utils/figure_utils.py`) and shown as zoomable images
  (`apps/web/src/components/page-specific/analysis/ChartImage.tsx`). They cannot show values on hover, do not
  follow the shadcn theme, are blurry when zoomed past 100 dpi, have no text alternative beyond `alt`, and every
  view or mode switch is a full recomputation plus a render round-trip (`apps/web/src/hooks/chart.hook.ts`).
- The owner asked to research shadcn charts or a better library; the research recommends ECharts because
  shadcn charts (Recharts) have no heatmap or directed-graph series.
- DEMATELab's production setup assumes it is alone on its VPS (decision: "The VPS runs only DEMATELab"; Nginx
  on `${HTTP_PORT:-80}`). The owner plans to run DEMATELab, PCK and possibly ice2kg on one VPS behind possibly
  one Dockerised Nginx; three stacks cannot all publish port 80, and HTTPS (required before AI explanations are
  used, because users send provider keys) is still commented out.

## Goals

- A1. The causal diagram and both heatmaps render in the browser with ECharts, with the same meaning as today:
  same nodes, positions, colours by group, edges (strictly above the threshold, no self-loops), relative widths,
  mutual-edge curvature, reference lines, legend texts, titles, matrix values and cluster labels.
- A2. The browser computes nothing DEMATEL-specific; every chart value comes from new API chart-data responses
  covered by pytest.
- A3. Downloads keep their file names and offer PNG at 2400 x 1800 px (8 x 6 in at 300 dpi) and SVG, produced
  from the same option object as the screen.
- A4. Matplotlib, its font registration and its Docker layers are removed from the API once no endpoint uses
  them (decision gate D3).
- B1. DEMATELab runs behind the shared edge proxy at `https://<dematelab host>/` with no publicly published port
  of its own, and still runs standalone with `make prod` on a developer machine.
- B2. The edge proxy configuration is owned outside the app repositories, and each app's changes are small and
  documented.

## Non-Goals

- No change to any DEMATEL number, threshold rule, clustering or the XLSX export (it contains no charts:
  `apps/api/features/xlsx_export_feature.py:1-8`).
- No new chart types (for example a dendrogram or prominence bar chart) and no graph editing or node dragging.
- No server-side export path for charts (ECharts `renderToSVGString` in the web server) unless D4 asks for it.
- Part B does not create the infrastructure repository, change ice2kg, or touch the VPS; it only lists what
  those need and changes DEMATELab's files.
- No change to the summary PNG capture (`html-to-image`, `apps/web/src/hooks/export.hook.ts:40-47`).

## Current State

Plan validity: written against DEMATELab `main` at `6a76ae2` with a clean worktree (only this plan and the two
research notes added). Revalidate the paths below if `apps/api/features/*chart*`, `apps/api/utils/
influence_map_utils.py`, the chart router, `ResultTabs`, `ExportBar`, `docker-compose-prod.yml` or
`nginx/nginx.prod.conf` change first.

### Charts

- Router `apps/api/routers/analysis_charts.py`: `POST /api/v1/analysis/charts/causal-diagram?dpi=100|300` and
  `POST /api/v1/analysis/charts/heatmap?mode=standard|cluster&dpi=100|300`, body `AnalysisRequest`, response
  `image/png`; cluster mode returns 422 with "Could not generate cluster heatmap: …" when clustering fails
  (`apps/api/features/clustering_feature.py`, `ClusteringFailedError`).
- Causal diagram (`causal_diagram_chart_feature.py:72-133`): threshold defaults to `mean(crisp_total_matrix)`
  when `threshold_value` is `None`; nodes at (prominence, relation), green when `relation > 0`, red otherwise;
  dashed line at relation 0; dotted line at mean prominence; labels "Prominence"/"Relation"; legend "Cause
  factor"/"Effect factor"; grid. Geometry in `apps/api/utils/influence_map_utils.py`: `validate` (Qt messages),
  `positions`, `edges` (strictly above threshold, row-major, diagonal skipped), `line_width` (linear between
  0.6 and 4.0, midpoint when all equal), `draw_edges` (single edges `rad` 0.06; a mutual pair sorted by
  (source, target) gets +0.20 and −0.20). Style values in `apps/api/constants/chart_constants.py`.
- Heatmap (`heatmap_chart_feature.py:87-123`): standard = `imshow(crisp_total_matrix)` with colourbar "Relation
  Strength", title "Total Relation Matrix Heatmap"; cluster = codes 0..4 ("No influence" + `CLUSTER_NAMES`) with
  `CLUSTER_COLORS`, title "Cluster-Based Heatmap"; ticks rotated 45°.
- The analysis response already contains `factors`, `prominence`, `relation`, `threshold_value`,
  `crisp_total_matrix` (`apps/api/models/analysis_result_models.py:19-32`) but not edges, widths, curvature,
  the threshold fallback or cluster codes.
- Web: `CausalDiagramPanel.tsx` and `HeatmapPanel.tsx` fetch PNG blobs with `useChart` (`hooks/chart.hook.ts`,
  `services/charts.service.ts`) and show `ChartImage` → `ZoomableImage`. The heatmap's cluster checkbox
  pre-fetches the cluster PNG and shows the API's error inline on failure (`HeatmapPanel.tsx:30-49`).
  `ExportBar.tsx` downloads `causal_diagram.png`, `heatmap_standard.png`, `heatmap_cluster.png` from the API at
  300 dpi (`hooks/export.hook.ts:16-38`, `constants/results.constants.ts:23-35`, `CHART_DPI` in
  `constants/api.constants.ts:19`).
- Rules that constrain the work: "No DEMATEL maths in the browser", `useQuery` for chart data, Zod for every
  response, UI text in `constants/`, 300-line limit, shadcn components only via the CLI (`apps/web/AGENTS.md`);
  `Figure` API only and the 300-line limit in `apps/api/AGENTS.md`.
- Matplotlib footprint: `matplotlib==3.11.2` (`apps/api/pyproject.toml:16`), `matplotlib.use("Agg")` and
  `font_registrar.register_inter_fonts()` (`apps/api/main.py:9,19,24-26`), `utils/font_utils.py`,
  `utils/figure_utils.py`, `assets/fonts/`, `MPLCONFIGDIR` and `fonts-dejavu-core` in
  `apps/api/Dockerfile.{dev,prod}:5-10`.
- `--chart-1…5` in `apps/web/src/styles.css:39-43,75-79` are greyscale neutrals.

### Production

- `docker-compose-prod.yml`: project `dematelab`; `dematelab-nginx` publishes `${HTTP_PORT:-80}:80`; `web`, `api`
  on bridge `app-network`; api healthcheck on `/api/v1/is-alive`.
- `nginx/nginx.prod.conf`: per-request resolver; `/` → `web:3000`, `/api/` → `api:50001` with
  `proxy_read_timeout 300s`, `proxy_buffering off`; `client_max_body_size 20m`; sets
  `X-Forwarded-Proto $scheme`; HTTPS block commented out.
- `Makefile:191-206`: `prod` = `compose -f docker-compose-prod.yml up -d --build --wait`; no network setup.

## Owner Decisions

Each needs an answer before the phase that depends on it. Recommendations are from the two research notes.

| # | Decision | Options | Recommendation | Blocks |
|---|---|---|---|---|
| D1 | Chart library | Settled by the owner (2026-11-18) | **Apache ECharts only, in both DEMATELab and Policy Coherence Kit; no shadcn/Recharts middle ground.** Charts must be styled to fit the project's theme and patterns (colours, fonts, radii and spacing read from the theme's CSS variables; shadcn-style card, legend and tooltip look), and built as reusable chart components wherever possible: one themed base `EChart` wrapper in `components/general/charts/` (init, resize, theme from CSS variables, SSR-safe lazy load, PNG/SVG download) plus typed per-type components (heatmap, directed network, scatter, bar) that the page-specific panels compose. | A0 |
| D2 | Accept that charts no longer look like the Qt/matplotlib figures | Accept (keep meaning, colours, texts); keep matplotlib look | **Accept**, with "parity of meaning" as defined in Goal A1; record it in a decision superseding the chart part of the stateless-API decision. | A0 |
| D3 | Fate of the PNG endpoints and matplotlib | Remove after browser downloads are validated; keep as a "classic" download | **Remove** in A4, after A3 is validated on the VPS; keeping both doubles maintenance and invites drift. | A4 |
| D4 | Download formats | PNG only; PNG + SVG; PNG with 300 dpi metadata | **PNG (2400 x 1800 px, with a `pHYs` chunk set to 300 dpi) + SVG.** No server-side export. | A3 |
| D5 | Interactivity | Static; tooltips + legend toggle; + zoom/pan (roam) | **Tooltips, legend toggling, zoom/pan with a reset button**; no node dragging (downloads must equal the data). | A2 |
| D6 | Which VPS hosts the shared setup | ice2kg's `metadb` VM; another VM | **`metadb`**, if the hosting institution agrees: 4 vCPUs and 24-31 GiB RAM, about 2.1 GB used (ice2kg VPS report). | B3 |
| D7 | Routing | Host names; path prefixes; one port per app | **Host names** (for example `dematelab.<domain>`); ports 80/8080/8081 only as an interim without DNS. | B1, B2 |
| D8 | Edge proxy technology | Static Nginx; static Caddy; Traefik/label-based | **Static Nginx**, same image and patterns as the apps, no engine socket. Caddy if automatic HTTPS is preferred. | B1 |
| D9 | Where the edge config lives | New infra repository; inside ice2kg; inside DEMATELab | **New small repository** (name to choose), owned like the apps: Compose file, per-host conf files, Makefile, docs. | B1 |
| D10 | Certificates | Let's Encrypt (certbot/acme.sh sidecar); institutional CA; IP certificate | **Let's Encrypt HTTP-01 via a certbot sidecar**, unless the domain belongs to the institution and it issues certificates. | B1 |
| D11 | Binding 80/443 under rootless Podman | Lower `net.ipv4.ip_unprivileged_port_start` to 80 (root, once); firewall redirect to high ports; rootful Podman for the edge | **Lower the sysctl to 80** (persisted in `/etc/sysctl.d/`). | B3 |
| D12 | DEMATELab Nginx publishing on the VPS, and deploy downtime | Publish on `127.0.0.1:${HTTP_PORT:-8080}`; publish nothing; keep `${HTTP_PORT:-80}` | **Loopback `127.0.0.1:${HTTP_PORT:-8080}`** (debug through an SSH tunnel; laptops still work at `http://localhost:8080`). Accept a few seconds of 503 during deploys. | B2 |

## Phases

### Part A: Browser charts

#### Phase A0: Decision record and spike

Depends on D1, D2.

1. Add `docs/decisions/2026-11-xx-browser-charts-from-api-chart-data.md` (date of acceptance): charts are drawn
   in the browser with ECharts from API chart data; the API stays stateless and owns all chart geometry;
   matplotlib remains only until A4. Mark the chart paragraph of
   `2026-11-16-stateless-api-with-server-rendered-charts.md` as superseded (dated note at the top, link).
2. Spike on a throwaway branch (not merged): add `echarts` (pin the exact version, 6.1.0 or newer) to
   `apps/web`, import through `echarts/core` with `GraphChart`, `HeatmapChart`, `ScatterChart`, the grid,
   tooltip, legend, visualMap, markLine, dataZoom (only if roam is insufficient), aria components and both
   `CanvasRenderer` and `SVGRenderer`; render a hard-coded causal diagram inside TanStack Router's `ClientOnly`.
   Record: gzip size of the lazy chunk (`pnpm run build` output), that SSR of `/` is unaffected, PNG export at
   `pixelRatio: 3`, SVG export, and how jsdom tests behave (expect: ECharts needs canvas; tests target option
   builders and mock the chart component). Also check against today's PNG for the same request: arrowheads end
   at the node border (matplotlib shrinks both ends by 18 points), and a mutual pair drawn with the API's
   `curvature` values bends the same way as matplotlib's `arc3,rad` (ECharts `curveness` is relative to the
   edge direction too; confirm the sign mapping before A2).
3. Exit: numbers recorded in this plan's Testing section; if the lazy chunk exceeds the agreed budget (owner
   to state; suggestion 250 KB gzip), stop and revisit D1.

#### Phase A1: API chart-data endpoints

Depends on A0. Files: `apps/api/models/chart_models.py` (new), `apps/api/features/causal_diagram_chart_feature.py`,
`apps/api/features/heatmap_chart_feature.py`, `apps/api/utils/influence_map_utils.py`,
`apps/api/routers/analysis_charts.py`, tests next to each.

1. Refactor `InfluenceMapGeometry.draw_edges` into a pure `edge_curvatures(edges) -> list[float]` (same pairing
   and ordering rules: single 0.06, mutual sorted pair +0.20/−0.20, third and later 0.06) used by both
   `draw_edges` and the new data builder, so the PNG and the data cannot drift while both exist.
2. Add `CausalDiagramData` (Pydantic): `factors`, `nodes: [{factor, prominence, relation, group:
   "cause"|"effect"}]` (group by `relation > 0`, as drawn today), `threshold` (after the mean fallback),
   `mean_prominence`, `edges: [{source, target, weight, line_width, curvature}]` in row-major order. Build it in a
   `CausalDiagramChartFeature.data(output)` method reusing `validate`, `positions`, `edges`, `line_width`.
3. Add `HeatmapData`: `factors`, `mode`, `values` (crisp total matrix, unrounded), `min`, `max`, and in cluster
   mode `codes` (0..4 as `heatmap_chart_feature.py:105-106` computes them) and `labels` (`["No influence",
   *CLUSTER_NAMES]`). Colours stay in the web constants (UI concern), copied from `CLUSTER_COLORS`.
4. Routes (names to align with the API contract section of the backend plan):
   `POST /api/v1/analysis/charts/causal-diagram/data` and `POST /api/v1/analysis/charts/heatmap/data?mode=…`,
   returning the standard `ResponseBuilder.ok` envelope; same 422 for clustering failures; CPU work in
   `asyncio.to_thread` like the PNG routes. Keep the PNG routes unchanged until A4.
5. Tests: unit tests for `edge_curvatures` and both data builders (equal-weights midpoint, threshold `None`,
   mutual pairs, no edges, clustering failure); a consistency test that the edges, widths and curvatures in
   the data equal what `draw_edges` draws for the same output (patch `_arrow` and compare calls); router tests
   for status codes and envelope; parity tests keep passing unchanged (`make test-api T="tests/parity_integration_test.py -v"`).
6. Update the API contract in `docs/plans/2026-11-16-port-backend-to-fastapi-api-plan.md` (or the API
   AGENTS.md section that lists endpoints).

Exit: `make check-api` passes; new endpoints visible at `/api/docs`.

#### Phase A2: Web charts

Depends on A1 and D5. Files (all under `apps/web/src/`): `interfaces/chart.interface.ts` (Zod schemas mirroring
A1), `services/charts.service.ts`, `hooks/chart.hook.ts`, `components/general/EChart.tsx` (new),
`utils/causal-diagram-chart.utils.ts` and `utils/heatmap-chart.utils.ts` (new, pure option builders),
`utils/chart-theme.utils.ts` (new), `constants/chart.constants.ts` (new: titles, axis and legend labels,
cluster colours, export size), `components/page-specific/analysis/{CausalDiagramPanel,HeatmapPanel}.tsx`,
`styles.css` (new chart tokens).

1. Add `echarts` with `pnpm add echarts@<pinned>` inside the web container; no React wrapper package needed.
2. `EChart.tsx`: a `ClientOnly` component that initialises an instance on a ref, applies the option, resizes
   with a `ResizeObserver`, disposes on unmount, enables `aria`, and exposes the instance to the export code
   (ref or callback). Lazy-load the module (`React.lazy` or dynamic import) so the flow steps do not pay the
   bundle cost. Rendering is not data fetching, so the `useEffect` rule in `apps/web/AGENTS.md` is not broken;
   say so in a code comment.
3. Option builders (pure functions, unit-tested): causal diagram as a `graph` series on `cartesian2d` with value
   axes, node colour by `group`, labels inside nodes, `edgeSymbol: ['none','arrow']`, per-edge
   `lineStyle.width` and `curveness` from the API, `markLine` at relation 0 (dashed) and at `mean_prominence`
   (dotted), legend "Cause factor"/"Effect factor", tooltip with factor, prominence, relation, and for edges the
   weight. Heatmap: `heatmap` series on category axes with labels rotated 45°, continuous `visualMap` titled
   "Relation Strength" (standard) or piecewise `visualMap` with the five labels and colours (cluster).
4. Theme: `chart-theme.utils.ts` reads `--foreground`, `--muted-foreground`, `--border`, `--background`, the
   font family and new tokens (`--chart-cause`, `--chart-effect`, a heatmap ramp) with `getComputedStyle` and
   builds the ECharts theme; colour values for cause/effect start from today's green/red.
5. Hooks: `useChartData(snapshot, snapshotHash, kind, mode)` with `useQuery` keyed like today's chart query;
   the cluster checkbox keeps its pre-fetch-and-revert behaviour using the data query.
6. Accessibility: `aria.show` with a short generated description; a visually hidden caption pointing to the
   Scores table and Prominence ranking as the tabular alternative; decal patterns for the cluster heatmap.
7. Layout: charts fill the tab width with an aspect-ratio box (4:3) and scroll inside their box below 320 px,
   as the layout rules require.
8. Tests (Vitest): option builders (edges, widths, curvature, markLines, visualMap pieces, empty edges);
   panels render loading, error (including the cluster error) and success states with the chart component
   mocked; Zod schemas reject malformed data.

Exit: `make check-web` passes; screens show the new charts; PNG routes still used for downloads.

#### Phase A3: Browser downloads

Depends on A2 and D4. Files: `hooks/export.hook.ts`, `components/page-specific/analysis/ExportBar.tsx`,
`utils/chart-export.utils.ts` (new), `constants/results.constants.ts`.

1. Downloads render an off-screen ECharts instance at 800 x 600 CSS px with animation off and a white
   background, then `getDataURL({type: 'png', pixelRatio: 3})` (2400 x 1800 px) and, with the SVG renderer,
   an SVG string. File names unchanged (`causal_diagram.png`, `heatmap_standard.png`, `heatmap_cluster.png`);
   SVG files use the same stem with `.svg`.
2. If D4 keeps dpi metadata: insert a `pHYs` chunk (11811 pixels per metre) into the PNG bytes in
   `chart-export.utils.ts` (small, unit-tested; no new dependency).
3. Keep the export bar's pending/error behaviour; chart downloads become client-side mutations like the
   summary capture.

Exit: downloads open in an image viewer at 2400 x 1800 px; SVGs open in a browser; `make check-web` passes.

#### Phase A4: Remove matplotlib (decision gate D3)

Depends on A3 validated on the VPS (or locally with `make prod` if the VPS is not ready).

1. Remove the PNG routes, `draw`/`render*` methods, `utils/figure_utils.py`, `utils/font_utils.py`,
   `assets/fonts/` (if nothing else uses them; check the AI prompt and XLSX code first), `ChartDpi`/`DISPLAY_DPI`/
   `DOWNLOAD_DPI`/`PNG_MEDIA_TYPE`, `matplotlib` from `pyproject.toml` (then `uv lock`), `MPLCONFIGDIR` and
   `fonts-dejavu-core` from both Dockerfiles, `matplotlib.use` and font registration from `main.py`, and their
   tests. Keep `ResponseBuilder.image` only if something else uses it.
2. Web: remove `ChartImage`, `ZoomableImage` (if unused), `useObjectUrl` (if unused), `CHART_DPI`, PNG chart
   service functions.
3. Update `AGENTS.md` (root: "Charts are PNGs rendered with matplotlib"), `apps/api/AGENTS.md` (Figure API rule,
   chart constants), `apps/web/AGENTS.md` (file organisation, "useQuery … for chart PNGs"), READMEs, and mark
   the decision as fully superseded for charts.

Exit: `make check` passes; API image no longer installs matplotlib; `grep -ri matplotlib apps/` finds nothing.

### Part B: Shared VPS and shared edge proxy

#### Phase B0: Prerequisites (owner and VPS administrator)

Depends on D6, D7, D10, D11. Outside this repository: DNS records for the chosen host names pointing at the VPS;
firewall opens 80 and 443; `net.ipv4.ip_unprivileged_port_start=80` persisted (or the D11 alternative);
confirmation from the hosting institution that public HTTPS services are allowed.

#### Phase B1: Edge proxy repository (outside DEMATELab)

Depends on D8, D9, D10. Recorded here so DEMATELab's changes match it; implemented in the new repository.

- `docker-compose.yml` (project `edge`): `edge-nginx` (`nginx:stable-alpine`, pinned) publishing 80 and 443,
  joined to the external network `edge` (created by its Makefile); a `certbot` service using the webroot method
  on a shared volume; named volumes for certificates and the ACME webroot.
- `conf.d/00-default.conf`: port 80 serves `/.well-known/acme-challenge/` for every host and redirects
  everything else to HTTPS; unknown hosts get 444 on 443/80.
- `conf.d/dematelab.conf`, `conf.d/pck.conf`, `conf.d/ice2kg.conf`: one `server` per host on 443 with its
  certificate; `resolver` + `set $upstream http://dematelab-nginx:80` (per-request resolution so a stopped app
  answers a 503 page, not a failed edge start); `client_max_body_size 20m`; `proxy_read_timeout 300s`;
  `proxy_buffering off` on `/api/`; `X-Forwarded-For`, `X-Forwarded-Proto https`, `X-Real-IP`, `Host`.
- Makefile: `up`, `down`, `reload` (runs `nginx -t` first), `certs` (issue/renew), `logs`; a scheduled renew
  (systemd user timer or cron) documented in its README.

#### Phase B2: Make DEMATELab edge-ready (this repository)

Depends on D7, D12. Safe to ship before the VPS cutover: locally it behaves like today except for the port.

1. `docker-compose-prod.yml`: `nginx` service `ports` → `"127.0.0.1:${HTTP_PORT:-8080}:80"` (D12); add the
   external network `edge` (`networks: edge: {name: edge, external: true}`) to the `nginx` service only; keep
   `web` and `api` on `app-network` only; add an Nginx healthcheck against a new `/healthz` location.
2. `nginx/nginx.prod.conf`: add `location = /healthz { return 200; }` (no logging); replace
   `X-Forwarded-Proto $scheme` with a `map` that keeps the edge's `X-Forwarded-Proto` when present (fallback
   `$scheme`); add `set_real_ip_from` for the edge network's subnet with `real_ip_header X-Forwarded-For` (subnet
   fixed by naming the network's subnet in the edge repository, or the Docker/Podman default ranges); delete the
   commented HTTPS block and update the comments (TLS terminates at the edge).
3. `Makefile`: an `_edge-network` helper (like ice2kg's `_sandbox-network`: inspect, create when missing) as a
   prerequisite of `prod`; `prod` echoes the local URL `http://localhost:8080`; add a port check for
   `HTTP_PORT` like `require_port` (today prod has none).
4. Docs: new decision `docs/decisions/2026-11-xx-shared-edge-proxy-on-a-shared-vps.md` superseding the
   "only public service on `${HTTP_PORT:-80}`" and "The VPS runs only DEMATELab" parts of
   `2026-11-16-docker-compose-with-nginx-as-only-public-entry.md`; update root `AGENTS.md` (Docker services
   table: prod host port), `README.md` production section, and `apps/api/.env.example` comments
   (`CORS_ORIGINS=https://<dematelab host>` on the VPS).

Exit: `make prod` locally serves the app at `http://localhost:8080`; `docker compose -f
docker-compose-prod.yml config` is valid; with a local edge (B1) and the host `dematelab.localhost`,
`curl -H "Host: dematelab.localhost" http://localhost/api/v1/health` returns 200 through both proxies.

#### Phase B3: Cutover on the VPS

Depends on B0, B1, B2 and the same changes in the other apps that share the VPS. HTTP-01 validation needs
port 80, so the cutover is a short announced maintenance window (minutes). Order:

1. Set `CORS_ORIGINS=https://<dematelab host>` in `apps/api/.env` and deploy the edge-ready version with
   `make prod` (loopback port only). Any app still publishing port 80 on the VPS keeps serving meanwhile.
2. Stop the old public binding on port 80 (the app that holds it deploys its edge-ready version).
3. Start the edge with only the port-80 default server (ACME webroot and redirect), issue the certificates
   (`make certs` in the edge repository), then enable the 443 host files and `make reload`.
4. Validate (see Testing); then use AI explanations publicly (HTTPS is in place).

Rollback: DEMATELab is stateless. Revert B2's commit and `make prod` with `HTTP_PORT=80` to serve directly
again; stop the edge. No data to restore.

## Risks And Decision Gates

- **Visual drift from Qt** (A): accepted only via D2; mitigated by keeping colours, texts, rules and the
  consistency test between data and the matplotlib drawing while both exist.
- **Bundle size** (A0 gate): if the lazy chunk exceeds the budget, revisit D1 (for example Observable Plot for
  static SVG charts).
- **Dense charts** (100 factors): heatmap labels and causal-diagram node labels overlap; mitigate with
  `dataZoom` on the heatmap and hiding labels below a zoom level; check in A2 manual tests.
- **Testing canvas in jsdom**: ECharts needs a canvas; keep logic in pure option builders and mock the chart
  component; manual visual checks cover rendering.
- **Download fidelity**: canvas fonts must be loaded before export; wait for `document.fonts.ready`.
- **Single point of failure** (B): the edge serves all apps; pin its image, run `nginx -t` before reloads, keep
  per-host files small.
- **Header trust** (B): trusting `X-Forwarded-*` only from the edge subnet; otherwise clients can spoof them.
- **Rootless Podman** (B): port binding (D11) and whether client IPs survive Podman's port forwarding are
  unverified on the VPS; check in B3.
- Gates: A0 needs D1/D2; A3 needs D4; A4 needs D3 and validated downloads; B1 needs D8-D10; B2 needs D7/D12;
  B3 needs B0, B1, B2 and the other apps' edge-ready changes.

## Testing And Validation

- API: `make check-api` (Ruff format check, Ruff lint, pytest); targeted
  `make test-api T="features/causal_diagram_chart_feature_test.py features/heatmap_chart_feature_test.py utils/influence_map_utils_test.py routers/analysis_charts_test.py -v"`;
  parity unchanged: `make test-api T="tests/parity_integration_test.py -v"`.
- Web: `make check-web` (format check, lint, typecheck, Vitest); `make test-web T=chart`.
- Spike/bundle (A0): `pnpm run build` in the web container; record the chart chunk's gzip size here.
- Manual (A2/A3), with `make dev` and `data/examples/` workbooks: crisp, fuzzy, grey and fuzzy Z results; a
  result with `threshold_value` absent; mutual edges; no edges above the threshold; the cluster checkbox on a
  matrix too small to cluster (inline error, box unticked); 320 px width; keyboard focus order; screen reader
  reads the aria description; downloads at 2400 x 1800 px with the expected names; side-by-side comparison with
  the old PNGs for the same request.
- Part B: `docker compose -f docker-compose-prod.yml config`; local two-proxy check with `*.localhost` hosts;
  on the VPS: `curl -I https://<dematelab host>/`, `/api/v1/health`, a 15 MB request accepted and a 25 MB one
  rejected with 413, an AI explanation completing (300 s timeout path), `X-Forwarded-Proto` seen as `https` by
  the API, the edge's 503 page while `dematelab-web` is stopped, certificate renewal dry run.

## Acceptance Criteria

- The causal diagram and both heatmaps render with ECharts from the new chart-data endpoints; no PNG is
  requested for display.
- For the same request, edges, widths and curvatures in the chart data equal those the matplotlib drawing used
  (consistency test passes while both exist).
- PNG downloads are 2400 x 1800 px (with 300 dpi metadata if D4 says so) and SVG downloads open; file names
  are unchanged.
- After A4, matplotlib and its fonts are gone from `apps/api`, and docs no longer mention server-rendered charts.
- `make check` passes after every phase.
- DEMATELab serves at `https://<dematelab host>/` through the edge, publishes no public port of its own, and
  `make prod` still works standalone at `http://localhost:8080`.
- The two new decision records exist and the superseded decisions carry dated notes.

## Open Questions

- D1-D12 above.
- Is there a JuGit issue for this work to link?
- Bundle budget for the chart chunk (suggested 250 KB gzip)?
- Name of the infrastructure repository and of the shared network (placeholder `edge`)?
- Will ice2kg join the shared edge at the same time (it currently owns port 80 on `metadb`)? If it moves later,
  the edge must start on 443 only and port 80 moves with ice2kg's change.
