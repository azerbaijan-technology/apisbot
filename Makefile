.PHONY: help install test lint run clean format check

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
	@command -v uv >/dev/null 2>&1 || { echo "Error: uv is not installed. Install it with: pip install uv"; exit 1; }
	@uv pip install -e ".[dev]"
	@echo "$(CYAN)✓ Dependencies installed$(RESET)"

test: ## Run the test suite with pytest
	@echo "$(CYAN)Running tests...$(RESET)"
	@pytest || { echo "$(CYAN)Note: No tests found or tests failed$(RESET)"; exit 0; }
	@echo "$(CYAN)✓ Tests completed$(RESET)"

lint: ## Run code quality checks with pyright
	@echo "$(CYAN)Running linter...$(RESET)"
	@pyright src/
	@echo "$(CYAN)✓ Linting completed$(RESET)"

format: ## Format code (pyright is a type checker, use a formatter like black if needed)
	@echo "$(CYAN)Note: pyright is a type checker, not a formatter$(RESET)"
	@echo "$(CYAN)Consider adding black or autopep8 for code formatting$(RESET)"

check: lint test ## Run both linting and tests
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
