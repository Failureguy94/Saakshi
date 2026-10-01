.PHONY: help up down test lint format build-frontend clean

UV ?= $(shell which uv 2>/dev/null || echo ~/.local/bin/uv)

help:
	@echo "Saakshi Forensics Monorepo"
	@echo ""
	@echo "Usage:"
	@echo "  make up              Start backend, database, redis, and frontend in Docker"
	@echo "  make down            Stop all running services"
	@echo "  make test            Run all backend unit and integration tests"
	@echo "  make lint            Run ruff and mypy static analysis"
	@echo "  make format          Run ruff formatters"
	@echo "  make build-frontend  Build the production React + Vite frontend bundle"
	@echo "  make clean           Remove caches and test artifacts"

up:
	docker compose up --build -d

down:
	docker compose down

test:
	cd backend && $(UV) run pytest -v tests/

lint:
	cd backend && $(UV) run ruff check app tests
	cd backend && $(UV) run mypy app

format:
	cd backend && $(UV) run ruff format app tests

build-frontend:
	cd frontend && npm install && npm run build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf backend/.venv frontend/dist
