.PHONY: install test install-simple clean install-dev lint

# Python interpreter settings
VENV = venv
BIN = $(VENV)/bin
PRECOMMIT_INSTALL = pre-commit install

# Default target
.DEFAULT_GOAL := help

help:  ## Show this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package and dependencies using uv
	uv venv
	uv pip install -e .
	$(PRECOMMIT_INSTALL)

install-simple:  ## Install package and dependencies
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e .
	$(PRECOMMIT_INSTALL)

clean:  ## Remove build/test artifacts
	rm -rf $(VENV)
	git clean -fdX

test:  ## Run tests
	uv run pytest
