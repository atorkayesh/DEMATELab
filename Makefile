# DEMATELab: dev, check, and production entrypoints for the rebuilt app (apps/). `make help` lists
# every target. The legacy Qt app has its own Makefile: make -C qt-app dev (see README.md).
#
# Container first: the stack and every check run in Docker, so the host needs only Docker and
# make. Each target wraps a plain docker compose, uv, or pnpm command (make echoes it), and those
# commands keep working without make.
#
#   make dev      start the api (and web, once apps/web exists) with hot reload
#   make check    the pre-commit checks, inside the dev containers
#   make prod     start production on the VPS (Nginx is the only public entry)
#
# Narrow some targets with S=<service> (logs, restart) or T=<args> (test-api, test-web).

# Each service has its own env file (make setup creates it from its .env.example). Files whose
# .env.example does not exist yet (apps/web before the frontend plan) are skipped.
ENV_FILES := apps/api/.env apps/web/.env

# Fixed ports, the same inside and outside the containers. These values only feed the printed URLs
# and the port checks.
override WEB_PORT := 3000
override API_PORT := 50001

# Container engine: docker when installed, otherwise podman (the VPS). Override with
# `make DOCKER=podman <target>` or `export DOCKER=...`.
ifeq ($(origin DOCKER),undefined)
DOCKER := $(shell command -v docker >/dev/null 2>&1 && echo docker || echo podman)
endif

# Web is a regular service in both compose files; web targets still check that apps/web exists first.
WEB_READY := $(wildcard apps/web/package.json)

DEV  := $(DOCKER) compose -f docker-compose-dev.yml
PROD := $(DOCKER) compose -f docker-compose-prod.yml

DEV_PROJECT   := dematelab-dev
API_CONTAINER := dematelab-api
WEB_CONTAINER := dematelab-web

# -t only when a terminal is attached, so targets also work from scripts and pipes.
TTY      := $(shell [ -t 0 ] && echo -t)
API_EXEC := $(DOCKER) exec -i $(TTY) $(API_CONTAINER)
WEB_EXEC := $(DOCKER) exec -i $(TTY) $(WEB_CONTAINER)

# Checks need the dev containers: prod uses the same container names, but its images have no dev tools.
require_dev = @test "$$($(DOCKER) inspect -f '{{.State.Running}} {{index .Config.Labels "com.docker.compose.project"}}' $(1) 2>/dev/null)" = "true $(DEV_PROJECT)" \
	|| { echo "→ $(1) is not running from docker-compose-dev.yml (make dev)" >&2; exit 1; }

# Web targets explain themselves until apps/web exists.
require_web = @test -n "$(WEB_READY)" \
	|| { echo "→ apps/web/package.json does not exist yet: the web app comes with the frontend plan (docs/plans/)" >&2; exit 1; }

# Fail before Compose starts when a fixed port is taken by something else (for example another app
# using 3000/50001). Reuses a running dev container that already publishes the port.
require_port = @if [ "$$($(DOCKER) inspect -f '{{.State.Running}} {{index .Config.Labels "com.docker.compose.project"}}' $(2) 2>/dev/null)" = "true $(DEV_PROJECT)" ] \
	&& $(DOCKER) port $(2) $(1)/tcp 2>/dev/null | grep -q ':$(1)$$'; then :; \
	else \
		occupied=false; \
		if command -v nc >/dev/null 2>&1; then \
			nc -z localhost $(1) >/dev/null 2>&1 && occupied=true; \
		elif command -v ss >/dev/null 2>&1; then \
			ss -H -ltn 'sport = :$(1)' | grep -q . && occupied=true; \
		else \
			echo "→ checking fixed ports requires nc (macOS/Linux) or ss (Linux); install one and retry" >&2; exit 1; \
		fi; \
		if [ "$$occupied" = true ]; then \
			echo "→ port $(1) is already in use; free it and retry (DEMATELab uses fixed ports, see AGENTS.md)" >&2; \
			exit 1; \
		fi; \
	fi

.DEFAULT_GOAL := help
.PHONY: help setup urls dev api web down restart ps logs rebuild sh-api sh-web \
	check check-api check-web test test-api test-web lint typecheck format install \
	prod prod-down prod-restart prod-ps prod-logs _api-up _web-up

##@ Help

help: ## List every target
	@awk 'BEGIN {FS = ":.*## "} /^##@/ {printf "\n%s\n", substr($$0, 5)} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "Narrow with S=<service> (logs, restart, prod-logs, prod-restart) or T=<args> (test-api, test-web)."
	@echo "Legacy Qt app: make -C qt-app help"

##@ Setup

setup: ## Create each service's .env from its .env.example (never overwrites; skips missing examples)
	@for f in $(ENV_FILES); do \
		if [ -f $$f ]; then echo "→ $$f already exists, left unchanged"; \
		elif [ ! -f $$f.example ]; then echo "→ $$f.example does not exist yet, skipped"; \
		else cp $$f.example $$f && echo "→ created $$f from $$f.example"; fi; \
	done

##@ Development stack

dev: ## Start the api (and web once apps/web exists) with hot reload (detached; then make logs)
	$(call require_port,$(API_PORT),$(API_CONTAINER))
	$(if $(WEB_READY),$(call require_port,$(WEB_PORT),$(WEB_CONTAINER)))
	$(DEV) up -d --build --wait
	@$(MAKE) --no-print-directory urls

api: ## Start only the api
	$(call require_port,$(API_PORT),$(API_CONTAINER))
	$(DEV) up -d --build --wait api
	@echo "→ API docs http://localhost:$(API_PORT)/api/docs"

web: ## Start the web app (and the api it needs)
	$(require_web)
	$(call require_port,$(API_PORT),$(API_CONTAINER))
	$(call require_port,$(WEB_PORT),$(WEB_CONTAINER))
	$(DEV) up -d --build --wait web
	@$(MAKE) --no-print-directory urls

down: ## Stop and remove the dev containers
	$(DEV) down

restart: ## Restart the dev services, or one with S=api|web
	$(DEV) restart $(S)

ps: ## Show the dev containers and their health
	$(DEV) ps

logs: ## Follow dev logs, or one service's with S=api|web
	$(DEV) logs -f --tail=100 $(S)

rebuild: ## Rebuild the dev images and containers (after dependency changes)
	$(call require_port,$(API_PORT),$(API_CONTAINER))
	$(DEV) up -d --build --force-recreate --renew-anon-volumes --wait
	@$(MAKE) --no-print-directory urls

urls:
	@$(if $(WEB_READY),echo "→ Web           http://localhost:$(WEB_PORT)",echo "→ Web           not yet (apps/web comes with the frontend plan)")
	@echo "→ API docs      http://localhost:$(API_PORT)/api/docs"
	@echo "→ API health    http://localhost:$(API_PORT)/api/v1/health"

##@ Shells

sh-api: ## Open a shell in the api container
	$(DOCKER) exec -i $(TTY) $(API_CONTAINER) bash

sh-web: ## Open a shell in the web container
	$(require_web)
	$(DOCKER) exec -i $(TTY) $(WEB_CONTAINER) bash

##@ Checks (inside the dev containers)

check: check-api check-web ## All pre-commit checks for both apps

check-api: _api-up ## API checks: Ruff format check, Ruff lint, pytest
	$(API_EXEC) uv run ruff format --check .
	$(API_EXEC) uv run ruff check .
	$(API_EXEC) uv run pytest

check-web: _web-up ## Web checks: format check, lint, typecheck, tests
	$(WEB_EXEC) pnpm run format:check
	$(WEB_EXEC) pnpm run lint
	$(WEB_EXEC) pnpm run typecheck
	$(WEB_EXEC) pnpm run test

test: test-api test-web ## Run the api and web tests

test-api: _api-up ## Run pytest; T=<pytest args>, e.g. T="tests/parity_integration_test.py -v"
	$(API_EXEC) uv run pytest $(T)

test-web: _web-up ## Run the web tests; T=<filter>
	$(WEB_EXEC) pnpm run test $(T)

lint: _api-up ## Lint both apps (Ruff; the web linter once apps/web exists)
	$(API_EXEC) uv run ruff check .
	$(if $(WEB_READY),$(WEB_EXEC) pnpm run lint,@echo "→ apps/web does not exist yet, web lint skipped")

typecheck: _web-up ## Typecheck the web app
	$(WEB_EXEC) pnpm run typecheck

format: _api-up ## Format both apps (Ruff; the web formatter once apps/web exists); run before committing
	$(API_EXEC) uv run ruff format .
	$(if $(WEB_READY),$(WEB_EXEC) pnpm run format,@echo "→ apps/web does not exist yet, web format skipped")

_api-up:
	$(call require_dev,$(API_CONTAINER))

_web-up:
	$(require_web)
	$(call require_dev,$(WEB_CONTAINER))

##@ Dependencies

install: _api-up ## Install dependencies in the dev containers from the lockfiles (after a pull)
	$(API_EXEC) uv sync --frozen
	$(if $(WEB_READY),$(WEB_EXEC) pnpm install --frozen-lockfile,@echo "→ apps/web does not exist yet, web install skipped")

##@ Production (on the VPS)

prod: ## Build and start production (Nginx on HTTP_PORT, default 80, is the only public entry)
	$(PROD) up -d --build --wait

prod-down: ## Stop and remove the production containers
	$(PROD) down

prod-restart: ## Restart production, or one service with S=nginx|web|api
	$(PROD) restart $(S)

prod-ps: ## Show the production containers and their health
	$(PROD) ps

prod-logs: ## Follow production logs, or one service's with S=nginx|web|api
	$(PROD) logs -f --tail=100 $(S)
