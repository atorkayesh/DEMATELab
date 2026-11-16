# Port The DEMATELab Backend To A Dockerised FastAPI `apps/api`

**Date:** 16 November, 2026
**Status:** Ready for implementation
**Owner:** Youpele Michael (planned with Claude Code)
**Created:** 2026-11-16 14:10 CET · **Last modified:** 2026-11-16 14:40 CET
**Inspected:** `/Users/youpele/DevWorld/FZJ/dematelab`, branch `restructure/apps-api-web`, commit `df78b5c`,
clean worktree. Conventions from `/Users/youpele/DevWorld/FZJ/ice2kg` (`apps/api`, `docker-compose-*.yml`,
`nginx/`, `Makefile`, `docs/`), inspected the same day.

## Summary

Everything the Qt app does apart from drawing widgets moves into a FastAPI service in `apps/api`:
the four solvers and five threshold methods, Excel import, the results summary, XLSX export, the causal
diagram and heatmaps (standard and cluster) as PNGs, and the AI explanation. The service runs in Docker
with the same Compose, Nginx and Make setup as ice2kg. **Same numbers, new structure:** for the same
input, every number must equal the Qt app's. The TanStack frontend is a separate plan
([Rebuild The DEMATELab UI In TanStack Start](2026-11-16-rebuild-ui-in-tanstack-start-plan.md)) that
depends on this one; this plan creates the Compose/Nginx/Make files with both services so the frontend
plan only fills in `apps/web`.

## Related Work

- Commit `df78b5c`: empty `apps/` layout, Qt app moved to `qt-app/`, sample data in `data/examples/`.
- ice2kg reference plans: `docs/plans/2026-10-26-dockerised-api-and-web-scaffold-plan.md`,
  `docs/plans/2026-10-27-port-sandbox-backend-to-api-plan.md`.
- Frontend plan: [Rebuild The DEMATELab UI In TanStack Start](2026-11-16-rebuild-ui-in-tanstack-start-plan.md).
- JuGit issue: none identified.

## Problem

All logic runs inside a PySide6 desktop app (served in Docker over noVNC). There is no HTTP API, no tests,
and parts of the business logic live in GUI files: weight correction and name checks in
`qt-app/DEMATELab/DEMATELab/gui_app.py:55-101,1922-1946`; summary numbers, XLSX export, heatmaps and the
cluster heatmap in `results_viewer_widget.py:439-789,1020-1123,1397-1545`; workbook-to-expert matching in
`matrix_editor_widget.py:611-656`. A web frontend cannot use any of it.

## Goals

- Every non-UI capability of the Qt app is available under `/api/v1` (endpoint list below).
- Numerical parity with the Qt app, proven by frozen fixtures generated from `qt-app/`.
- XLSX export reproduces the Qt GUI export (`results_viewer_widget.py:1397`), not the unused
  `export_service.py`.
- Code follows the ice2kg API rules (copied into `apps/api/AGENTS.md`): router → feature → service/utils,
  class-based with constructor injection and shared instances, absolute imports, docstring-only
  `__init__.py`, Google docstrings, `Optional[...]` typing, co-located `*_test.py`, Ruff E/F/I/B at 120
  columns, every code file ≤ 300 lines, `AppError` subclasses only (never `HTTPException`).
- `make dev` starts api (and later web) with hot reload; `make prod` runs gunicorn behind Nginx;
  `make check-api` passes inside the dev container.
- `apps/api` never imports from or reads `qt-app/`.

## Non-Goals

- The frontend (`apps/web` content). This plan only adds its Compose/Nginx/Make entries, guarded so they
  work before `apps/web` exists (see Phase 8).
- Changing formulas, linguistic maps, thresholds, KMeans settings, the prompt text, or plot styling.
- Persistence, accounts, auth, saving projects. The API is stateless.
- Z-DEMATEL import (the Qt app has none), text/paste import (`parse_linguistic_matrix_from_text`, unused),
  PDF export and the cluster membership bar chart (unused in the GUI).
- Removing or changing `qt-app/`.

## Settled Decisions (do not reopen without new evidence)

1. API port **50001**, web **3000** (own VPS, so no clash with ice2kg). Python **3.13**.
2. **Stateless API.** Every endpoint that needs results (summary, export, charts, explanation) receives
   the full analysis request and recomputes. Solving is milliseconds for the Qt limits (≤ 100 factors,
   ≤ 50 experts), so no cache or session store.
3. The API **always applies the Qt weight correction** (`_normalize_weight_inputs`: 3 decimals,
   tolerance 0.005, remainder from the last expert backwards) and returns the corrected weights.
4. **No per-expert numeric matrices** in responses (the Qt app never shows them).
5. Validation matches the Qt GUI: factor names required, trimmed, unique **case-sensitively**; expert
   names required, **duplicates allowed**; 2–100 factors, 1–50 experts; diagonals forced to the solver's
   no-influence label (`"No influence"` / `"No influence with VH reliability"`).
6. Charts are rendered **server-side with matplotlib** in the Qt style (same functions, same colours,
   Inter font), returned as PNG. Both charts are drawn as Qt does on screen: an 8×6 figure at
   matplotlib's default dpi (100) with `tight_layout()` (`results_viewer_widget.py:96,172-185`; the
   `DematelPlotStyle(dpi=120)` the GUI passes is ignored because it draws on an existing axis,
   `dematel_visualization.py:166`). `dpi` accepts `100` (display) or `300` (download, saved with
   `bbox_inches="tight"` as Qt's export does).
7. AI provider keys are **supplied per request by the user** (as in Qt), never stored, never logged, and
   not in env files. Five providers as in Qt: Gemini, OpenAI, Azure OpenAI, OpenRouter, Groq; Anthropic was added
   later, with a validated model catalogue served by `GET /explanations/providers`.
8. **Fixes to labels, not maths** (these were wrong in Qt and are corrected because the web app shows
   them):
   - Results carry the real `solver_type`, so Z results are labelled "Fuzzy Z-DEMATEL" (Qt shows
     "Fuzzy …" because `_result_kind` never detects Z, `results_viewer_widget.py:223`).
   - The AI payload uses the real solver type (Qt sends `"dematel"` for grey,
     `llm_explanation_service.py:38-68`) and includes the grey interval vectors as it does fuzzy ones.
   - The summary returns the threshold method's user-facing label ("Maximum Mean De-Entropy") and its
     key (`mmde`). The XLSX export keeps the key, as Qt writes it.
   - A blank AI model uses the viewer's default-model table (`results_viewer_widget.py:1245-1251`), not
     the worker's older one (`llm_worker.py:36-45`), which Qt never reaches from the GUI.
   - Exporting the cluster heatmap when clustering fails returns 422 with Qt's message instead of
     silently saving the standard heatmap (`results_viewer_widget.py:1076-1085,1519-1539`).
   - Cluster heatmap cells are coloured by their ranked cluster label (Low … High), so each colour matches
     its colourbar label; Qt colours by the raw KMeans id + 1 while labelling the colourbar by rank
     (`results_viewer_widget.py:1087-1102`). Display only: the clustering itself is unchanged.
   Everything else that looks odd is kept as is and listed under Known Qt Behaviour Kept.
9. The Inter fonts are copied into `apps/api/assets/fonts/` and registered at startup; no download
   (drop `font_loader.py`'s GitHub fallback).
10. Plans live in `docs/plans/` (ice2kg convention), not `docs/plan/`.

## Known Qt Behaviour Kept (parity, not bugs to fix here)

- Cause group is `relation >= 0`, but the causal diagram colours a node green only when `relation > 0`
  (`dematel_visualization.py`). Kept in both places.
- Thresholds are computed over the whole crisp/defuzzified/whitened total matrix **including the
  diagonal**; diagram edges use `T > threshold` strictly and skip the diagonal.
- Fuzzy and grey normalisation divide by the scale of the upper component only.
- The stat-box descriptions in the summary are fixed text (frontend concern; the API returns numbers).
- Workbook sheets are matched to experts by name only if **all** experts match (trimmed,
  case-insensitive); otherwise by order.

## Current State

Source (all under `qt-app/DEMATELab/DEMATELab/`):

| File | What it holds | Port target |
| --- | --- | --- |
| `constants.py` (132) | Linguistic maps, `ThresholdMethod`, Z labels, `CLUSTER_NAMES`, `LLM_MODEL` | `constants/*_constants.py` |
| `analysis_service.py` (157) | `AnalysisInput`, alias normalisation (:46-91), `run_analysis` dispatch | `features/analysis_feature.py`, `constants/solver_constants.py` |
| `dematel_core.py` (205) | crisp converter (:43), `DematelEngine` (:66-205) | `features/crisp_dematel_feature.py`, `features/linguistic_conversion_feature.py` |
| `fuzzy_dematel_core.py` (299) | fuzzy converter (:46), defuzzify (:69), TFN maths (:89-110), engine (:113) | `features/fuzzy_dematel_feature.py`, `utils/triangular_utils.py` |
| `grey_dematel_core.py` (294) | grey converter (:46), whiten (:69), interval maths (:87-106), engine (:109) | `features/grey_dematel_feature.py`, `utils/interval_utils.py` |
| `fuzzy_z_dematel_core.py` (36) | Z converter | `features/linguistic_conversion_feature.py` |
| `mmde_service.py` (134) | MMDE threshold (:98) | `features/mmde_threshold_feature.py` |
| `matrix_parsers.py` (348) | Excel parsing; used: `parse_standard_linguistic_labels_and_factor_names_from_excel_bytes` (:266), `..._workbook_bytes` (:312) | `features/matrix_import_feature.py`, `utils/excel_matrix_utils.py` |
| `gui_app.py` (active code :1227-2241) | weight defaults (:55), weight correction (:64), name checks (:1922) | `features/weight_normalization_feature.py`, request validators |
| `results_viewer_widget.py` | summary numbers (:439-789), XLSX (:1397), heatmaps (:1052), `_get_matrix_attr` (:232) | `features/result_summary_feature.py`, `features/xlsx_export_feature.py`, `features/heatmap_chart_feature.py` |
| `matrix_editor_widget.py` | workbook → expert matching (:611-656) | `features/matrix_import_feature.py` |
| `dematel_visualization.py` (302) | influence map | `features/causal_diagram_chart_feature.py`, `constants/chart_constants.py` |
| `clustering_service.py` (235) | `cluster_total_matrix` (KMeans 4, `random_state=42`, `n_init="auto"`, off-diagonal) | `features/clustering_feature.py` |
| `llm_explanation_service.py` (278) | payload (:38), prompt (:71-97), provider calls (:100-216) | `features/explanation_feature.py`, `features/explanation_prompt_feature.py`, `services/llm_provider_service.py`, `services/gemini_service.py` |
| `export_service.py` | **unused by the GUI**, crashes on grey | not ported |
| `font_loader.py` | Inter registration + GitHub download | `utils/font_utils.py` (registration only) |

Locked versions for Python 3.13 in `qt-app/DEMATELab/uv.lock`: numpy 2.5.4, pandas 3.1.1, matplotlib
3.11.2, scikit-learn 1.9.1, openpyxl 3.1.5, httpx 0.28.1, google-genai 3.0.0. The API pins the same
versions so parity fixtures and the API run the same numerical stack.

## API Contract

All responses use ice2kg's `ApiResponseModel[T]` (`success`, `message`, `data`, `metadata`, `error`),
except file downloads. Errors use `ErrorInfo(code, fields)`; validation errors are 422 with field paths.

Shared request body **`AnalysisRequest`** (used by every analysis-derived endpoint):

```text
solver_type: "dematel" | "fuzzy_dematel" | "grey_dematel" | "fuzzy_z_dematel"   (aliases from analysis_service.py:46-61 accepted)
threshold_method: "average" | "first_quartile" | "median" | "third_quartile" | "mmde"   (aliases :64-84 accepted; required, as in the GUI)
factors: list[str]                      2..100, trimmed, non-empty, unique (case-sensitive)
experts: list[{name: str, weight: float, matrix: list[list[str]]}]   1..50; name trimmed non-empty; weight 0..1; matrix n×n
```

| Method + path | Body | Returns |
| --- | --- | --- |
| `GET /api/v1/health` | – | `HealthCheckData` (API only; no dependencies) |
| `GET /api/v1/is-alive` | – | `AliveData` (Docker healthcheck) |
| `GET /api/v1/scales` | – | per solver family: ordered term list, default/diagonal label; Z also influence terms and reliability terms; solver options (key + label); threshold options (key + label); expert/factor limits and weight decimals/tolerance; default weights rule |
| `POST /api/v1/weights/defaults` | `{expert_count}` | equal weights in thousandths, remainder to the first experts (`gui_app.py:55`) |
| `POST /api/v1/weights/normalize` | `{weights: list[float]}` | corrected weights, or 422 "Expert weights must sum to 1." (`gui_app.py:64-101`; used by the web app at "Next: Create Matrix Editor") |
| `POST /api/v1/analysis` | `AnalysisRequest` | `AnalysisResponseData` = `{result, summary, corrected_weights}` |
| `POST /api/v1/analysis/export/xlsx` | `AnalysisRequest` | `dematel_results.xlsx` (binary download) |
| `POST /api/v1/analysis/charts/causal-diagram?dpi=100\|300` | `AnalysisRequest` | `image/png` |
| `POST /api/v1/analysis/charts/heatmap?mode=standard\|cluster&dpi=100\|300` | `AnalysisRequest` | `image/png` |
| `POST /api/v1/imports/matrix` | multipart: `file`, `factor_count` | `{factor_names: list[str] \| null, matrix: list[list[str]]}` |
| `POST /api/v1/imports/workbook` | multipart: `file`, `factor_count`, `expert_names` (repeated) | `{factor_names \| null, matrices: [{expert_name, matrix}], matched_by: "name" \| "order"}` |
| `POST /api/v1/explanations` | `{analysis: AnalysisRequest, provider, api_key, model?, azure_endpoint?}` | `{text, provider, model}` |

`result` is a Pydantic union discriminated by `solver_type`, with the Qt field names:

- common: `solver_type`, `factors`, `expert_weights`, `r`, `c`, `prominence`, `relation` (crisp, `n`),
  `cause_group`, `effect_group`, `threshold_method`, `threshold_value`, `crisp_total_matrix` (`n×n`; what
  the Qt viewer uses for charts and clustering: `np.asarray(total, float)` for crisp, `.mean(axis=2)` of
  the fuzzy/grey total, exactly as `_to_numeric_2d_array`, `results_viewer_widget.py:54-58`. Thresholds
  keep using the engine's own defuzzified/whitened matrix.)
- crisp: `direct_matrix`, `normalized_matrix`, `total_matrix` (`n×n`)
- fuzzy and fuzzy Z: `fuzzy_direct_matrix`, `fuzzy_normalized_matrix`, `fuzzy_total_matrix` (`n×n×3`),
  `fuzzy_r`, `fuzzy_c`, `fuzzy_prominence`, `fuzzy_relation` (`n×3`)
- grey: `grey_*` equivalents (`n×n×2`, `n×2`)

`summary` (from `results_viewer_widget.py:439-789`): `result_type_label` ("Classical DEMATEL",
"Fuzzy DEMATEL", "Grey DEMATEL", "Fuzzy Z-DEMATEL"), `threshold_method_key`, `threshold_method_label`,
`threshold_value`, `driving_factor_count`, `dependent_factor_count`, `top_prominence`,
`strongest_relation` (`relation[np.argmax(np.abs(relation))]`), `prominence_ranking`
(`[{factor, prominence, relation, bar_ratio}]` in the order `np.argsort(prominence)[::-1]` exactly as
`results_viewer_widget.py:728-741`, so ties keep Qt's reversed index order; `bar_ratio = p / max|p|`, 0
when the maximum is 0). Rounding is a display concern; the API returns full floats.

Limits: upload size 5 MB (`UploadTooLargeError`, 413) checked in the feature; `.xlsx` only (by
extension and openpyxl load; 422 otherwise). Nginx `client_max_body_size 20m` (a 100×100×50 JSON request
is ≈10 MB).

## Target Layout

```text
apps/api/
  main.py  pyproject.toml  uv.lock  .python-version  .env.example  .dockerignore
  Dockerfile.dev  Dockerfile.prod  README.md  AGENTS.md  CLAUDE.md
  assets/fonts/Inter-*.ttf                       copied from qt-app (9 files)
  api/v1/api.py                                  router registration
  config/settings_config.py                      APP_ENV, CORS_ORIGINS
  constants/
    app_constants.py  linguistic_constants.py  solver_constants.py  weight_constants.py
    chart_constants.py  cluster_constants.py  import_constants.py  llm_constants.py
  models/
    response_model.py  error_models.py  health_models.py  scale_models.py  weight_models.py
    analysis_request_models.py  analysis_result_models.py  summary_models.py
    import_models.py  explanation_models.py  solver_models.py (internal engine outputs)
  errors/
    app_error.py  error_handlers.py  error_presenter.py  health_errors.py
    analysis_errors.py  import_errors.py  llm_errors.py
  utils/
    response_utils.py (+ bytes download)  triangular_utils.py  interval_utils.py
    matrix_utils.py  excel_matrix_utils.py  font_utils.py  figure_utils.py
  features/
    health_feature.py  scales_feature.py  weight_normalization_feature.py
    linguistic_conversion_feature.py  threshold_feature.py  mmde_threshold_feature.py
    crisp_dematel_feature.py  fuzzy_dematel_feature.py  grey_dematel_feature.py
    analysis_feature.py  result_summary_feature.py  clustering_feature.py
    causal_diagram_chart_feature.py  heatmap_chart_feature.py  xlsx_export_feature.py
    matrix_import_feature.py  explanation_prompt_feature.py  explanation_feature.py
  services/
    llm_provider_service.py   httpx calls: OpenAI-compatible (Groq/OpenRouter/OpenAI) and Azure
    gemini_service.py         google-genai call
  middleware/cache_control_middleware.py
  routers/
    health.py  scales.py  weights.py  analysis.py  analysis_export.py  analysis_charts.py
    imports.py  explanations.py
  tests/fixtures/parity/*.json   tests/fixtures/imports/*.xlsx
scripts/generate_parity_fixtures.py   (repo root; runs against qt-app, never imported by apps/api)
docker-compose-dev.yml  docker-compose-prod.yml  Makefile  nginx/
```

Each `*_feature.py` / `*_service.py` holds one class and ends with a shared instance; every co-located
`*_test.py` exists for each feature, util, service and router. Files that approach 300 lines are split
by responsibility (e.g. `fuzzy_dematel_feature.py` → matrix steps and score/result assembly), never by
moving logic into routers.

## Phases

### Phase 1: API skeleton (copied from ice2kg)

1. `apps/api/pyproject.toml` (name `dematelab-api`, `requires-python ">=3.13"`): `fastapi[standard]`,
   `pydantic`, `pydantic-settings`, `python-dotenv`, `gunicorn`, `uvicorn-worker`, `httpx==0.28.1`,
   `numpy==2.5.4`, `pandas==3.1.1`, `matplotlib==3.11.2`, `scikit-learn==1.9.1`, `openpyxl==3.1.5`,
   `google-genai==3.0.0`; dev group `ruff`, `pytest`, `pytest-cov`, `pytest-asyncio`. Copy ice2kg's
   `[tool.uv] package = false`, Ruff, pytest (markers unit/integration/slow, `--strict-markers`) and
   coverage sections. `.python-version` = `3.13`; un-ignore it in the root `.gitignore`
   (`!apps/api/.python-version`). Run `uv lock`.
2. Copy as-is from `ice2kg/apps/api` (change only names/docstrings): `models/response_model.py`,
   `models/error_models.py`, `models/health_models.py`, `errors/app_error.py`,
   `errors/error_handlers.py` (+ test), `errors/error_presenter.py`, `errors/health_errors.py`,
   `utils/response_utils.py` (+ test), `middleware/cache_control_middleware.py` (+ test),
   `tests/__init__.py`.
3. Adapt: `main.py` (no Neo4j/auth/LLM lifespan closing; call `font_utils.register_inter_fonts()` and
   `matplotlib.use("Agg")` at startup), `config/settings_config.py` (only `app_env`, `cors_origins`,
   `cors_origins_list`), `constants/app_constants.py` (`PORT = 50001`, `PROJECT_DETAILS` name
   "DEMATELab API", `PROJECT_SETTINGS` docs URLs, `CACHE_CONTROL_SETTINGS`, `PROJECT_PATHS` with
   `FONTS_DIR`), `api/v1/api.py` (health only for now), `features/health_feature.py` (API status only,
   no dependency checks), `routers/health.py` (+ test).
4. `utils/response_utils.py`: add `download_bytes(content: bytes, filename, media_type)` next to the
   text `download`, with `Content-Disposition: attachment; filename="..."`; tests for both.
5. `.env.example` (`APP_ENV`, `CORS_ORIGINS=http://localhost:3000`, `WEB_CONCURRENCY=2`), `.dockerignore`
   (ice2kg list), `apps/api/AGENTS.md` (ice2kg's, minus Neo4j/sandbox/auth/LLM-gateway sections, plus a
   "Numerical parity" section: never change maths without updating fixtures from `qt-app/`, and the
   upload/download patterns from this plan), `CLAUDE.md` (imports AGENTS.md), `README.md`.
6. Delete `.gitkeep` files in folders that now contain files; delete `apps/api/dependencies/` (no auth).

Done when `uv run python main.py` serves `/api/docs`, `/api/v1/health`, `/api/v1/is-alive`, and
`uv run ruff format --check . && uv run ruff check . && uv run pytest` passes.

### Phase 2: Parity fixtures (before porting any maths)

1. `scripts/generate_parity_fixtures.py` at the repo root, run with the Qt environment:
   `uv run --python 3.13 --project qt-app/DEMATELab python scripts/generate_parity_fixtures.py`. It imports
   `DEMATELab.analysis_service`, `DEMATELab.matrix_parsers`, `DEMATELab.clustering_service` from
   `qt-app/`. `apps/api` never imports it.
2. Cases (deterministic, written into the script):
   - `small`: 3 factors, 2 experts (weights 0.6/0.4), hand-written labels per scale (standard and Z).
   - `weights3`: 4 factors, 3 experts with weights 0.334/0.333/0.333.
   - `fuzzy_example`, `grey_example`: read from `data/examples/*.xlsx` with the Qt workbook parser, using
     the sheet count as expert count and equal default weights.
   - `zero`: all "No influence" (expected error message).
   - `mmde_tie`: a matrix with repeated values (MMDE ordering is stable-sorted) and equal prominences
     (ranking tie order).
   Each case × each solver it applies to (standard cases → dematel, fuzzy, grey; Z cases → fuzzy Z) ×
   each of the 5 threshold methods.
3. Output per run: `apps/api/tests/fixtures/parity/<case>__<solver>__<threshold>.json` with
   `request` (AnalysisRequest body), `result` (every result field as nested lists), `crisp_total_matrix`
   (computed as `_to_numeric_2d_array` does), `summary_order` (`np.argsort(prominence)[::-1]`),
   `cluster` (`cluster_total_matrix` labels and numeric codes for that crisp total, or the error message
   when it raises), and
   `numpy_version`. Error cases store `error_message`.
4. Also copy the two example workbooks plus hand-made bad workbooks (wrong size, unknown label,
   mismatched names, blank names, wrong sheet count, differing names across sheets, labelled
   `(n+1)×(n+1)`) into `apps/api/tests/fixtures/imports/`, and store the Qt parser output or error for
   each in `.json` next to them.
5. Commit script and fixtures together.

Done when the fixture folder holds one file per case × solver × threshold and every import fixture has
an expected output.

### Phase 3: Constants, models, utils

1. `constants/linguistic_constants.py`: `LinguisticScale`, `DEFAULT_LINGUISTIC_MAP`,
   `DEFAULT_FUZZY_LINGUISTIC_MAP`, `DEFAULT_GREY_LINGUISTIC_MAP`, Z influence/reliability terms,
   `DEFAULT_Z_LINGUISTIC_MAP` (values verbatim from `constants.py:21-132`), `NO_INFLUENCE_LABEL`,
   `Z_NO_INFLUENCE_DEFAULT`.
2. `constants/solver_constants.py`: `SolverType` enum, `ThresholdMethod` enum, alias maps, display
   labels (solver: "DEMATEL", "Fuzzy DEMATEL", "Grey DEMATEL", "Fuzzy Z-DEMATEL"; result type
   "Classical DEMATEL" etc.; thresholds "Average", "First quartile", "Median", "Third quartile",
   "Maximum Mean De-Entropy"), limits (factors 2–100 default 4, experts 1–50 default 2).
3. `constants/weight_constants.py`: decimals 3, step 0.001, tolerance 0.005.
4. `constants/chart_constants.py` (all `DematelPlotStyle` defaults and the GUI overrides, heatmap
   titles/labels/cmap, dpi values), `constants/cluster_constants.py` (`CLUSTER_NAMES`, colours,
   `n_clusters=4`, `random_state=42`), `constants/import_constants.py` (5 MB, `.xlsx`),
   `constants/llm_constants.py` (providers, default models from `results_viewer_widget.py:1245` table,
   URLs, OpenRouter headers, system message, temperature 0.4, timeout 120 s, Azure api-version
   `2024-06-01`).
5. Request models with validators implementing Settled Decision 5 and alias normalisation; result,
   summary, scale, weight, import and explanation models per the contract. Every float array is
   `List[float]`/nested lists; conversion lives in `utils/matrix_utils.py`.
6. `utils/triangular_utils.py` (`_fuzzy_add`, `_fuzzy_subtract`, defuzzify), `utils/interval_utils.py`
   (`_interval_add`, `_interval_subtract`, whiten), `utils/matrix_utils.py` (ndarray ↔ lists),
   `utils/font_utils.py` (register `assets/fonts/*.ttf` with matplotlib, set
   `rcParams["font.family"] = ["Inter", "DejaVu Sans"]`), `utils/figure_utils.py` (figure → PNG bytes
   with `bbox_inches="tight"`, always `plt.close(fig)`).

### Phase 4: Solver features

1. `linguistic_conversion_feature.py`: crisp, fuzzy, grey and Z converters as methods; strip cells,
   case-sensitive lookup; unknown label → `UnknownLinguisticTermError` (422) whose public message names
   expert, row and column factor and the label; shape errors → `InvalidAnalysisInputError`.
2. `mmde_threshold_feature.py`: port `compute_mmde_threshold` verbatim (stable sort, natural-log
   entropy, first argmax, min over dispatch × receiver pairs).
3. `threshold_feature.py`: average, quartiles (`np.quantile`, default interpolation), median, MMDE,
   applied to the crisp total matrix the caller passes. One implementation replaces the three
   per-engine copies; behaviour identical.
4. `crisp_dematel_feature.py`, `fuzzy_dematel_feature.py`, `grey_dematel_feature.py`: engine steps
   ported verbatim (direct, normalise, total via `np.linalg.inv`, R/C, prominence/relation, crisp
   values, cause `>= 0` / effect `< 0`, threshold). Engine validation errors become
   `InvalidAnalysisInputError` with the Qt messages; "All matrix cells are set to \"No influence\"…"
   and inversion failures become `AnalysisFailedError` (422, Qt text as public message). Each returns
   an internal `solver_models` result including the crisp total matrix.
5. `weight_normalization_feature.py`: `_normalize_weight_inputs` and `_equal_weight_defaults` verbatim;
   sum outside tolerance → `InvalidWeightsError` (422, "Expert weights must sum to 1.").
6. `analysis_feature.py`: request → weight correction → diagonal forced to the solver's no-influence
   label → conversion → engine → result model. Fuzzy Z = Z converter + fuzzy engine, result
   `solver_type="fuzzy_z_dematel"`. CPU work runs via `asyncio.to_thread` (ice2kg pattern).
7. `result_summary_feature.py`: the summary block described in the contract.

### Phase 5: Import, export and charts

1. `utils/excel_matrix_utils.py` + `features/matrix_import_feature.py`: port the two used parsers
   (`matrix_parsers.py:21-150,266-348`) with identical rules and messages (`{source}` prefixes,
   allowed-value list, sheet-count message), plus the workbook → expert mapping from
   `matrix_editor_widget.py:611-656` (all-names match → by name, else by order; reported as
   `matched_by`), plus the editor-level checks and messages from `matrix_editor_widget.py:370-378,451-468`
   ("Imported factor names must match the matrix size.", blank/duplicate (case-insensitive) names,
   "Imported matrix must be exactly n x n.", "Unsupported imported value: …"), with an import fixture for
   each. Read with `pd.read_excel(BytesIO, header=None, sheet_name=..., engine="openpyxl")`;
   keep `fillna("")` before `astype(str)` and test under pandas 3.1.1. Errors → `InvalidImportError`
   (422) with the Qt message. Size/extension → `UploadTooLargeError` / `UnsupportedFileError`.
2. `features/xlsx_export_feature.py`: reproduce `results_viewer_widget.py:1397-1490` exactly: sheet
   order (3 matrix sheets named by result kind, truncated to 31 chars; `R_C_Scores`; `Summary`), crisp
   values unrounded, tuple strings with 4 decimals for fuzzy/grey, `"(…) (crisp)"` cells, Summary rows
   Threshold Method (the method key, e.g. `mmde`) / Threshold Value / Cause Group / Effect Group. Z sheets are named "Fuzzy …" as in
   Qt (sheet names are a file format; only on-screen labels change). Written with `pd.ExcelWriter`
   (openpyxl) into `BytesIO`. Router returns `download_bytes(..., "dematel_results.xlsx",
   XLSX_MEDIA_TYPE)`.
3. `features/clustering_feature.py`: `cluster_total_matrix` verbatim (off-diagonal, KMeans(4,
   random_state=42, n_init="auto"), ranked names, diagonal label -1/"No influence", ≥ 4 values else
   `ClusteringFailedError` (422, Qt message)).
4. `features/causal_diagram_chart_feature.py`: port `plot_dematel_influence_map` and its helpers
   (`dematel_visualization.py:53-302`), called as the GUI does: crisp total matrix, threshold value or
   mean(T) when missing, figsize (8, 6), dpi from the query (120 display, 300 download). If the file
   approaches 300 lines, split geometry/edges into `utils/influence_map_utils.py`. Figure 8×6, `dpi`
   from the query (100 or 300), `tight_layout()` before saving.
5. `features/heatmap_chart_feature.py`: standard (`imshow`, default cmap, colourbar "Relation
   Strength", title "Total Relation Matrix Heatmap", ticks rotated 45° right-aligned, figsize 8×6,
   `dpi` 100 or 300, `tight_layout()`)
   and cluster mode (discrete colours and ticks from `results_viewer_widget.py:1052-1123`, title
   "Cluster-Based Heatmap"), from `clustering_feature`. Use a new `Figure` per request (no pyplot global
   state) so concurrent requests are safe.
6. Routers `analysis_export.py`, `analysis_charts.py` (`dpi` restricted to the allowed values,
   `mode` enum) and `imports.py` (`UploadFile`, `Form`), one statement per handler.

### Phase 6: AI explanation

1. `services/llm_provider_service.py`: one `httpx.AsyncClient` per call (timeout 120 s);
   OpenAI-compatible POST for Groq/OpenRouter/OpenAI (URLs, headers, system message, temperature from
   constants) and Azure (`/openai/v1` suffix → `/chat/completions` with model in body; else
   `/openai/deployments/{model}/chat/completions?api-version=2024-06-01`; `api-key` header). Wraps
   httpx/HTTP/JSON errors in typed errors with distinct public messages (Qt showed the raw provider
   error; these keep it distinguishable without echoing secrets): 401/403 → `LlmAuthError` (502, "The AI
   provider rejected the API key."), 429 → `LlmRateLimitError` (502, "The AI provider rate limit was
   reached. Try again later."), timeout → `LlmTimeoutError` (504, "The AI provider did not answer in
   time."), other → `LlmProviderError` (502, "The AI provider request failed (HTTP {status})." or
   "...could not be reached."). The provider's response body goes to `detail` (logged) only after
   removing the key. Never logs the key or headers.
2. `services/gemini_service.py`: `genai.Client(api_key=...)` `models.generate_content`, run in
   `asyncio.to_thread` with a 120 s `asyncio.wait_for`; empty text → `LlmProviderError`.
3. `features/explanation_prompt_feature.py`: `build_result_payload` and `build_prompt` text verbatim,
   except the real `solver_type` and grey interval vectors (Settled Decision 8).
4. `features/explanation_feature.py`: validate provider, key required (`MissingApiKeyError`, 422,
   "Please enter an API key."), Azure endpoint required ("Azure OpenAI endpoint is required."), default
   model per provider when blank; recompute analysis; call the service; return `{text, provider, model}`.
   `api_key` is a `SecretStr` with `repr=False`.
5. `routers/explanations.py`; `routers/weights.py` serves both weight endpoints. Error handlers must not echo request bodies (keys) in validation errors:
   test that a 422 from `/explanations` never contains the key.

### Phase 7: Scales, weights, router registration

1. `features/scales_feature.py` + `routers/scales.py`; `routers/weights.py` (`/weights/defaults`,
   `/weights/normalize`).
2. Register all routers in `api/v1/api.py`, all public (no auth).

### Phase 8: Docker, Compose, Nginx, Make

1. `apps/api/Dockerfile.dev` and `Dockerfile.prod` copied from ice2kg (python:3.13-slim, uv 0.12.10,
   `/opt/venv`, dev `uvicorn --reload` on 50001, prod gunicorn + uvicorn workers, user `app` uid 1001).
   Add `MPLCONFIGDIR=/tmp/matplotlib` and `fonts-dejavu-core` (fallback font); no data volume (stateless).
2. Root `docker-compose-dev.yml` (`name: dematelab-dev`): `api` (`dematelab-api`, `50001:50001`,
   `env_file ./apps/api/.env`, `APP_ENV=development`, bind mount `./apps/api:/app:z`, `is-alive`
   healthcheck as ice2kg) and `web` (`dematelab-web`, `3000:3000`, `./apps/web:/app:z` + anonymous
   `/app/node_modules`, `depends_on: api`). Root `docker-compose-prod.yml` (`name: dematelab`): `api`,
   `web`, `nginx` (only published service, `${HTTP_PORT:-80}:80`). Both on `app-network`. Until the
   frontend plan's Phase 1, the `web` service sits under Compose profile `web` **in both files**, and
   prod `nginx` declares `depends_on: {api: {condition: service_healthy}, web: {condition:
   service_started, required: false}}`, so `make dev` and `make prod` work with the API alone.
3. `nginx/Dockerfile.prod` and `nginx/nginx.prod.conf` from ice2kg without sandbox/auth blocks:
   `/api/` → `api:50001` (`proxy_buffering off`, `proxy_read_timeout 300s`), `/` → `web:3000`,
   `client_max_body_size 20m`, commented HTTPS block. Keep ice2kg's runtime resolver pattern
   (`resolver ${NGINX_LOCAL_RESOLVERS}` + `set $web_upstream` / `set $api_upstream`,
   `nginx.prod.conf:3-14`) so Nginx starts even when `web` is absent (`/` then returns 502 until it
   exists).
4. Root `Makefile` from ice2kg: `help`, `setup` (`ENV_FILES := apps/api/.env apps/web/.env`, skipping
   files whose `.example` does not exist yet), `dev`, `api`, `web`, `down`, `restart`, `ps`, `logs`,
   `rebuild`, `urls`, `sh-api`, `sh-web`, `check`, `check-api`, `check-web`, `test`, `test-api`,
   `test-web`, `lint`, `typecheck`, `format`, `install`, `prod*`. Drop db/auth/sandbox/cypher targets.
   Web targets print a clear message when `apps/web/package.json` is missing.
5. `qt-app/` keeps its own `Makefile` and compose files; root `README.md` documents
   `make -C qt-app dev` for the legacy app.
6. Decisions in `docs/decisions/` (ice2kg format, one per file): rebuild in `apps/` with FastAPI and
   TanStack Start; Docker Compose with Nginx as only public entry; each service has its own env file;
   Make entrypoint with container-first checks; stateless API with server-rendered charts; AI keys
   supplied per request. Copy ice2kg's four `_*-authoring-guide--do-not-delete.md` files, replacing
   the "Project Rules" section with DEMATELab's (parity, `qt-app/` read-only, no imports from it).

### Phase 9: Tests and docs

1. Parity tests (`tests/parity_integration_test.py`): for every fixture, the feature result and the
   HTTP response equal the fixture with `numpy.testing.assert_allclose(rtol=0, atol=1e-12)`; groups,
   labels, threshold method equal exactly; error fixtures produce the same public message.
2. Cluster parity: cluster labels and codes equal the fixture.
3. Import parity: every import fixture gives the same matrix/names or the same error message.
4. XLSX: open the export with openpyxl and assert sheet names, headers, cell values and order against
   the Qt layout for one crisp, one fuzzy, one grey and one Z case.
5. Charts: PNG signature, no exception for every solver, both heatmap modes and both dpi values; the
   300 dpi image is about 3× the 100 dpi width; cluster mode error path returns 422.
6. Summary: ranking order and strongest relation equal the fixture `summary_order` incl. the tie case.
7. Explanation: provider services tested with `httpx.MockTransport` / a mocked Gemini client (URL,
   headers, body, Azure URL variants, error wrapping); feature tests for missing key/endpoint, default
   models, real solver type in the payload, 401/429/timeout mapping; key never in logs (`caplog`) or
   error bodies.
8. Unit tests for every util, feature and router (validation 422s, alias handling, weight correction
   cases incl. 3 experts and over/under tolerance).
9. Rewrite root `AGENTS.md` in the ice2kg shape (How the app fits together, Running the app, env files,
   workflow, pre-commit checklist), keeping the current Qt guidance as a "Legacy Qt app (`qt-app/`)"
   section with paths updated. Append an "Apps" section to `README.md` and mark the Qt sections legacy,
   updating `Example data/` → `data/examples/` and `exports/` → `qt-app/exports/` (append/adjust, do not
   remove the Qt instructions).

## Risks And Decision Gates

- **Numeric drift** between the Qt environment and the API. Gate: Phase 4 starts only after Phase 2
  fixtures are committed; both use the same pinned numpy/pandas/scikit-learn. A mismatch is a bug in
  the port, never a reason to loosen `atol` without a documented decision.
- **Qt environment on 3.13**: `uv run --project qt-app/DEMATELab` must resolve the 3.13 lock entries.
  If PySide6 blocks installation on a host, run the script inside the Qt dev container
  (`make -C qt-app shell`), which already has the environment.
- **matplotlib thread safety**: use the object-oriented `Figure` API only, never `pyplot`, in API code;
  gunicorn workers give process isolation in production.
- **Request size**: 100 factors × 50 experts ≈ 10 MB JSON. Nginx limit 20 MB; FastAPI has no default
  body limit. Acceptable for the Qt maxima.
- **AI keys in transit**: HTTPS is only commented out in Nginx (as in ice2kg). Production must enable
  TLS before the AI feature is used on the VPS; documented in the README and the AI-keys decision.
- **pandas 3 string dtype** may change empty-cell handling in the importer; covered by import fixtures.

## Testing And Validation

Inside the dev container (`make dev`, then):

```bash
make check-api                       # ruff format --check, ruff check, pytest
make test-api T="tests/parity_integration_test.py -v"
```

Outside Docker: `cd apps/api && uv sync && uv run ruff format --check . && uv run ruff check . && uv run pytest`.

Manual: `make dev`, open `http://localhost:50001/api/docs`; run a fixture request through
`/analysis`; download `/analysis/export/xlsx` and compare with a Qt export of the same input
(`make -C qt-app dev`, `http://localhost:6080`); open both PNG charts and compare visually with the Qt
tabs; import both `data/examples/` workbooks. `make prod` then `curl http://localhost/api/v1/health`.

## Acceptance Criteria

- All endpoints in the contract exist, appear in `/api/docs`, and return the documented shapes.
- Every parity, cluster and import fixture passes; XLSX layout tests pass.
- Invalid input returns 4xx with a public message and no stack trace or API key.
- `make check-api` passes; every code file in `apps/api` ≤ 300 lines; nothing in `apps/api` imports
  `qt-app` or reads outside `apps/api`.
- `make dev` and `make prod` start the API healthy (and Nginx in prod); `make dev` works before
  `apps/web` exists.
- Root `AGENTS.md`, `README.md`, `apps/api/AGENTS.md`, `apps/api/README.md` and the decision records
  describe the new setup; Qt instructions remain as legacy.

## Plan Validity

Valid for branch `restructure/apps-api-web` at `df78b5c` with the Qt sources unchanged. Revalidate if
`qt-app/DEMATELab/DEMATELab/*.py` or `constants.py` change, if `qt-app/DEMATELab/uv.lock` versions
change, or if ice2kg's API skeleton files are restructured.

## Handoff Notes

- Order: Phase 1 → 2 → 3 → 4 → 5/6/7 (independent) → 8 → 9. Tests are written with each phase; Phase 9
  is the completeness pass.
- Settled Decisions and Known Qt Behaviour Kept must not be reopened without new evidence.
- No blockers. The frontend plan depends on the contract above; change the contract only by updating
  both plans.

## Open Questions

None.
