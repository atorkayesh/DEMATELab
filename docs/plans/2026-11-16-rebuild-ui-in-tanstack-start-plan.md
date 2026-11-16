# Rebuild The DEMATELab UI In TanStack Start (`apps/web`)

**Date:** 16 November, 2026
**Status:** Ready for implementation (after the backend plan's API contract is implemented)
**Owner:** Youpele Michael (planned with Claude Code)
**Created:** 2026-11-16 14:10 CET · **Last modified:** 2026-11-16 14:40 CET
**Inspected:** `/Users/youpele/DevWorld/FZJ/dematelab`, branch `restructure/apps-api-web`, commit `df78b5c`,
clean worktree. Conventions and theme from `/Users/youpele/DevWorld/FZJ/ice2kg/apps/web`, inspected the
same day.

## Summary

The PySide6 interface is rebuilt as a TanStack Start web app in `apps/web` with feature parity: analysis
setup, factors and expert weights, the per-expert matrix editor with Excel import, and the results view
(summary, matrices, R/C scores, causal diagram, heatmaps, AI explanation, exports). All computation comes
from the FastAPI service defined in
[Port The DEMATELab Backend To A Dockerised FastAPI `apps/api`](2026-11-16-port-backend-to-fastapi-api-plan.md).
Look and tooling follow ice2kg (navy ink `#023d6b`, Manrope, shadcn on Base UI), with **warmer whites**.

## Related Work

- Backend plan: [Port The DEMATELab Backend To A Dockerised FastAPI `apps/api`](2026-11-16-port-backend-to-fastapi-api-plan.md)
  (API contract, Compose/Nginx/Make files with the `web` service behind a profile).
- ice2kg reference: `apps/web/AGENTS.md`, `src/styles.css`, `components/general/AppLayout.tsx`,
  `AppHeader.tsx`, `AppFooter.tsx`, `PageHeader.tsx`, `routes/status.tsx`, `utils/download.utils.ts`.
- JuGit issue: none identified.

## Problem

The only UI is a Qt desktop window (served over noVNC in Docker). The goal is a normal web app on the
same VPS, talking to the new API.

## Goals

- Every Qt screen, control and action listed under Parity Inventory works in the browser against the API.
- Visual design: ice2kg tokens with the warm-white palette below; works from 320 px wide.
- Code follows ice2kg's `apps/web/AGENTS.md`: folder roles, `*.hook.ts` / `*.service.ts` /
  `*.utils.ts` / `*.interface.ts` / `*.constants.ts`, one named component per PascalCase file, `@/`
  imports, Zod for env and API responses, TanStack Query for all requests (no `useEffect` fetching),
  Biome, strict TypeScript, Vitest co-located tests, every code file ≤ 300 lines.
- `make dev` serves the web app on `http://localhost:3000`; `make prod` serves it behind Nginx;
  `make check-web` passes.

## Non-Goals

- Any computation in the browser beyond display formatting (rounding, tuple strings).
- Accounts, saved projects, persistence across reloads (Qt has none).
- Dark mode (ice2kg does not use it; keep the `.dark` block from shadcn but never toggle it).
- Z-DEMATEL import (the API has none), PDF export, table sorting, tooltips (none in Qt).
- Interactive (client-side) charts: charts are the API's PNGs.

## Settled Decisions

1. **One route for the workflow** (`/`), built like Qt as progressive cards: Analysis Setup → Factors
   and Experts → Matrix Input → Results. Plus `/status` (API health, unlinked, as ice2kg) and a 404.
   No auth, no `_authed` routes, no `.env.server`.
2. **Client state** in one Zustand store (`store/analysis.store.ts`; add `zustand`): setup, factors,
   experts, matrices per expert, and the **request snapshot** used for the current results. Results,
   charts, exports and the AI explanation always use that snapshot, so editing inputs after a run never
   mixes old results with new inputs. Nothing is persisted (no localStorage), matching Qt.
3. **Server data** through TanStack Query: `useScales` (`GET /scales`, `staleTime: Infinity`, loaded
   before the setup card renders), `useRunAnalysis` mutation, chart queries keyed by snapshot hash +
   mode + dpi, import / export / explanation mutations. Defaults, labels, limits and term lists come
   from `/scales`; the web app hard-codes none of them.
4. **Charts** are `<img>` elements from PNG blobs (object URLs revoked on change), requested with
   `dpi=100`. Zoom In / Zoom Out scale the image by 1.2× per click inside a scroll container, like Qt.
   Downloads request `dpi=300`.
5. **Summary PNG** is captured client-side with `html-to-image` (`toPng`, `pixelRatio: 2`) from the
   summary panel, file `summary.png`. All downloads use ice2kg's `saveBlob` util.
6. **AI explanation output is plain text** (`whitespace-pre-wrap`), as in Qt. The API key lives only in
   the AI panel's component state (password input), is sent once per request, and is never put in the
   store, query keys, URLs or logs.
7. **UX corrections over Qt** (safety only, no behaviour removed):
   - "Generate Input Forms" asks for confirmation when later cards already hold data (Qt wipes silently).
   - Changing between the standard and Z solver families shows Qt's warning text; on confirm the matrix
     editor is **regenerated** (as the Qt message promises) and results are cleared; Cancel restores the
     previous solver.
   - Cause/effect factor badges are auto-width pills, so long names are not clipped (Qt's fixed 28 px
     circles clip them).
   - Validation errors appear inline next to the card's action button (Qt used modal dialogs); texts
     are Qt's.
   - On-screen labels use the API's `result_type_label` and `threshold_method_label` (Z is labelled
     "Fuzzy Z-DEMATEL"; matrix tab names for Z read "Fuzzy Z …").
8. **Matrix editor rendering**: native `<select>` per cell (fast, keyboard accessible, ignores the mouse
   wheel when not focused by default), only the active expert tab mounted, rows and columns virtualised
   with `@tanstack/react-virtual` so 100 × 100 stays responsive. Frozen header row and column via
   sticky positioning.
9. Font **Manrope** (ice2kg) for the UI; the charts keep Inter (rendered by the API).
10. Ports: web **3000**, `VITE_API_BASE_URL=http://localhost:50001` in dev, empty in production (same
    origin through Nginx).

## Theme: ice2kg Colours, Warmer Whites

Copy ice2kg's `src/styles.css` and change only the light (`:root`) surfaces and neutrals. Ink, primary
and destructive stay identical.

| Token | ice2kg | DEMATELab |
| --- | --- | --- |
| `--background` | `#f9fafb` | `#faf8f4` |
| `--card`, `--popover` | `#ffffff` | `#fffdf9` |
| `--primary-foreground` | `#ffffff` | `#fffdf9` |
| `--secondary`, `--muted`, `--accent` | `#f3f4f6` | `#f4f1ea` |
| `--soft-2` | `#eceef2` | `#eeeae1` |
| `--border`, `--input` | `#e5e7eb` | `#e8e3d9` |
| `--line-strong` | `#d1d5db` | `#d6cfc2` |
| `--muted-foreground` | `#6b7280` | `#6f6a60` |
| `--ring`, `--placeholder` | `#9ca3af` | `#a39d91` |
| `--sidebar` | `oklch(0.985 0 0)` | `oklch(0.985 0.006 85)` |
| body gradient | `#ffffff` / `#fafafa` / `#f3f4f6` | `#fffdf9` / `#fbf9f5` / `#f4f1ea` |
| `--foreground`, `--primary`, `*-foreground` inks | `#023d6b` | `#023d6b` (unchanged) |

Domain colours (new tokens, used by badges and legends to match the charts): `--cause: #4e9965`,
`--cause-foreground: #f3faf5`, `--effect: #f97816`, `--effect-foreground: #fff4e5`; edited-cell
highlight `--cell-edited: #eef4f8` (a light tint of the navy, replacing Qt's teal `#e8f5f4`). Check every
text/background pair for WCAG AA (4.5:1) with a contrast checker during Phase 2 and record the values in
the PR; adjust only the lightness if a pair fails.

## Parity Inventory (source: Qt, active code `gui_app.py:1227-2241`)

**Header**: "DEMATELab" with subtitle "Cause and Effect Analysis"; logo from
`qt-app/DEMATELab/DEMATELab/assets/logo.png` converted to `public/logo.png`, `favicon.ico` and
`apple-touch-icon.png`. Footer like ice2kg (`APP_FULL_NAME` · Forschungszentrum Jülich · year).

**Card 1 – Analysis Setup** (subtitle "Choose your preferred solver and threshold identifier. The number of
experts and factors can be defined subsequently."): Solver type (DEMATEL, Fuzzy DEMATEL, Grey DEMATEL,
Fuzzy Z-DEMATEL; default DEMATEL), Threshold method (Average, First quartile, Median, Third quartile,
Maximum Mean De-Entropy; default Average), Number of experts (1–50, default 2), Number of factors
(2–100, default 4); steppers clamp on blur and reset non-integers to the minimum; button
"Generate Input Forms".

**Card 2 – Factors and Experts** ("Define the factors to be analyzed and specify expert weights."):
factor name inputs prefilled `F1..Fn`; expert name + weight (0–1, step 0.001, 3 decimals) prefilled
`Expert 1..k` and `POST /weights/defaults`; button "Next: Create Matrix Editor". Validation messages:
"All factor names must be filled.", "All expert names must be filled.", "Factor names must be unique."
(case-sensitive), "Expert weights must sum to 1." (tolerance 0.005). Name checks run client-side
(`validation.utils.ts`); the weight check and correction call `POST /weights/normalize`, and on success
the corrected weights are written back to the fields (no weight arithmetic in the browser).

**Card 3 – Matrix Input** ("Diagonal cells are fixed to the solver-specific no-influence value because a
factor cannot directly influence itself."): one tab per expert (right-aligned pill tabs); grid with
frozen factor headers; each cell a select of the solver's terms (5 standard or 25 Z labels), default =
no-influence label; diagonal disabled; cells differing from the default highlighted; per-tab
"Import Matrix from XLSX" (`POST /imports/matrix`; imported factor names rename factors everywhere,
including card 2) and "Import All Experts from XLSX" (`POST /imports/workbook`; hidden for Z); for Z the
per-tab button shows Qt's "Import Not Available" text. Import errors inline: "Import failed: {message}".
Button "Run Analysis"; analysis errors inline in red under the editor.

**Card 4 – Results** ("Analysis complete. Review the cause-and-effect relationships below."):
- Export bar: "Export Results to XLSX" (`dematel_results.xlsx`), "Export Summary to PNG" (`summary.png`),
  "Export Causal Diagram to PNG" (`causal_diagram.png`), "Export Standard Heatmap to PNG"
  (`heatmap_standard.png`), "Export Cluster Heatmap to PNG" (`heatmap_cluster.png`).
- Segmented tabs: Summary, {Direct, Normalized, Total Relation} Matrix (no prefix for classical;
  "Fuzzy …", "Grey …" or "Fuzzy Z …" otherwise),
  R/C Scores, Causal Diagram, Heatmap, AI Explanation.
- Summary: "Summary Insights" with four stat boxes (Driving Factors, Dependent Factors, Top Prominence
  2 dp, Strongest Relation signed 2 dp) and Qt's fixed descriptions; "Analysis Configuration" (Result
  Type, Threshold Method label, Threshold Value 4 dp or "—"); "Cause Group (Driving Factors)" and
  "Effect Group (Dependent Factors)" badges ("—" when empty); "Prominence and Relation Analysis" ranked
  list with bar, "P x.xx", "R ±x.xx".
- Matrix tables and R/C table: factor names as row and column headers, 4 decimals, fuzzy `(l, m, u)` and
  grey `(lo, hi)` tuples; R/C columns `Factor | R | C | R+C | R-C` (crisp) or
  `Factor | R | C | Prominence | Relation` (tuples); horizontal scroll for wide tables; not sortable.
- Causal Diagram: PNG (dpi 120) with zoom; "Total relation matrix is not available." placeholder.
- Heatmap: checkbox "Show cluster-based heatmap" switching `mode`; on a cluster error show Qt's
  "Could not generate cluster heatmap: {message}" and untick. "Export Cluster Heatmap to PNG" shows the
  same message on failure (no fallback file, see backend Settled Decision 8).
- AI Explanation: title "AI-Assisted Interpretation", Qt's note text, Engine (Gemini, OpenAI, Azure
  OpenAI, OpenRouter, Groq), API Key (password), Model (prefilled with the engine's default; placeholder
  "Leave blank to use the default model", Azure "Enter the Azure deployment name"); Azure opens a dialog
  "Azure OpenAI Endpoint" with Qt's text and placeholder, remembered while the results stay; status
  "Please enter an API key." / "Generating explanation..." / "Done" / error message; button
  "Generate Explanation" disabled while pending. On failure the status shows "Error" and the API's
  public message appears in the output area, as Qt does.

## Target Layout

```text
apps/web/
  package.json  pnpm-lock.yaml  pnpm-workspace.yaml  vite.config.ts  vitest.config.ts  tsr.config.json
  tsconfig.json  biome.json  components.json  .env.example  .dockerignore  Dockerfile.dev  Dockerfile.prod
  README.md  AGENTS.md  CLAUDE.md
  public/  logo.png  favicon.ico  apple-touch-icon.png
  src/
    router.tsx  routeTree.gen.ts  styles.css  env.ts  vite-env.d.ts
    routes/  __root.tsx  index.tsx  status.tsx
    lib/  utils.ts  query-client.ts  query-devtools.tsx
    components/
      ui/            shadcn: button, card, badge, input, select, tabs, checkbox, dialog, alert-dialog, separator, scroll-area
      general/       AppLayout, AppHeader, AppFooter, PageHeader, SectionCard, NumberStepper, InlineError, ZoomableImage, DownloadButton
      page-specific/
        analysis/    SetupCard, FactorsExpertsCard, FactorNameList, ExpertWeightList, MatrixInputCard,
                     ExpertTabs, MatrixGrid, MatrixCell, MatrixImportActions, ResultsCard, ExportBar,
                     ResultTabs, SummaryPanel, StatBox, ConfigurationPanel, FactorBadgeGroup,
                     ProminenceRanking, MatrixTable, ScoresTable, CausalDiagramPanel, HeatmapPanel,
                     ExplanationPanel, AzureEndpointDialog, SolverChangeDialog, ResetConfirmDialog
        status/      ApiHealthCard, StatusRow
    constants/   api.constants.ts  layout.constants.ts  analysis.constants.ts  results.constants.ts
                 explanation.constants.ts  health.constants.ts  query.constants.ts
    interfaces/  api.interface.ts  scales.interface.ts  analysis.interface.ts  result.interface.ts
                 import.interface.ts  explanation.interface.ts  health.interface.ts
    services/    scales.service.ts  weights.service.ts  analysis.service.ts  charts.service.ts
                 export.service.ts  import.service.ts  explanation.service.ts  health.service.ts
    hooks/       scales.hook.ts  analysis.hook.ts  chart.hook.ts  export.hook.ts  import.hook.ts
                 explanation.hook.ts  health.hook.ts  object-url.hook.ts
    store/       analysis.store.ts
    utils/       api.utils.ts  api-error.utils.ts  download.utils.ts  format.utils.ts
                 matrix.utils.ts  analysis-request.utils.ts  validation.utils.ts
```

`constants/` holds only UI text that the API does not provide (card titles/subtitles, button labels,
stat-box descriptions, placeholders, file names). `interfaces/` holds Zod schemas mirroring the API
models (discriminated result union on `solver_type`); every service parses responses with
`apiResponseSchema(...)`. Binary endpoints return `Blob` after checking `response.ok` (errors parsed with
`apiErrorBodySchema`).

## Phases

### Phase 1: Scaffold from ice2kg

1. Create the app with the TanStack CLI as ice2kg did (file routes, Nitro node-server), then align with
   ice2kg's files: `package.json` scripts and pinned versions (drop better-auth, d3, markdown packages,
   `auth:cli`; add `zustand`, `@tanstack/react-virtual`, `html-to-image`), `pnpm-workspace.yaml`,
   `vite.config.ts` (no `allowedHosts`), `vitest.config.ts`, `tsr.config.json`, `tsconfig.json`,
   `biome.json`, `components.json` (base-nova, neutral, lucide). Run `pnpm install` to create the lock.
2. `src/env.ts` (`VITE_APP_ENV`, `VITE_API_BASE_URL`), `.env.example`, `.dockerignore`,
   `Dockerfile.dev`, `Dockerfile.prod` (ice2kg's, without the auth data dir).
3. `lib/` and `utils/api.utils.ts` from ice2kg without credentials/401 handling; `api.interface.ts`;
   `download.utils.ts`; `api-error.utils.ts`.
4. Remove the `web` Compose profile from both compose files and the `required: false` on prod Nginx's
   `web` dependency (backend plan Phase 8.2); add `apps/web/.env` to `make setup`.
5. `AGENTS.md` (ice2kg's, minus auth/graph/chat/markdown sections, plus the store rule from Settled
   Decision 2 and the API-key rule from Settled Decision 6), `CLAUDE.md`, `README.md`.

Done when `make dev` serves a blank page on 3000 and `make check-web` passes.

### Phase 2: Theme and layout

1. `styles.css` per the Theme table, domain tokens registered in `@theme inline`.
2. `AppLayout`, `AppHeader` (static logo + "DEMATELab" + subtitle; no nav links, the app has one page),
   `AppFooter`, `PageHeader`, `SectionCard` (title, subtitle, body, footer slot); `layout.constants.ts`.
3. `__root.tsx` from ice2kg without the session `beforeLoad`; `/status` with `ApiHealthCard` adapted to
   the API-only health response; 404 component.
4. Contrast check (see Theme).

### Phase 3: API layer

1. Zod schemas for every API model in the backend contract; services for every endpoint; hooks as in
   Settled Decision 3; `analysis-request.utils.ts` builds the `AnalysisRequest` from store state.
2. Service tests with `vi.stubGlobal("fetch")`, including 4xx error bodies and blob downloads.

### Phase 4: Setup, factors and experts

1. `store/analysis.store.ts` with actions: `configureSetup`, `generateForms` (resets later steps),
   `setFactorName`, `setExpertName`, `setExpertWeight`, `applyCorrectedWeights`, `createMatrixEditor`,
   `setCell`, `applyImportedMatrix`, `applyImportedWorkbook`, `renameFactors`, `changeSolver`,
   `setResults(snapshot, data)`, `clearResults`. Unit-tested.
2. `SetupCard` with `NumberStepper` (clamping rules), selects from `/scales`, `SolverChangeDialog`,
   `ResetConfirmDialog`.
3. `FactorsExpertsCard` with name validation (`validation.utils.ts`, Qt messages) and weight correction
   via `POST /weights/normalize`.

### Phase 5: Matrix editor and import

1. `MatrixInputCard`, `ExpertTabs`, virtualised `MatrixGrid`, `MatrixCell` (native select, highlight,
   disabled diagonal), keyboard: Tab order row-major, arrow keys handled by the native select.
2. `MatrixImportActions` with hidden file inputs (`accept=".xlsx"`), import mutations, inline errors,
   Z behaviour.
3. "Run Analysis": validates again, builds the snapshot, calls `/analysis`, stores results, scrolls to
   the results card; errors inline.

### Phase 6: Results

1. `ResultsCard`, `ExportBar`, `ResultTabs` (segmented control on shadcn Tabs).
2. `SummaryPanel` and children (12-column layout collapsing to one column below `md`).
3. `MatrixTable`, `ScoresTable` with `format.utils.ts` (4 dp, tuple strings), horizontal scroll.
4. `CausalDiagramPanel` and `HeatmapPanel` with `ZoomableImage` and chart hooks; cluster error handling.
5. Exports: XLSX and chart PNGs via blob endpoints; summary PNG via `html-to-image`.

### Phase 7: AI explanation

`ExplanationPanel`, `AzureEndpointDialog`, `explanation.hook.ts`; key never leaves component state except
in the request body; tests assert the key is not in the store or query cache.

### Phase 8: Docs and finish

1. Root `AGENTS.md` and `README.md`: add the web app to the sections written by the backend plan.
2. Add a decision record "Warm-white variant of the ice2kg theme" with the token table.

## Risks And Decision Gates

- **Gate:** start Phase 3 only when the backend contract endpoints exist (or develop against
  `/api/openapi.json` with mocked services, then switch).
- **Large matrices** (100 × 100 × 50 experts): virtualisation and one mounted tab keep the DOM small;
  measure with React DevTools Profiler on a 100 × 100 matrix — cell change must not re-render the grid
  (store selectors per cell).
- **Large requests** (≈10 MB at the maxima) are sent for every chart/export; acceptable (Nginx limit
  20 MB). If slow in practice, add a cache keyed by snapshot hash in a later decision, not now.
- **`html-to-image`** must embed Manrope; test the exported PNG in Chrome, Firefox and Safari.
- **AI keys** require HTTPS in production (backend plan risk).

## Testing And Validation

```bash
make check-web                    # biome format check, lint, typecheck, vitest
make test-web T="src/store"       # focused runs
```

Tests: store actions; name validation; weight normalisation service and error display; formatters;
services (fetch stubs, Zod parsing, blob downloads, error bodies); components with Testing Library for
each card's happy path and error texts, the solver-change dialog (cancel restores), Z hiding import-all,
results tabs switching, explanation key handling.

Manual (in `make dev`, against the API): run every solver × threshold on a 4-factor matrix and compare
the summary, tables and charts with the Qt app on the same input (`make -C qt-app dev`); import both
`data/examples/` workbooks; download every export and open it; 100 × 100 matrix stays responsive;
layout at 320 px, tablet and desktop; `make prod` and the same smoke test through `http://localhost`.

## Acceptance Criteria

- Every item in the Parity Inventory works in the browser, with the Qt texts and the corrections in
  Settled Decision 7.
- Theme matches the table; AA contrast for text pairs; usable at 320 px.
- No computed DEMATEL value is produced in the browser; all come from the API.
- API key never stored, logged or cached.
- `make check-web` passes; every code file ≤ 300 lines (except `routeTree.gen.ts`).
- `make dev` and `make prod` serve the app; Nginx routes `/api/` to the API and everything else to web.

## Plan Validity

Valid for `df78b5c` plus the backend plan's contract. Revalidate if the API contract changes or ice2kg's
web conventions change significantly.

## Handoff Notes

- Order: backend plan Phases 1–8 first (at least the contract endpoints), then Phases 1–8 here.
- Do not reopen Settled Decisions or the theme values without new evidence (e.g. a failed contrast check,
  which may only change lightness).
- No blockers.

## Open Questions

None.
