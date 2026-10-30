.PHONY: setup test all

setup:
	pip install -e ".[dev]"

test:
	pytest -q

all:
	@echo "Pipeline todavía vacío: los pasos se añaden según existan los módulos"