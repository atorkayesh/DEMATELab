# DEMATELab - Agent Guidelines

DEMATELab runs DEMATEL cause-and-effect analyses (classical, fuzzy, grey, fuzzy Z-DEMATEL) from expert
judgments. It is being rebuilt as a web app in `apps/`; the original PySide6 desktop app stays in `qt-app/`
as the legacy app and the numerical reference. This file covers the **whole-app workflow**:

- **[`apps/api/AGENTS.md`](./apps/api/AGENTS.md)**: FastAPI, numerical parity, Python style, API testing.
  **Read it before changing anything in `apps/api/`.**
- `apps/web/`: the TanStack Start app (read [`apps/web/AGENTS.md`](./apps/web/AGENTS.md) before changing it)
  ([Rebuild The DEMATELab UI In TanStack Start](./docs/plans/2026-11-16-rebuild-ui-in-tanstack-start-plan.md)).

Human-facing setup is in [`README.md`](./README.md). Plans, decisions, reports, and research are in
[`docs/`](./docs/); each folder has a `--do-not-delete` authoring guide to follow.

---

## How the App Fits Together

```
Browser ──► web (TanStack Start, :3000) ──► api (FastAPI, :50001, /api/v1/*)
```

- **api** is stateless: every analysis-derived endpoint (analysis, XLSX export, charts, AI explanation)
  receives the full analysis request and recomputes it. Charts are PNGs rendered with matplotlib in the Qt
  style. AI provider keys come with each request and are never stored
  ([decision](./docs/decisions/2026-11-16-ai-keys-supplied-per-request.md)).
- **Numerical parity:** for the same input, every number equals the Qt app's, proven by fixtures generated
  from `qt-app/` (`scripts/generate_parity_fixtures.py`, see `apps/api/AGENTS.md`).
- **Nginx** reverse-proxies web (`/`) and api (`/api/`) in production. On the VPS that is the shared HTTPS
  proxy in `nginx/` (also serving Policy Coherence Kit, whose routes live in `nginx/conf.d/` too)
  ([decision](./docs/decisions/2026-11-21-shared-https-proxy-on-the-vps.md)).

### Repository layout

```
apps/api/       FastAPI app (see apps/api/AGENTS.md)
apps/web/       TanStack Start app (Typeform-style flow on /, results, /status)
nginx/          Shared HTTPS proxy for the VPS (DEMATELab + PCK) and its orchestration (just proxy …)
qt-app/         Legacy PySide6 app, its own Makefile and Compose files (read-only reference)
data/examples/  Sample workbooks
scripts/        generate_parity_fixtures.py (runs against qt-app/, writes apps/api/tests/fixtures/)
docs/           plans/, decisions/, reports/, research/ (each with an authoring guide)
justfile        Dev, check, and production entrypoints (just)
docker-compose-dev.yml / docker-compose-prod.yml
```

### `qt-app/` is read-only

- `apps/` must never import from, read, or start anything in `qt-app/`. Port code by copying or rewriting
  it and name the original file and lines.
- Do not change `qt-app/` as part of `apps/` work. Only `scripts/generate_parity_fixtures.py` runs it.

---

## Running the App

Run the app in Docker. The root `justfile` is the entrypoint: `just` lists every recipe
([decision](./docs/decisions/2026-11-21-just-entrypoint-with-container-first-checks.md)).

```bash
just setup          # create apps/api/.env and apps/web/.env from their examples

just dev            # docker compose -f docker-compose-dev.yml up -d --build --wait (api on :50001, web on :3000)
just down           # stop and remove the dev containers
just logs api       # follow logs
just sh-api         # shell in dematelab-api

just check-api      # ruff format --check, ruff check, pytest inside the dev container
just test-api tests/parity_integration_test.py -v
just format

just prod           # api (gunicorn) and web; the VPS's shared proxy serves them over HTTPS
just prod-logs api
just proxy up-all   # VPS: both apps and the shared HTTPS proxy (nginx/README.md)
```

- just uses `docker` when installed, otherwise `podman` (override with `DOCKER=podman just …`).
- Ports are fixed: API 50001, web 3000. If another app holds them (for example ice2kg on the same
  machine), `just dev` stops with a message; free the port and retry.
- Web checks: `just check-web` runs `cd apps/web && pnpm run format:check && pnpm run lint && pnpm run
  typecheck && pnpm run test` inside the web container.
- The legacy Qt app keeps its own setup: `make -C qt-app dev` (noVNC at `http://localhost:6080`). Its dev
  Compose project is also called `dematelab-dev`; run one of the two dev stacks at a time.

### Docker services

| Service | Container | Purpose | Dev host port | Prod host port |
|---|---|---|---|---|
| `web` | `dematelab-web` | TanStack Start app | 3000 | not published |
| `api` | `dematelab-api` | FastAPI API | 50001 | not published |
| – | `proxy-nginx` (`nginx/docker-compose.yml`) | Shared HTTPS proxy, VPS only | – | 80, 443 |

### Environment files

Each service has its own env file, created from the `.env.example` next to it (`just setup`); there is no
root `.env` ([decision](./docs/decisions/2026-11-16-each-service-has-its-own-env-file.md)).

| File | Used by | Holds |
|---|---|---|
| `apps/api/.env` | `api` | `APP_ENV` (Compose overrides it), `CORS_ORIGINS`, `WEB_CONCURRENCY` |
| `apps/web/.env` | `web` | `VITE_APP_ENV`, `VITE_API_BASE_URL` (public: inlined into the bundle, never secrets) |
| `qt-app/DEMATELab/.env` | legacy Qt containers | `VNC_PASSWORD`, `NOVNC_PORT`, … |

On the VPS: `CORS_ORIGINS` set to the public origin (`https://dematelab.example.com`), and the app is
reached only over HTTPS through the shared proxy (keys travel in request bodies). Never commit `.env` files.

---

## Development Workflow

1. **Plan first.** Non-trivial work gets a plan in `docs/plans/`; significant choices get a decision record
   in `docs/decisions/`.
2. **Work in the right app.** Read its AGENTS.md first and follow its patterns.
3. **Keep changes in scope**; preserve Qt behaviour unless a decision says otherwise.
4. **Add or update tests** for every important function, route, service, or feature.
5. **Keep every code file at or below 300 lines** (tests included; fixtures, lockfiles, and `.md` exempt).
6. **Before committing:** run `just format` and `just check-api` (or `cd apps/api && uv run ruff format
   --check . && uv run ruff check . && uv run pytest`), fix every failure, and re-run until they pass.
7. **Update docs** when behaviour changes: the app's AGENTS.md for rules, README files for setup.

---

## Pre-Commit Checklist

- [ ] Changes follow the app's AGENTS.md rules
- [ ] Tests written or updated, and all checks pass (`just check-api`)
- [ ] Parity fixtures regenerated from `qt-app/` if maths or Qt-derived behaviour changed
- [ ] Every code file in `apps/` is at or below 300 lines
- [ ] No hardcoded secrets; no AI keys in env files or logs
- [ ] No imports or reads from `apps/` into `qt-app/`
- [ ] Docs updated if behaviour or workflow changed

---

## Legacy Qt App (`qt-app/`)

### Setup and launch
- The installable project is `qt-app/DEMATELab/pyproject.toml`, not the repository root; Python must be >=3.10. From the root, install for development with `python3 -m pip install -e ./qt-app/DEMATELab`.
- Launch from `qt-app/DEMATELab/` with `python3 -m DEMATELab` (or the installed `DEMATELab` command). Both call `DEMATELab.gui_app:main`; running `gui_app.py` directly is not the entrypoint.
- Keep that working directory: stepper icons and stylesheet URLs use relative `assets/icons/...` paths, while logos/fonts use package-relative `qt-app/DEMATELab/DEMATELab/assets/`. These two asset directories are not interchangeable.
- `qt-app/DEMATELab.app` is a launcher, not a standalone distribution: it executes `/opt/miniconda3/bin/python3` against the adjacent source checkout.

### Execution paths and editing traps
Paths below are relative to `qt-app/DEMATELab/DEMATELab/`.

- **Duplicate definitions:** `gui_app.py` defines `StepperWidget`, `FloatStepperWidget`, `MainWindow`, and `main` twice. The later definitions override the earlier ones; locate the active definition before editing.
- Analysis flows from `gui_app.py` through `analysis_service.run_analysis(AnalysisInput)` into the numerical engines. This service is the GUI-independent entrypoint for focused solver checks.
- Fuzzy Z-DEMATEL only has a separate linguistic converter (`fuzzy_z_dematel_core.py`); it reuses `FuzzyExpertInput`, `FuzzyDematelEngine`, and `FuzzyDematelResult`, not a separate Z engine/result.
- Result matrices differ: classical uses `(n, n)` arrays and unprefixed fields; fuzzy/Z use `(n, n, 3)` arrays and `fuzzy_*` fields; grey uses `(n, n, 2)` arrays and `grey_*` fields. All expose scalar `r`, `c`, `prominence`, and `relation` vectors. The viewer resolves matrix fields via `_get_matrix_attr`.
- GUI XLSX/PNG exports are implemented in `results_viewer_widget.py`; they do not call `export_service.py`. Changing the latter alone will not change GUI exports.
- AI requests run through `ExplanationWorker` in a `QThread`, wired and cleaned up in `results_viewer_widget.py`; provider requests live in `llm_explanation_service.py`.

### Input contracts
- `constants.py` owns linguistic maps. Standard scales end in `Extreme influence`; Z uses `Very high influence` plus reliability. Labels are case-sensitive after trimming.
- `matrix_parsers.py` handles Excel imports: one sheet per expert for workbook imports, either an `n x n` body or an `(n+1) x (n+1)` labeled matrix. Named-import paths require matching row/column factor names and consistent names across sheets; comparisons are case-insensitive. Imported diagonals are forced to `No influence`.
- Engine weights must sum to 1; the GUI's three-decimal rounding/tolerance correction is in `_normalize_weight_inputs`, not in `analysis_service.run_analysis`.

### Verification
- The Qt app has no automated tests or lint configuration of its own; `scripts/generate_parity_fixtures.py` runs it to produce the API's parity fixtures.
- Dependencies are locked in `qt-app/DEMATELab/uv.lock` (used by the Docker images). After editing `qt-app/DEMATELab/pyproject.toml`, run `uv lock` in `qt-app/DEMATELab/`.
- Docker: `make -C qt-app dev` / `make -C qt-app prod` (`qt-app/Makefile`, wrapping `docker compose -f docker-compose-<dev|prod>.yml --env-file DEMATELab/.env` inside `qt-app/`) runs the GUI in a container served over noVNC at `http://localhost:6080`; `make -C qt-app logs|restart|shell|status|down` act on whichever setup is running. The container starts as root only so `qt-app/DEMATELab/docker/start.sh` can give the `app` user the owner of `exports/`, then drops privileges. The app runs from `/workspace`, which links `assets/` back to `/app/assets` so the relative icon paths still resolve.
- Minimum syntax check from the repository root: `python3 -m compileall -q qt-app/DEMATELab/DEMATELab`. This does not verify numerical correctness or GUI behavior.
- For behavior changes, launch the GUI and exercise the affected solver/import/export flow. Sample workbooks are in `data/examples/`; AI explanation additionally requires a provider API key and network access.
- `font_loader.ensure_inter_fonts` may download Inter from GitHub if the package's `assets/fonts/Inter-Regular.ttf` is missing; download failures silently fall back to available fonts.
