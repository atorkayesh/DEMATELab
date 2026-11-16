# Shortcuts for the DEMATELab Docker setups. Each target runs a plain `docker compose`
# command (echoed as it runs; also listed in README.md, "Running with Docker").
# Run from the repository root. Needs Docker (Compose 2.24+) and make.
#
#   make dev | make prod     build and start one setup (stopping the other one first)
#   make logs | restart | shell | status | down
#                            act on whichever setup is running
#
# Only one setup runs at a time: both publish the same port. To pick one explicitly,
# add MODE=dev or MODE=prod, e.g. `make logs MODE=prod`.

APP          := DEMATELab
PROJECT      := dematelab
SERVICE      := dematelab
ENV_FILE     := DEMATELab/.env
DEFAULT_PORT := 6080

# DEMATELab's .env sits next to its Dockerfiles, not next to the compose files, so pass
# it to compose for ${NOVNC_PORT} and ${NOVNC_BIND} too (env_file only feeds the container).
COMPOSE_ENV_FILE = $(if $(wildcard $(ENV_FILE)), --env-file $(ENV_FILE))

compose = docker compose -f docker-compose-$(1).yml$(COMPOSE_ENV_FILE)

# ID of the dev or prod container if it exists (running or stopped), otherwise empty.
container = $(shell docker ps -aq --filter 'name=^$(PROJECT)-$(1)$$' 2>/dev/null)

# Stop and remove one setup if it exists. Uses the compose project name, so it works
# even without the setup's .env file.
stop = if [ -n "$(call container,$(1))" ]; then echo "Stopping the $(1) setup"; docker compose -p $(PROJECT)-$(1) down; fi

# Which setup the instance commands act on: dev, prod, both, or none. Only a MODE given on
# the make command line counts, so an unrelated MODE variable in your shell is ignored.
ifneq ($(origin MODE),command line)
MODE := $(if $(call container,dev),$(if $(call container,prod),both,dev),$(if $(call container,prod),prod,none))
endif
ifeq ($(filter dev prod both none,$(MODE)),)
$(error MODE must be dev or prod, not '$(MODE)')
endif

# Shell command printing a setting from $(ENV_FILE) the way compose reads it: the last
# occurrence, without quotes, carriage returns, or a trailing comment.
read_env = sed -n 's/^$(1)=//p' $(ENV_FILE) 2>/dev/null | tail -n 1 | tr -d "\"'\r" | sed -e 's/[[:space:]][[:space:]]*\#.*//' -e 's/[[:space:]]*$$//'

# Same precedence as compose: shell environment, then $(ENV_FILE), then the default.
NOVNC_PORT ?= $(or $(shell $(call read_env,NOVNC_PORT)),$(DEFAULT_PORT))
URL = http://localhost:$(NOVNC_PORT)

.DEFAULT_GOAL := help
.PHONY: help dev prod logs restart shell status down check-running check-prod-env

help:
	@echo "$(APP) Docker shortcuts (run from the repository root):"
	@echo "  make dev       build and start the dev setup (reloads on code changes)"
	@echo "  make prod      build and start the prod setup (needs VNC_PASSWORD in $(ENV_FILE))"
	@echo "  make logs      follow the logs of the running setup"
	@echo "  make restart   restart the running setup"
	@echo "  make shell     open a shell in the running setup"
	@echo "  make status    show which setup is running"
	@echo "  make down      stop and remove the running setup"
	@echo "dev and prod stop each other first. Add MODE=dev or MODE=prod to pick one explicitly."

dev:
	@$(call stop,prod)
	$(call compose,dev) up -d --build --wait
	@echo "$(APP) (dev) is running at $(URL)"

prod: check-prod-env
	@$(call stop,dev)
	$(call compose,prod) up -d --build --wait
	@echo "$(APP) (prod) is running at $(URL)"

logs: check-running
	$(call compose,$(MODE)) logs -f --tail=200

restart: check-running
	$(call compose,$(MODE)) restart

shell: check-running
	$(call compose,$(MODE)) exec -u app $(SERVICE) bash

status:
	@if [ "$(MODE)" = none ]; then \
	  echo "Nothing is running. Start it with 'make dev' or 'make prod'."; \
	else \
	  docker ps -a --filter 'name=^$(PROJECT)-(dev|prod)$$' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'; \
	fi

down:
	@if [ "$(MODE)" = none ]; then echo "Nothing is running."; fi
	@$(if $(filter dev both,$(MODE)),$(call stop,dev),true)
	@$(if $(filter prod both,$(MODE)),$(call stop,prod),true)

check-running:
	@case "$(MODE)" in \
	  none) echo "Nothing is running. Start it with 'make dev' or 'make prod'."; exit 1 ;; \
	  both) echo "Both dev and prod exist; pick one with MODE=dev or MODE=prod."; exit 1 ;; \
	esac

check-prod-env:
	@if [ ! -f $(ENV_FILE) ]; then \
	  echo "Missing $(ENV_FILE): copy $(ENV_FILE).example to $(ENV_FILE) and set VNC_PASSWORD."; exit 1; \
	fi
	@password="$$($(call read_env,VNC_PASSWORD))"; \
	if [ -z "$$password" ]; then \
	  echo "VNC_PASSWORD is empty in $(ENV_FILE); the prod setup requires a password."; exit 1; \
	fi; \
	if [ $${#password} -gt 8 ]; then \
	  echo "Note: VNC passwords are limited to 8 characters; only the first 8 are checked."; \
	fi
