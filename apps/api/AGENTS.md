# DEMATELab API - Agent Guidelines

FastAPI API for DEMATELab: the four DEMATEL solvers, five threshold methods, Excel import, XLSX export,
charts, and the AI explanation, ported from the legacy Qt app. For the whole-app workflow (Docker,
cross-app changes), see the [root `AGENTS.md`](../../AGENTS.md). Human-facing setup is in
[`apps/api/README.md`](./README.md).

**Stack:** Python 3.13, FastAPI, numpy, pandas, scikit-learn, matplotlib, openpyxl, httpx, google-genai,
Pydantic Settings, uv, Ruff, pytest

---

## Commands

Run these in the dev container from the repo root: `make check-api`, `make test-api T="<pytest args>"`,
`make format`, `make lint`, `make sh-api` (root `AGENTS.md` → Running the App). The commands below
are what they run, and also work outside Docker.

```bash
cd apps/api

# Run locally (no other service needed)
cp .env.example .env
uv sync
uv run python main.py

# Format and lint (Ruff replaces Black; line length 120)
uv run ruff format .
uv run ruff check --fix .

# Checks to run before committing
uv run ruff format --check . && uv run ruff check . && uv run pytest

# Tests
uv run pytest -v                                   # All tests
uv run pytest -m "not integration" -v              # Skip integration (parity) tests
uv run pytest tests/parity_integration_test.py -v  # Numerical parity with the Qt app
uv run pytest --cov=. --cov-report=html            # Coverage
```

API docs are live at `http://localhost:50001/api/docs` when the API runs.

---

## Code Style

### Imports

Group imports (standard library, third-party, local), separated by blank lines and sorted
alphabetically within groups. Ruff's `I` rules enforce the order (`uv run ruff check --fix .`).

```python
# 1. Standard library
import time
from typing import Dict, Optional

# 2. Third-party
from fastapi import APIRouter

# 3. Local application
from models.solver_models import SolverOutput
from services.llm_provider_service import LlmProviderService
```

- Use **absolute imports** from the `apps/api` root (`from services.llm_provider_service import ...`).
- **Never** use relative imports between packages (`from . import`, `from .. import`).
- Import directly from module files, never through `__init__.py` re-exports.

### `__init__.py` files

`__init__.py` files contain **only a docstring**, nothing else:

```python
"""Features module."""
```

### Formatting and linting

- **Ruff** only: `ruff format` (Black-compatible) and `ruff check` (rules `E`, `F`, `I`, `B`), configured
  in `pyproject.toml` with a **120-character** line length. Black is not used.
- 4-space indentation, double quotes, trailing commas in multi-line structures.

### Type hints (required on every function)

- Use `Optional[T]`, not `T | None`.
- Use `List`, `Dict`, `Tuple` from `typing`, not `list`, `dict`, `tuple`.
- Avoid `Any` unless necessary.

### Naming

| Kind | Convention | Example |
|---|---|---|
| Functions, methods, modules | `snake_case` | `health_check`, `gemini_service.py` |
| Classes | `PascalCase` | `GeminiService` |
| Constants | `UPPER_SNAKE_CASE` | `PROJECT_DETAILS` |
| Private members | `_` prefix | `_get_driver` |
| Feature files | `*_feature.py` | `health_feature.py` |
| Service files | `*_service.py` | `llm_provider_service.py` |
| Model files | `*_model.py` / `*_models.py` | `response_model.py`, `health_models.py` |
| Config files | `*_config.py` | `settings_config.py` |
| Constant files | `*_constants.py` in `constants/` | `solver_constants.py` |
| Util files | `*_utils.py` | `response_utils.py` |
| Error files | `*_errors.py` (`app_error.py` for the base) | `analysis_errors.py` |

### Docstrings (Google style, required for public APIs)

```python
def compute(self, matrix: np.ndarray, method: ThresholdMethod) -> float:
    """
    Compute the threshold.

    Args:
        matrix: `n x n` crisp total relation matrix
        method: Threshold method

    Returns:
        float: Threshold value
    """
```

### Error handling (`errors/`)

- Every expected failure is an `AppError` subclass from `errors/` (one `*_errors.py` file per area).
  An `AppError` carries a stable `code` (e.g. `analysis_failed`), its `status_code`, a
  `public_message` that is safe to show, optional `data` to return with the error (e.g. health
  details), and an internal `detail` that is logged and never returned.
- Services wrap HTTP and SDK errors in the matching `AppError`, so features never handle raw
  library exceptions. Features raise `AppError`s; routers never catch anything.
- `ErrorHandlers` (registered in `main.py`) packages every failure, including request validation
  (422) and unexpected exceptions (500), as an `ApiResponseModel` with `success: false` and
  `error.code`. `ErrorPresenter` logs the details server-side.
- **Never expose internal errors in API responses** (exception text, URIs, credentials, stack traces).

### Class-based code

- Every module except routers is class-based: features, services, utils, error handlers, and
  middleware are classes with methods. Dependencies are passed to `__init__`, defaulting to the
  module-level instances (`ThresholdFeature(mmde_threshold_feature)`).
- Each feature and service module ends with one module-level instance, like
  `gemini_service = GeminiService()`. Import that instance; tests pass mocks to the constructor
  instead of patching import paths.
- Utils get real classes where they hold settings or state (`FigureRenderer(figure_size)`). A standalone
  `def` in `utils/` is allowed only when it is stateless, used in several places, and fits nowhere
  better; its docstring must say why it is not a method.
- Standalone `def`s allowed elsewhere: FastAPI route handlers, `lifespan` in `main.py`, and the cached
  `get_settings()`.

### File size

Every code file, tests included, stays at or below **300 lines**. Split by responsibility into a
second class or module (e.g. `causal_diagram_chart_feature.py` + `utils/influence_map_utils.py`), never
arbitrarily. See the [root `AGENTS.md`](../../AGENTS.md) → Development Workflow.

### Committing

Run `make format` and `make check-api`, fix every failure,
and re-run until they pass before committing (root `AGENTS.md` → Development Workflow).

---

## Numerical Parity

The API reproduces the legacy Qt app (`qt-app/DEMATELab/DEMATELab/`) number for number. Each ported module
names its Qt source file and lines in its docstring.

- **Never change maths, linguistic maps, thresholds, KMeans settings, the prompt text, or plot styling
  without regenerating the fixtures from `qt-app/`** and recording the decision. Fixtures are generated,
  never hand-written:

  ```bash
  # From the repository root, with the Qt environment (PySide6 included)
  uv run --frozen --python 3.13 --project qt-app/DEMATELab python scripts/generate_parity_fixtures.py
  ```

  It writes `tests/fixtures/parity/<case>__<solver>__<threshold>.json` (request, every result field,
  crisp total matrix, ranking order, strongest relation, cluster labels or errors),
  `tests/fixtures/imports/*.xlsx` + `.json` (Qt parser and matrix editor output or error), and
  `tests/fixtures/xlsx/*.xlsx` (the Qt viewer's own XLSX export). `apps/api` never imports or reads
  `qt-app/`; `tests/repository_rules_integration_test.py` checks this and the 300-line limit.
- Parity tolerance is `rtol=0, atol=1e-12`. Fixtures are generated on macOS (Accelerate BLAS); the dev
  container uses Linux (OpenBLAS), which differs by at most about 1e-13. A mismatch above the tolerance is
  a bug in the port, never a reason to loosen it without a decision record.
- Kept from Qt on purpose: cause group is `relation >= 0` but diagram nodes are green only for `> 0`;
  thresholds use the whole total matrix including the diagonal; diagram edges are `T > threshold`
  without the diagonal; fuzzy and grey normalisation use the upper component's scale; workbook sheets map to
  experts by name only if all names match (trimmed, case-insensitive), else by order; Qt's doubled
  "Uploaded sheet: Uploaded sheet: " prefix in factor-name import errors; Z export sheets are named "Fuzzy …".
- Known Qt edge case: in fuzzy DEMATEL an all-"No influence" input does not raise (the label is (0, 0, 0.25)),
  Qt inverts a singular `I - X` and returns values around 1e15 that depend on the BLAS library. There is no
  fixture for it. When two relations have the same magnitude, the "strongest relation" sign depends on the
  last bits (the parity test accepts either tied value).
- Labels fixed on purpose (Settled Decision 8 in the plan): results carry the real `solver_type` (Z is
  "Fuzzy Z-DEMATEL"), the AI payload uses the real solver type and includes grey intervals, the summary
  returns the threshold label and key, a blank AI model uses the viewer's default table, a failing
  cluster heatmap is a 422 instead of the standard heatmap, and cluster heatmap cells are coloured by their
  ranked label so they match the colourbar (Qt coloured by the raw KMeans id; clustering is unchanged).

---

## Architecture

### File organization

```
apps/api/
├── main.py              # FastAPI app, CORS, error handlers, middleware, Agg backend, Inter fonts
├── assets/fonts/        # Inter (from qt-app), registered with matplotlib at startup; no download
├── constants/           # linguistic, solver, weight, chart, cluster, import, llm, app constants
├── api/v1/api.py        # Router aggregation; every route is public (no accounts)
├── routers/             # One-statement handlers: health, scales, weights, analysis, analysis_export,
│                        # analysis_charts, imports, explanations
├── features/            # All logic: conversion, engines, thresholds, analysis, summary, clustering,
│                        # charts, XLSX export, imports, explanation prompt and flow
├── services/            # I/O only: llm_provider_service (httpx, incl. Anthropic), gemini_service (google-genai)
├── models/              # Pydantic request/response models; solver_models.py holds internal numpy outputs
├── utils/               # Helpers without I/O: response builder, number arithmetic, Excel parsing,
│                        # figure rendering, influence map geometry, fonts
├── errors/              # AppError hierarchy, ErrorPresenter, ErrorHandlers
├── config/              # settings_config.py (APP_ENV, CORS_ORIGINS)
├── middleware/          # cache_control_middleware.py
└── tests/               # Parity, import, XLSX, and repository-rule integration tests; fixtures/
```

### Analysis flow

```
AnalysisRequest (validated: names, limits, aliases, n x n)
  → WeightNormalizationFeature (GUI correction: thousandths, ±0.005, from the last expert backwards)
  → LinguisticConversionFeature (diagonal forced to the solver's no-influence label, then the scale)
  → CrispDematelFeature | FuzzyDematelFeature (fuzzy and fuzzy Z) | GreyDematelFeature → SolverOutput
  → result model + ResultSummaryFeature
```

Export, charts, and the explanation call `AnalysisFeature.solve` with the same request (the API is
stateless). CPU work runs in `asyncio.to_thread`. Charts use the `Figure` API only, never `pyplot`.

### Layers

| Layer | Holds | May call | Called by |
|---|---|---|---|
| `routers/` | Route declarations. Each handler is one statement: call a feature, return through `ResponseBuilder`. | features, `ResponseBuilder`, models | FastAPI |
| `features/` | All business logic. | other features (one direction, no cycles), services, utils, models, errors | routers, other features |
| `services/` | I/O only: external APIs. No business decisions. | utils, models, errors, config | **features only** |
| `utils/` | Small helpers without I/O. | other utils, models, errors | features, services, routers (`ResponseBuilder` only) |
| `errors/` | Error types and their packaging into responses. | models, utils | raised anywhere; handlers registered in `main.py` |
| `models/` | Pydantic schemas and internal solver dataclasses. | models | everything |

- A router never touches a service, and services never call features.
- One router per file.
- Nothing in `apps/api` imports from, reads, or starts anything in `qt-app/`.

### API versioning and responses

- Routes are mounted at `/api/v1` (`api/v1/api.py`).
- JSON responses use `ApiResponseModel` (`success`, `message`, `data`, `metadata`, `error`) built with
  `ResponseBuilder`. Errors are `AppError`s with a stable `error.code`; request validation is 422
  `validation_error` with `error.fields`.
- File responses: `ResponseBuilder.download_bytes(content, filename, media_type)` for attachments (XLSX)
  and `ResponseBuilder.image(content, media_type)` for inline PNG charts.
- Uploads: routers declare `UploadFile` and `Form` fields with `Annotated[...]`; the feature reads at most
  5 MB + 1 byte (`UploadTooLargeError`, 413), accepts only `.xlsx` that openpyxl can open
  (`UnsupportedFileError`, 422), and returns the Qt parser or editor message as `InvalidImportError` (422).

### AI explanation

- Keys come with each request (`ExplanationRequest.api_key`, a `SecretStr` with `repr=False`), are used
  once, and are never stored, logged, or returned. `ErrorPresenter` logs only field paths and error types
  for validation errors; provider bodies are logged only after removing the key.
- Providers: Gemini (google-genai), OpenAI, OpenRouter, Groq (OpenAI-compatible), Azure OpenAI, and
  Anthropic (Messages API, `x-api-key`, `anthropic-version: 2023-06-01`). `constants/llm_constants.py` is
  the single model catalogue (`PROVIDER_MODELS`, 3-7 models each, source URL per list; `DEFAULT_MODELS`,
  a cheap model), served by `GET /explanations/providers`. Requested models must be in the list; Azure
  OpenAI takes any deployment name, has no default, and requires one.
- Errors: 422 `missing_api_key` / `missing_azure_endpoint` / `missing_azure_deployment` /
  `unsupported_model`; 502 `llm_auth_failed` (401/403), `llm_rate_limited` (429),
  `azure_deployment_not_found` (Azure 404 / DeploymentNotFound), `llm_provider_error`; 504 `llm_timeout` (120 s).
- Services take an injectable `httpx` transport / Gemini client factory; tests never call providers.

### Health checks

| Route | Checks | Status codes |
|---|---|---|
| `GET /api/v1/health` | API only (no dependencies) | 200 |
| `GET /api/v1/is-alive` | Liveness | 200 |

---

## Environment

`apps/api/.env` (template `.env.example`). Compose loads it and overrides only `APP_ENV`.

```bash
APP_ENV=development                  # development | production
CORS_ORIGINS=http://localhost:3000   # Comma-separated; the public origin on the VPS
WEB_CONCURRENCY=2                    # Gunicorn workers (production image only)
```

No AI keys or other secrets belong here.

---

## Adding an Endpoint

1. Define Pydantic models in `models/<area>_models.py`.
2. Put I/O in a service class and logic in a feature class, with constructor injection and a module-level
   instance at the end of each file.
3. Add failure cases as `AppError` subclasses in `errors/<area>_errors.py`.
4. Create `routers/<area>.py` with `APIRouter(prefix=..., tags=[...])`; one statement per handler.
5. Register the router in `api/v1/api.py`.
6. Add co-located tests, and parity fixtures if Qt behaviour is involved.
7. Document the endpoint in `apps/api/README.md`.

---

## Testing

- Unit tests are co-located (`features/analysis_feature.py` → `features/analysis_feature_test.py`); every
  feature, util, service, and router has one.
- Integration tests live in `tests/` as `*_integration_test.py` (parity, imports, XLSX, repository rules).
- Classes `Test[ClassName]` (`unittest.TestCase` / `IsolatedAsyncioTestCase`), markers `unit`,
  `integration`, `slow` (`--strict-markers`).
- Mock external providers (`httpx.MockTransport`, a fake Gemini client factory).

---

## Pitfalls

❌ Relative imports between packages → ✅ Absolute imports from the `apps/api` root  
❌ Re-exports in `__init__.py` → ✅ Docstring only; import from source files  
❌ Changing a formula or label "to fix it" → ✅ Regenerate fixtures from `qt-app/` and record a decision  
❌ Loosening the parity tolerance → ✅ Find the port bug  
❌ Importing or reading `qt-app/` → ✅ Copy or rewrite into `apps/api`; only the fixture script uses it  
❌ `pyplot` in API code → ✅ `matplotlib.figure.Figure` via `FigureRenderer`  
❌ Logging request bodies or provider responses with the key → ✅ Paths and types only; strip the key  
❌ Logic or service calls in a router → ✅ One statement calling a feature, via `ResponseBuilder`  
❌ Raising `HTTPException` or returning raw error text → ✅ Raise an `AppError` from `errors/`  
❌ A code file over 300 lines → ✅ Split it by responsibility  
