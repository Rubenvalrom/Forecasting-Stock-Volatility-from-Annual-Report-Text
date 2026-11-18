.PHONY: setup test all

setup:
	pip install -e ".[dev]"

test:
	pytest -q

data:
	python -m volatility_from_text.steps.build_universe --config $(CONFIG)

all:
	@echo "Pipeline not built yet"