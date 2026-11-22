# DEMATELab

> **Rebuild in progress:** DEMATELab is being rebuilt as a web app in `apps/` (FastAPI API in
> `apps/api`, TanStack Start UI in `apps/web`). See [Apps](#apps) below. The sections up to "Running with
> Docker" describe the **legacy desktop app**, which now lives in `qt-app/`.

A desktop application for cause-and-effect analysis using DEMATEL and its extensions. Built with Python and PySide6, it provides an interactive GUI for entering expert judgments, running the analysis, visualizing results, and generating AI-powered interpretations.

---

## Features

- **Four solver types:** Classical DEMATEL, Fuzzy DEMATEL, Grey DEMATEL, and Fuzzy Z-DEMATEL
- **Multi-expert support** with customizable weights
- **Five threshold methods:** Average, First Quartile, Median, Third Quartile, and Maximum Mean De-Entropy (MMDE)
- **Interactive matrix editor** with linguistic dropdown inputs per expert
- **Results viewer** with tabs for matrices, R/C scores, causal diagram, and heatmap
- **Cluster analysis** of the total relation matrix (K-Means)
- **Export** results to XLSX and visualizations to PNG
- **AI-generated explanation** of results via LLMs

---

## Requirements

- Python 3.10 or higher
- Windows, macOS, or Linux

---

## Installation (legacy Qt app)

### From GitHub

```bash
pip install git+https://github.com/atorkayesh/DEMATELab.git
```

### From source

```bash
git clone https://github.com/atorkayesh/DEMATELab.git
cd DEMATELab/qt-app/DEMATELab
pip install .
```

---

## Usage

After installation, launch the application from the terminal:

```bash
DEMATELab
```

For Windows setup, launch it in the terminal: 

```bash
python -m DEMATELab
```

### Workflow

1. Select a **solver type** and **threshold method** from the Setup panel
2. Set the number of **experts** and **factors**
3. Click **Generate Input Forms** and fill in factor and expert names with weights
4. Click **Next: Create Matrix Editor** and fill in the linguistic judgment matrix for each expert
5. Click **Run Analysis** to compute results
6. Browse the **Results** tabs: Summary, Matrices, R/C Scores, Causal Diagram, Heatmap
7. Optionally generate an **AI Explanation** by selecting an engine and entering your API key

---

## Supported Linguistic Scales

**Standard / Fuzzy / Grey DEMATEL**
| Label | Crisp | Fuzzy (l, m, u) | Grey [l, u] |
|---|---|---|---|
| No influence | 0 | (0.00, 0.00, 0.25) | [0.00, 0.00] |
| Low influence | 1 | (0.00, 0.25, 0.50) | [0.00, 0.25] |
| Medium influence | 2 | (0.25, 0.50, 0.75) | [0.25, 0.50] |
| High influence | 3 | (0.50, 0.75, 1.00) | [0.50, 0.75] |
| Extreme influence | 4 | (0.75, 1.00, 1.00) | [0.75, 1.00] |

**Fuzzy Z-DEMATEL** uses combined influence–reliability judgments (e.g. *"High influence with M reliability"*), where reliability levels are VL, L, M, H, and VH.

---

## AI Explanation

The AI tab generates an academic-style narrative interpretation of the results. In the web app, pick an
**AI Provider** and one of its models (the list and the cheap default come from the API,
`GET /api/v1/explanations/providers`):

| AI Provider | Default model | Other models |
|---|---|---|
| Gemini | gemini-3.5-flash-lite | gemini-4-carbon, gemini-4-argon, gemini-4-hydrogen, gemini-3.8-flash, gemini-3.6-flash, gemini-3.1-flash-lite |
| OpenAI | gpt-6-luna | gpt-6-astra, gpt-6.1-sol, gpt-6.1-terra |
| Azure OpenAI | none: enter your deployment name | |
| OpenRouter | openai/gpt-6-luna | anthropic/claude-sonnet-5.5, openai/gpt-6.1-sol, google/gemini-4-carbon, x-ai/grok-4.7, qwen/qwen4-max, deepseek/deepseek-v4.1-flash |
| Groq | openai/gpt-oss-20b | openai/gpt-oss-120b, llama-3.3-70b-versatile, llama-3.1-8b-instant |
| Anthropic | claude-haiku-5-5 | claude-opus-5-5, claude-sonnet-5-5, claude-fable-5-2 |

The legacy Qt app keeps its own engine list (no Anthropic) and free-text model field.

An API key is required. Keys are never stored — they are only held in memory for the duration of the session.

---

## Running with Docker (legacy Qt app)

The commands in this section belong to the legacy app in `qt-app/`: run them with `make -C qt-app <target>` from the repository root, or from inside `qt-app/` (the root `Makefile` now runs the rebuilt app, see [Apps](#apps)).

The app can also run in a container and be used from a browser (via noVNC), with no local Python or Qt setup.

**Requirements:** to run it locally, install Docker and Make:

- **macOS:** [Docker Desktop](https://docs.docker.com/desktop/) (or OrbStack). Make comes with the Xcode Command Line Tools: `xcode-select --install`.
- **Linux:** [Docker Engine](https://docs.docker.com/engine/install/) with the Compose plugin, installed from Docker's own repository (distribution packages such as `docker.io` can be too old), and `make` (for example `sudo apt install make`). Add your user to the `docker` group rather than running with `sudo`.
- **Windows:** [Docker Desktop](https://docs.docker.com/desktop/), plus Make in one of two ways: inside WSL (`sudo apt install make`, then run the commands from WSL), or install it with `winget install ezwinports.make` or `choco install make` and run it from Git Bash (Git for Windows doesn't include Make). Without Make, use the `docker compose` commands below.

Docker Engine 25 or newer and Docker Compose 2.24 or newer are required (current Docker Desktop includes both).

All commands run from `qt-app/` (or as `make -C qt-app <target>` from the repository root):

```bash
make dev       # build and start the dev setup, then print http://localhost:6080
make prod      # build and start the prod setup (needs VNC_PASSWORD, see below)
make logs      # follow the logs
make restart   # restart the container
make status    # show which setup is running
make shell     # open a shell in the container
make down      # stop and remove the container
```

Only one setup runs at a time, because both use the same port: `make dev` stops prod first, and `make prod` stops dev. `logs`, `restart`, `status`, `shell` and `down` act on whichever one is running. To pick one explicitly, add `MODE=dev` or `MODE=prod`, for example `make logs MODE=prod`. Run `make` on its own to list the commands.

| | Dev (`docker-compose-dev.yml`) | Prod (`docker-compose-prod.yml`) |
|---|---|---|
| Image | `DEMATELab/Dockerfile.dev` (includes dev tools) | `DEMATELab/Dockerfile.prod` (runtime only) |
| Source | Mounted from `DEMATELab/`; the app restarts when a `.py` file changes | Baked into the image; rebuild to update |
| Password | None by default | `VNC_PASSWORD` required in `DEMATELab/.env` |
| Exports | `qt-app/exports/` on the host | `dematelab-exports` Docker volume |
| Address | `127.0.0.1:${NOVNC_PORT:-6080}` | `127.0.0.1:${NOVNC_PORT:-6080}` (`NOVNC_BIND` to change the interface) |

Setup for production:

```bash
cp DEMATELab/.env.example DEMATELab/.env   # then set VNC_PASSWORD
make prod
```

Without Make, use the plain `docker compose` commands (these are what the `make` targets run):

```bash
docker compose -f docker-compose-dev.yml --env-file DEMATELab/.env up -d --build --wait
docker compose -f docker-compose-dev.yml --env-file DEMATELab/.env logs -f
docker compose -f docker-compose-dev.yml --env-file DEMATELab/.env restart
docker compose -f docker-compose-dev.yml --env-file DEMATELab/.env exec -u app dematelab bash
docker compose -f docker-compose-dev.yml --env-file DEMATELab/.env down
```

For prod, use `docker-compose-prod.yml` instead and stop dev first. Leave out `--env-file DEMATELab/.env` if that file doesn't exist; it is needed so compose applies `NOVNC_PORT` and `NOVNC_BIND` from it.

Notes:
- In the app's file dialogs, the example workbooks are in `examples/` (read-only, mounted from `data/examples/`) and exports should be saved to `exports/` (`qt-app/exports/` on the host).
- Everyone who opens the URL shares the same app session, so the production setup suits one user at a time. noVNC traffic is not encrypted: before exposing it beyond `localhost`, put it behind a TLS reverse proxy with its own login. VNC passwords are limited to 8 characters.
- Without a `VNC_PASSWORD`, `make prod` stops before starting. With plain `docker compose`, the prod container logs the error once and waits instead of restarting, and after about 2 minutes `docker compose ps` reports it as unhealthy.
- Dev and prod share `DEMATELab/.env`, so setting `VNC_PASSWORD` for prod also adds a password to the dev session.
- On Linux, the container runs the app as the owner of `qt-app/exports/` (normally you), so exported files are yours. Keep the `qt-app/exports/` folder that comes with the repository: if it is missing, Docker creates it owned by root and the app then runs as root, so exported files are owned by root. With rootless Docker or Podman the app also runs as root inside the container, which is your own user on the host, so exports are still yours.
- On Windows, dev reload works automatically with Docker Desktop's default WSL2 backend. If edits don't restart the app (for example with the Hyper-V backend), set `WATCHFILES_FORCE_POLLING=true` in `DEMATELab/.env`.
- Dependencies are locked in `DEMATELab/uv.lock`; after changing `DEMATELab/pyproject.toml`, run `uv lock` in `DEMATELab/` and rebuild.

## Apps

The rebuilt DEMATELab runs in Docker with the root `justfile` (`just` lists every recipe). Requirements: Docker
(Engine 25+, Compose 2.24+) and [just](https://just.systems). Install just with `brew install just` (macOS), `sudo apt install just` (Debian 13+/Ubuntu 24.04+) or the
[prebuilt binaries](https://just.systems/man/en/pre-built-binaries.html) (Linux, any distribution), or
`winget install Casey.Just` (Windows).

```bash
just setup     # create apps/api/.env and apps/web/.env from their examples
just dev       # start the API and the web app with hot reload
just check-api # format check, lint, and tests inside the API container
just down
just prod      # production: API (gunicorn) and web, served by the VPS's shared HTTPS proxy
```

- Web app: `http://localhost:3000` (details: [`apps/web/README.md`](apps/web/README.md)).
- API: `http://localhost:50001/api/v1`, interactive docs at `http://localhost:50001/api/docs`. Endpoints,
  request format, and local runs without Docker: [`apps/api/README.md`](apps/api/README.md).
- Ports 50001 and 3000 are fixed; stop other apps using them first.
- The API gives the same numbers as the Qt app for the same input: tests compare it with fixtures generated
  from `qt-app/` (`scripts/generate_parity_fixtures.py`).
- AI explanations use the key the user enters with each request; it is never stored, and travels only
  over HTTPS on the VPS.
- In production, one shared Nginx serves this app and Policy Coherence Kit on ports 80 and 443.
  Set the deployment hostnames in the proxy environment file. Its config and the orchestration of
  both apps live in [`nginx/`](nginx/README.md): `just proxy up-all`, `just proxy up-dematelab`,
  `just proxy nginx-reload`, `just proxy` to list them
  ([decision](docs/decisions/2026-11-21-shared-https-proxy-on-the-vps.md)).
- The legacy Qt app is unchanged: `make -C qt-app dev` (see "Running with Docker (legacy Qt app)").

## License

MIT License — see [LICENSE](LICENSE) for details.
