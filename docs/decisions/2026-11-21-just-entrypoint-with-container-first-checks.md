# just Is The Entrypoint And Checks Run In The Dev Containers

**Status:** Accepted
**Date:** 21 November, 2026
**Deciders:** Youpele Michael (with Claude Code)

## Decision

The root `justfile` replaces the root `Makefile` as the entrypoint for running, checking, and deploying the
rebuilt app (`just` lists every recipe). Recipe names are unchanged (`just dev`, `just check-api`,
`just prod`, …); what used to be `S=<service>` and `T=<args>` are now recipe arguments (`just logs api`,
`just test-api tests/parity_integration_test.py -v`). Checks still run inside the dev containers, and just
still only wraps commands: `docker compose` and `uv run` keep working directly. The legacy Qt app keeps its
own Makefile (`make -C qt-app dev`).
The shared proxy's recipes are the module `proxy` (`nginx/justfile`): `just proxy up-all`.

## Context

The shared HTTPS proxy for the VPS is orchestrated with just (see
[A Shared HTTPS Proxy Serves The App On The VPS](./2026-11-21-shared-https-proxy-on-the-vps.md)); using one task
runner for the app and the proxy was preferred. just has real recipe arguments, `just --list` for
discoverability, recipe groups, modules, and no `.PHONY`/tab pitfalls.

## Alternatives Considered

- **Keep make:** ships with macOS and Linux, but argument passing (`S=`, `T=`) and listing need workarounds,
  and the VPS orchestration would use a second tool.
- **A Makefile that forwards to just:** keeps old habits working, but two entrypoints to maintain.

## Consequences

- just must be installed on every machine (README lists `brew`, `apt`, prebuilt binaries, `winget`).
- Container-first rules are unchanged: `just check-api` needs `just dev`; check recipes verify the container
  belongs to the `dematelab-dev` project, because prod uses the same container names without dev tools.
- Historical plans, reports and research keep their `make …` commands as written.

## Related Work

- Supersedes: [Make Is The Entrypoint And Checks Run In The Dev Containers](./2026-11-16-make-entrypoint-with-container-first-checks.md)
- Plan (DEMATELab repository): `docs/plans/2026-11-21-shared-https-proxy-and-just-plan.md`
