# DEMATELab API

FastAPI backend for DEMATELab. It runs classical, fuzzy, grey, and fuzzy Z-DEMATEL with five threshold
methods, imports Excel matrices, exports the results workbook, renders the causal diagram and heatmaps as
PNG, and generates AI explanations, with the same numbers as the legacy Qt app (`qt-app/`). The API is
stateless: every analysis-derived endpoint receives the full analysis request.

Agent and coding guidelines: [`AGENTS.md`](./AGENTS.md).

## Run with Docker (recommended)

From the repository root:

```bash
just setup    # creates apps/api/.env from .env.example
just dev
```

The API runs at `http://localhost:50001` with hot reload. Port 50001 must be free (`just dev` stops with a
message if another app, for example ice2kg, uses it). See the root [`README.md`](../../README.md).

## Run locally

Requires [uv](https://docs.astral.sh/uv/). No other service is needed.

```bash
cd apps/api
cp .env.example .env
uv sync
uv run python main.py
```

- API: `http://localhost:50001/api/v1`
- Docs: `http://localhost:50001/api/docs` (ReDoc: `/api/redoc`)

## Checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

`tests/parity_integration_test.py` compares every solver and threshold with fixtures generated from the Qt
app; see `AGENTS.md` → Numerical Parity for how to regenerate them.

## Endpoints

All JSON responses use `{success, message, data, metadata, error}`; on failure `message` is safe to show
and `error.code` is stable (`validation_error` with `error.fields` for invalid requests).

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | API status (no dependencies). |
| GET | `/api/v1/is-alive` | Liveness (Docker health check). |
| GET | `/api/v1/scales` | Linguistic terms per solver family (standard; fuzzy Z with influence and reliability terms), default/diagonal labels, solver and threshold options (key + label), factor/expert limits, weight rules. |
| POST | `/api/v1/weights/defaults` | `{expert_count}` (1–50) → equal weights in thousandths, remainder to the first experts. |
| POST | `/api/v1/weights/normalize` | `{weights}` → corrected weights (±0.005 tolerance), or 422 `invalid_weights` "Expert weights must sum to 1." |
| POST | `/api/v1/analysis` | `AnalysisRequest` → `{result, summary, corrected_weights}`. |
| POST | `/api/v1/analysis/export/xlsx` | `AnalysisRequest` → `dematel_results.xlsx` (the Qt GUI export layout). |
| POST | `/api/v1/analysis/charts/causal-diagram?dpi=100\|300` | `AnalysisRequest` → `image/png`. |
| POST | `/api/v1/analysis/charts/heatmap?mode=standard\|cluster&dpi=100\|300` | `AnalysisRequest` → `image/png`; 422 `clustering_failed` in cluster mode when clustering is impossible. |
| POST | `/api/v1/imports/matrix` | multipart `file` (.xlsx, ≤ 5 MB), `factor_count` → `{factor_names, matrix}`. |
| POST | `/api/v1/imports/workbook` | multipart `file`, `factor_count`, `expert_names` (repeated) → `{factor_names, matrices: [{expert_name, matrix}], matched_by: "name" \| "order"}`. |
| GET | `/api/v1/explanations/providers` | `{providers: [{id, label, models, default_model, free_text_model}]}`: the model catalogue (Azure OpenAI: no models, no default, free-text deployment name). |
| POST | `/api/v1/explanations` | `{analysis, provider, api_key, model?, azure_endpoint?}` → `{text, provider, model}`. Providers: `Gemini`, `OpenAI`, `Azure OpenAI`, `OpenRouter`, `Groq`, `Anthropic`. A blank model uses the default; other models must be in the provider's list (422 `unsupported_model`); Azure needs a deployment name (422 `missing_azure_deployment`). |

`AnalysisRequest`:

```json
{
  "solver_type": "dematel | fuzzy_dematel | grey_dematel | fuzzy_z_dematel",
  "threshold_method": "average | first_quartile | median | third_quartile | mmde",
  "factors": ["Cost", "Quality", "Time"],
  "experts": [
    {"name": "Expert 1", "weight": 0.6, "matrix": [["No influence", "Low influence", "High influence"], ["...", "...", "..."], ["...", "...", "..."]]}
  ]
}
```

- Aliases from the Qt app are accepted (`"Fuzzy Z-DEMATEL"`, `"fz_dematel"`, `"Maximum Mean De-Entropy"`, …).
- 2–100 factors (trimmed, required, unique case-sensitively); 1–50 experts (names required, duplicates
  allowed); weights 0–1, corrected like the Qt GUI; the diagonal is always the solver's no-influence label.
- `result` has the Qt field names: crisp `direct_matrix`/`normalized_matrix`/`total_matrix`; fuzzy and fuzzy
  Z `fuzzy_*`; grey `grey_*`; all with `r`, `c`, `prominence`, `relation`, `cause_group`, `effect_group`,
  `threshold_method`, `threshold_value`, `crisp_total_matrix`. Numbers are not rounded.

Example:

```bash
curl -s -X POST http://localhost:50001/api/v1/analysis/charts/heatmap?mode=cluster \
  -H 'Content-Type: application/json' -d @request.json -o heatmap.png
```

AI keys are used once and never stored or logged. On the VPS the app is served only over HTTPS, through the
shared proxy (`nginx/conf.d/dematelab.conf`).

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | `development` or `production` (set by Compose) |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins (the public origin on the VPS) |
| `WEB_CONCURRENCY` | `2` | Gunicorn workers in the production image |

## Docker images

- `Dockerfile.dev`: uvicorn with `--reload`; installs all dependencies from `uv.lock`.
- `Dockerfile.prod`: gunicorn with Uvicorn workers (`WEB_CONCURRENCY`), runtime dependencies only,
  non-root user `app` (uid 1001), no volume.

Both install exactly `uv.lock` (`uv sync --frozen`), add `fonts-dejavu-core` as the chart font fallback,
and set `MPLCONFIGDIR=/tmp/matplotlib`. After changing dependencies, run `uv lock` and commit `uv.lock`.
