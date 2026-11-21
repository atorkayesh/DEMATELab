# Make Is The Entrypoint And Checks Run In The Dev Containers

**Status:** Superseded by [just Is The Entrypoint And Checks Run In The Dev Containers](./2026-11-21-just-entrypoint-with-container-first-checks.md)
**Date:** 16 November, 2026
**Deciders:** Youpele Michael (with Claude Code)

## Decision

The root `Makefile` is the recommended entrypoint for running, checking, and deploying the rebuilt app
(`make help`). Checks (`make check-api`, `make test-api`, `make lint`, `make format`) run inside the dev
containers, which install the exact toolchain from the lockfiles. Make only wraps commands; `docker
compose` and `uv run` keep working directly, and running the API outside Docker stays supported. The Qt
app keeps its own Makefile (`make -C qt-app dev`).

## Context

The dev image installs exactly `uv.lock` (Python 3.13, numpy, pandas, scikit-learn, matplotlib at the
versions the parity fixtures were generated with). ice2kg uses the same approach.

## Alternatives Considered

- **Host-first checks:** need uv and Python 3.13 on every machine and can run a different BLAS than the
  containers; kept as an alternative.
- **A task runner (just, Task):** an extra tool; `make` ships with macOS and Linux.

## Consequences

- `make check-api` needs `make dev`; check targets verify the container belongs to the `dematelab-dev`
  project, because prod uses the same container names without dev tools.
- Web targets print a clear message when `apps/web/package.json` does not exist; `web` is a regular
  Compose service, so make passes no profile flags.
- The Qt compose project for development is also named `dematelab-dev` (`qt-app/docker-compose-dev.yml`);
  run one stack at a time.

## Related Work

- Plan: [Port The DEMATELab Backend To A Dockerised FastAPI `apps/api`](../plans/2026-11-16-port-backend-to-fastapi-api-plan.md)
- Decision: [Docker Compose with Nginx as the only public entry](./2026-11-16-docker-compose-with-nginx-as-only-public-entry.md)
