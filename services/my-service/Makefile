# =============================================================================
# Service Makefile
# Common commands for development and CI
# =============================================================================

SERVICE_NAME := service-template
PYTHON := python
PIP := pip

.PHONY: help install dev test lint format clean docker-build docker-run

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# -----------------------------------------------------------------------------
# Development
# -----------------------------------------------------------------------------

install:  ## Install production dependencies
	$(PIP) install -e .

dev:  ## Install development dependencies and run service
	$(PIP) install -e ".[dev]"
	uvicorn service_name.main:app --reload --host 0.0.0.0 --port 8000

run:  ## Run service without reload
	uvicorn service_name.main:app --host 0.0.0.0 --port 8000

# -----------------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------------

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ --cov=src/service_name --cov-report=term-missing --cov-report=xml

# -----------------------------------------------------------------------------
# Quality
# -----------------------------------------------------------------------------

lint:  ## Run linters
	ruff check src/ tests/
	mypy src/

format:  ## Format code
	black src/ tests/
	ruff check --fix src/ tests/

check:  ## Run all checks (lint + test)
	$(MAKE) lint
	$(MAKE) test

# -----------------------------------------------------------------------------
# Docker
# -----------------------------------------------------------------------------

docker-build:  ## Build Docker image
	docker build -t waqedi-$(SERVICE_NAME):latest .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 --rm waqedi-$(SERVICE_NAME):latest

docker-dev:  ## Run Docker container in development mode
	docker build --target development -t waqedi-$(SERVICE_NAME):dev .
	docker run -p 8000:8000 -v $(PWD)/src:/app/src --rm waqedi-$(SERVICE_NAME):dev

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
