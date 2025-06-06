.PHONY: test test-verbose clean install dev lint format help bump bump-minor bump-major sync-version

# Install package in development mode and pre-commit hooks
install:
	uv sync
	pre-commit install
	@echo "All dependencies and pre-commit hooks installed. Ready to develop!"

# Install development dependencies
dev:
	uv sync --dev

# Lint code using ruff and mypy
lint:
	uv run ruff check finarkae/ tests/ --fix

# Format code using ruff
format:
	uv run ruff format finarkae/ tests/


VERSION_FILE=VERSION
PYPROJECTS=$(shell find . -name pyproject.toml)

.PHONY: bump-patch bump-minor bump-major update-version

## Count commits since latest tag and update VERSION
bump-patch:
	@git fetch --tags
	@latest_tag=$$(git describe --tags --abbrev=0); \
	patch_count=$$(git rev-list $$latest_tag..HEAD --count); \
	new_version=$${latest_tag}.$$patch_count; \
	echo $$new_version > $(VERSION_FILE); \
	echo "Bumped patch to $$new_version"; \
	make update-version

## Bump minor version tag (e.g. from 0.2 to 0.3)
bump-minor:
	@latest_tag=$$(git describe --tags --abbrev=0); \
	new_minor=$$(echo $$latest_tag | awk -F. '{$$2 += 1; $$3=0; print $$1"."$$2}' ); \
	git tag $$new_minor; \
	echo "$$new_minor.0" > $(VERSION_FILE); \
	echo "Created minor tag $$new_minor"; \
	make update-version

## Same for major
bump-major:
	@latest_tag=$$(git describe --tags --abbrev=0); \
	new_major=$$(echo $$latest_tag | awk -F. '{$$1 += 1; $$2=0; $$3=0; print $$1"."$$2}' ); \
	git tag $$new_major; \
	echo "$$new_major.0" > $(VERSION_FILE); \
	echo "Created major tag $$new_major"; \
	make update-version

## Write version into all pyproject.toml
update-version:
	@ver=$$(cat $(VERSION_FILE)); \
	for file in $(PYPROJECTS); do \
		sed -i.bak -E "s/(^version *= *\")[0-9]+\.[0-9]+\.[0-9]+(\")/\1$$ver\2/" $$file; \
		rm -f $$file.bak; \
	done; \
	echo "Updated all pyproject.toml to version $$ver"


# Run unit tests
test:
	uv run pytest tests/ -v

# Run tests with verbose output and show print statements
test-verbose:
	uv run pytest tests/ -v -s

# Run tests with coverage
test-cov:
	uv run pytest tests/ --cov=finarkae --cov-report=html --cov-report=term

# Test on sample data
sample-test:
	uv run finarkae proxity comp-remises-flux-pass --dir "tmp/sample/Remises PASS 04 2025" --verbose



# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete


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
	@echo "  bump         - Bump version"
	@echo "  bump-minor   - Bump minor version"
	@echo "  bump-major   - Bump major version"
	@echo "  sync-version - Sync version from VERSION file to other files

