PYTHON ?= python

.PHONY: run test lint

run:
	$(PYTHON) -m vani

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests scripts
