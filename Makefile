CONFIG ?= configs/pilot.yaml

.PHONY: setup test data all

setup:
	pip install -e ".[dev]"

test:
	pytest -q

data:
	python -m volatility_from_text.steps.build_universe --config $(CONFIG)
	python -m volatility_from_text.steps.align_filings --config $(CONFIG)

all:
	@echo "Pipeline not built yet"