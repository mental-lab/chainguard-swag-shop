# -----------------------------------------------------------------------------
# SWAG-SHOP — Makefile (simple and readable)
# -----------------------------------------------------------------------------

# Project knobs
PROJECT_NAME := SWAG-SHOP
PORT         ?= 8000
IMAGE        ?= swag-store:runtime
COMPOSE      ?= docker-compose

# Python / venv
VENV := .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip

# Use one shell per recipe (no fragile backslashes)
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# Default
.PHONY: all
all: help

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------
.PHONY: help
help: ## Show available targets
	@grep -E '^[a-zA-Z0-9_.-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sort \
	| awk 'BEGIN {FS=":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

# -----------------------------------------------------------------------------
# Setup / App
# -----------------------------------------------------------------------------
.PHONY: venv
venv: ## Create virtualenv if missing
	if [ ! -d "$(VENV)" ]; then python3 -m venv "$(VENV)"; fi

.PHONY: install
install: venv ## Install app dependencies
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

.PHONY: develop
develop: ## Run the Flask app locally
	$(PY) ./app.py

.PHONY: static
static: ## Build static site with Frozen-Flask
	$(PY) ./freezer.py

# Optional build args for authenticated index
BUILD_ARGS :=
ifneq ($(strip $(CGR_USERNAME)),)
BUILD_ARGS += --build-arg CGR_USERNAME=$(CGR_USERNAME)
endif
ifneq ($(strip $(CGR_TOKEN)),)
BUILD_ARGS += --build-arg CGR_TOKEN=$(CGR_TOKEN)
endif

.PHONY: runtime
runtime: ## Build the Docker image
	docker build . -t $(IMAGE)

# -----------------------------------------------------------------------------
# E2E (Playwright) + docker-compose
# -----------------------------------------------------------------------------
.PHONY: install-e2e
install-e2e: venv ## Install E2E deps and browsers
	$(PY) -m pip install -r requirements-e2e.txt
	$(VENV)/bin/playwright install

.PHONY: e2e-up
e2e-up: ## Start docker services for E2E
	$(COMPOSE) up -d --build
	echo "Waiting for services to be ready..."
	sleep 5
	curl -fsS "http://localhost:$(PORT)/" >/dev/null || echo "Warning: app may not be ready yet"

.PHONY: e2e-down
e2e-down: ## Stop docker services
	$(COMPOSE) down -v

.PHONY: e2e-logs
e2e-logs: ## Tail docker logs
	$(COMPOSE) logs -f

.PHONY: e2e-clean
e2e-clean: ## Remove E2E artifacts
	rm -rf test-results/ playwright-report/ .pytest_cache/

.PHONY: e2e-smoke
e2e-smoke: e2e-up ## Run smoke tests (headed Chromium)
	PYTHONPATH=. $(PY) -m pytest tests/e2e/test_smoke.py -v \
		--base-url="http://localhost:$(PORT)" \
		--browser chromium --headed
	$(MAKE) e2e-down

.PHONY: e2e-all
e2e-all: e2e-up ## Run all E2E tests (Chromium)
	PYTHONPATH=. $(PY) -m pytest tests/e2e/ -v \
		--base-url="http://localhost:$(PORT)" \
		--browser chromium
	$(MAKE) e2e-down

.PHONY: e2e-cross-browser
e2e-cross-browser: e2e-up ## Smoke tests on chromium, firefox, webkit
	PYTHONPATH=. $(PY) -m pytest tests/e2e/test_smoke.py -v \
		--base-url="http://localhost:$(PORT)" \
		--browser chromium --browser firefox --browser webkit
	$(MAKE) e2e-down

.PHONY: e2e-debug
e2e-debug: e2e-up ## Headed + slowmo for debugging
	PYTHONPATH=. $(PY) -m pytest tests/e2e/test_smoke.py -v \
		--base-url="http://localhost:$(PORT)" \
		--browser chromium --headed --slowmo=1000 -s
	$(MAKE) e2e-down

# -----------------------------------------------------------------------------
# Chainguard PyPI switching
# Chainguard remediated is primary; PyPI stays as a fallback.
# -----------------------------------------------------------------------------
.PHONY: switch-cgr
switch-cgr: ## Use Chainguard PyPI as primary and reinstall deps
	@echo "Writing pip.conf (Chainguard as primary)..."
	@printf '%s\n' \
		'[global]' \
		'index-url = https://libraries.cgr.dev/python-remediated/simple' \
		'extra-index-url = https://libraries.cgr.dev/python/simple' \
		'                https://pypi.org/simple' \
		'' \
		'[install]' \
		'timeout = 30' \
	> pip.conf
	@test -d "$(VENV)" || { echo "Virtual environment not found. Run '\''make install'\'' first."; exit 1; }
	@echo "Reinstalling dependencies..."
	@$(PY) -m pip install --upgrade pip
	@$(PY) -m pip install --force-reinstall -r requirements.txt
	@if [ -f requirements-e2e.txt ]; then $(PY) -m pip install --force-reinstall -r requirements-e2e.txt; fi
	@echo "Done."

.PHONY: switch-pypi
switch-pypi: ## Use regular PyPI only
	echo "Writing pip.conf (regular PyPI only)..."
	printf '%s\n' \
		'[global]' \
		'index-url = https://pypi.org/simple' \
		'' \
		'[install]' \
		'timeout = 30' \
	> pip.conf

.PHONY: show-config
show-config: ## Show pip.conf and a few installed packages
	echo "=== pip.conf ==="
	if [ -f pip.conf ]; then cat pip.conf; else echo "No pip.conf found"; fi
	echo ""
	echo "=== pip config (from venv) ==="
	$(PY) -m pip config list || echo "No pip config set"
	echo ""
	echo "=== sample installed packages ==="
	$(PY) -m pip list --format=columns | sed -n '1,6p'

.PHONY: show-provenance
show-provenance: ## Show provenance for all packages in requirements.txt (stdout only)
	@while read line; do \
		if echo "$$line" | grep -q '=='; then \
			pkg=$$(echo "$$line" | cut -d'=' -f1 | tr '[:upper:]' '[:lower:]'); \
			version=$$(echo "$$line" | cut -d'=' -f3); \
			echo "Fetching provenance for $$pkg==$$version..."; \
			provenance_url=$$(curl -s --netrc https://libraries.cgr.dev/python-remediated/simple/$$pkg/ | grep "$$version" | grep "\.tar\.gz" | grep -o 'data-provenance="[^"]*"' | cut -d'"' -f2 | head -1); \
			if [ -n "$$provenance_url" ]; then \
				curl -s --netrc "$$provenance_url" | jq -r '.attestation_bundles[0].attestations[0].envelope.statement' | base64 -d | jq .; \
			else \
				echo "No provenance found for $$pkg-$$version"; \
			fi; \
			echo ""; \
		fi; \
	done < requirements.txt

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------
.PHONY: clean
clean: ## Remove caches and build artifacts (keeps venv)
	rm -rf .pytest_cache/ __pycache__/ build/ dist/ *.egg-info/ \
		playwright-report/ test-results/

.PHONY: distclean
distclean: clean ## Remove venv and pip.conf as well
	rm -rf $(VENV) pip.conf
