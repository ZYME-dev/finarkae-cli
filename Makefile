.PHONY: test test-verbose clean install dev lint format help

# Default target
help:
	@echo "Available commands:"
	@echo "  test         - Run unit tests"
	@echo "  test-verbose - Run unit tests with verbose output"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  install      - Install the package in development mode"
	@echo "  dev          - Install development dependencies"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code"
	@echo "  clean        - Clean up build artifacts"
	@echo "  sample-test  - Test on sample data"

# Run unit tests
test:
	uv run pytest tests/ -v

# Run tests with verbose output and show print statements
test-verbose:
	uv run pytest tests/ -v -s

# Run tests with coverage
test-cov:
	uv run pytest tests/ --cov=finarkae --cov-report=html --cov-report=term

# Install package in development mode
install:
	uv sync

# Install development dependencies
dev:
	uv sync --dev

# Run linting
lint:
	uv run ruff check finarkae/ tests/
	uv run mypy finarkae/

# Format code
format:
	uv run ruff format finarkae/ tests/

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Test on sample data
sample-test:
	uv run finarkae proxity comp-remises-flux-pass --dir "tmp/sample/Remises PASS 04 2025" --verbose 