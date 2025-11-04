.PHONY: help install test lint run clean format all isort black flake8 pyright format-check lint-all

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[0;36m
RESET := \033[0m

help: ## Show this help message
	@echo "$(CYAN)Available targets:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}'

install: ## Install all dependencies using uv
	@echo "$(CYAN)Installing dependencies with uv...$(RESET)"
	@command -v uv >/dev/null 2>&1 || { echo "Error: uv is not installed. Install it from https://docs.astral.sh/uv/"; exit 1; }
	@uv sync --all-extras
	@echo "$(CYAN)✓ Dependencies installed$(RESET)"

test: ## Run the test suite with pytest and coverage
	@echo "$(CYAN)Running tests with coverage...$(RESET)"
	@uv run pytest
	@echo "$(CYAN)✓ Tests completed$(RESET)"

pyright: ## Run type checking with basedpyright
	@echo "$(CYAN)Running type checker...$(RESET)"
	@uv run basedpyright src/
	@echo "$(CYAN)✓ Type checking completed$(RESET)"

flake8: ## Run flake8 linter
	@echo "$(CYAN)Running flake8...$(RESET)"
	@uv run flake8 src/ tests/
	@echo "$(CYAN)✓ Flake8 completed$(RESET)"

isort: ## Sort imports with isort
	@echo "$(CYAN)Sorting imports...$(RESET)"
	@uv run isort src/ tests/
	@echo "$(CYAN)✓ Import sorting completed$(RESET)"

black: ## Format code with black
	@echo "$(CYAN)Formatting code with black...$(RESET)"
	@uv run black src/ tests/
	@echo "$(CYAN)✓ Code formatting completed$(RESET)"

format: isort black ## Format code with isort and black
	@echo "$(CYAN)✓ All formatting completed$(RESET)"

format-check: ## Check code formatting without modifying files
	@echo "$(CYAN)Checking import sorting...$(RESET)"
	@uv run isort --check-only src/ tests/
	@echo "$(CYAN)Checking code formatting...$(RESET)"
	@uv run black --check --diff src/ tests/
	@echo "$(CYAN)✓ Format check completed$(RESET)"

lint: pyright flake8 ## Run all linting checks (pyright + flake8)
	@echo "$(CYAN)✓ All linting completed$(RESET)"

lint-all: format-check lint ## Run format check and all linting
	@echo "$(CYAN)✓ All quality checks completed$(RESET)"

all: format lint-all test ## Run all checks (formatting, linting, and tests)
	@echo "$(CYAN)✓ All checks passed$(RESET)"

run: ## Run the Telegram bot
	@echo "$(CYAN)Starting Telegram bot...$(RESET)"
	@test -f .env || { echo "Error: .env file not found. Copy .env.example and configure it."; exit 1; }
	@uv run -m apisbot

clean: ## Remove build artifacts, caches, and temporary files
	@echo "$(CYAN)Cleaning build artifacts...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pyright" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@rm -rf dist/ build/ 2>/dev/null || true
	@echo "$(CYAN)✓ Cleanup completed$(RESET)"
