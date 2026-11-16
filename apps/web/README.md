# DEMATELab Web

TanStack Start frontend for DEMATELab, the cause-and-effect (DEMATEL) analysis tool. It replaces the
Qt desktop window (`qt-app/`, kept for reference) with a web app; every number comes from the API in
`apps/api`.

The home page (`/`) is one question per screen (Typeform style): solver, threshold method, number of
experts, number of factors, factor names, expert names and weights, one matrix per expert (with Excel
import), and a review step that runs the analysis. Results (summary, matrices, R/C scores, causal
diagram, heatmaps, AI explanation, exports) open full width. Browser Back/Forward move between the
steps (`?step=`), and any earlier answer can be changed; results then show an "out of date" banner
with Re-run. The API health is at `/status` (not linked).

Nothing is saved: a reload starts a new analysis, as in the Qt app.

The logo is `public/logo.png`, with `public/favicon.ico` (48 px) and `public/apple-touch-icon.png`
(180 px), rendered from `qt-app/DEMATELab/DEMATELab/assets/logo.png`.

Agent and coding guidelines: [`AGENTS.md`](./AGENTS.md).

## Run with Docker (recommended)

From the repository root:

```bash
make setup    # creates apps/web/.env and apps/api/.env from their examples
make dev
```

The web app runs at `http://localhost:3000` with hot reload, the API at `http://localhost:50001`.
See the root [`README.md`](../../README.md).

## Run locally

Requires Node.js 24 and pnpm 12, and a running API (see [`apps/api/README.md`](../api/README.md)).

```bash
cd apps/web
cp .env.example .env
pnpm install
pnpm run dev
```

Open `http://localhost:3000`.

## Checks

```bash
pnpm run format:check
pnpm run lint
pnpm run typecheck
pnpm run test
pnpm run build
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `VITE_APP_ENV` | `development` | `development` or `production` |
| `VITE_API_BASE_URL` | empty | API origin; `http://localhost:50001` in development, empty in production (same origin through Nginx) |

`VITE_*` values end up in the browser bundle: never put secrets in `apps/web/.env`. AI provider keys
are typed into the results page per request and never stored.
