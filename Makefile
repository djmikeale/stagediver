.PHONY: install test lint format clean help

# Python interpreter settings
PYTHON = python3
VENV = venv
BIN = $(VENV)/bin

# Default target
.DEFAULT_GOAL := help

help:  ## Show this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: $(VENV)/bin/pip  ## Install package and dependencies
	$(PYTHON) -m venv $(VENV)
	source $(BIN)/activate
	$(BIN)/pip install -e ".[dev]"

lint: install  ## Run all linters and type checks
	$(BIN)/black --check .
	$(BIN)/isort --check .
	$(BIN)/mypy stagediver/

verify: install lint test  ## Run all checks (lint + test)
	@echo "All checks passed! 🎉"

clean:  ## Remove build/test artifacts
	rm -rf $(VENV)
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf __pycache__
	rm -rf .coverage
	rm -rf dist/
	find . -type d -name __pycache__ -exec rm -rf {} +

build:  ## Build package distribution
	$(BIN)/pip install build
	$(BIN)/python -m build
