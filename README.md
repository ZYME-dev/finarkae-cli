# finarkae-cli

CLI tools for finarkae - A collection of tools for financial data processing. Made by ZYME with great 💚.

---

## 👤 For Users

### Prerequisites

You need to install `uv` (the Python package manager) first. Choose your preferred method:

**macOS (via Homebrew):**

First, install Homebrew if you don't have it:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install uv:
```bash
brew install uv
```

**Windows (via PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS (via curl):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> For more installation options, visit: https://docs.astral.sh/uv/getting-started/installation/

### Install finarkae-cli

Once `uv` is installed, install `finarkae-cli` directly from GitHub:

```bash
uv tool install git+https://github.com/zyme-dev/finarkae-cli.git
```

This will make the `finarkae` command globally available in your terminal.

### Usage

The CLI is organized into modules. Currently available:

#### Getting Help

```bash
# General help
finarkae --help

# Help for proxity module
finarkae proxity --help

# Show version
finarkae --version
```

#### Proxity Module

##### compile-ops

Read all CSV and XLS/XLSX files from a directory and display them in a formatted table.

**Features:**
* Supports both CSV and Excel files (.csv, .xls, .xlsx)
* Intelligent CSV parsing with French encoding support
* Handles complex CSV structures with metadata headers
* Displays file information including row/column counts
* Verbose mode with encoding details

**Usage:**
```bash
# Scan current directory
finarkae proxity compile-ops

# Scan specific directory
finarkae proxity compile-ops --dir /path/to/directory
finarkae proxity compile-ops -d /path/to/directory

# Verbose mode with detailed information
finarkae proxity compile-ops --verbose
finarkae proxity compile-ops -v --dir /path/to/directory
```

**Example output:**
```
                      Operations Files in /current/directory
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━┳━━━━━━┳━━━━━━━━━┓
┃ File Name                                 ┃ Type ┃ Size    ┃ Rows ┃ Columns ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━╇━━━━━━╇━━━━━━━━━┩
│ LISTE_OPERATIONS_ABC123_20250506.csv     │ .csv │ 1.2 KB  │ 5    │ 6       │
│ data.xlsx                                 │ .xlsx│ 1.25 MB │ 150  │ 8       │
│ report.xls                                │ .xls │ 0.85 MB │ 200  │ 5       │
└───────────────────────────────────────────┴──────┴─────────┴──────┴─────────┘

Summary:
  • CSV files: 1
  • Excel files: 2
  • Total files: 3
  • Total rows: 355
```

### Updating

To update to the latest version:

```bash
uv tool install git+https://github.com/zyme-dev/finarkae-cli.git --force
```

### Uninstalling

#### Remove finarkae-cli

To remove just the finarkae-cli tool:

```bash
uv tool uninstall finarkae_cli
```

#### Complete Removal (Optional)

If you no longer need `uv` and want to remove it completely:

**macOS (if installed via Homebrew):**
```bash
brew uninstall uv
```

**Linux/macOS (if installed via curl):**
```bash
# Remove uv binary
rm -rf ~/.cargo/bin/uv
# Remove uv cache and data
rm -rf ~/.cache/uv
rm -rf ~/.local/share/uv
```

**Windows (if installed via PowerShell):**
```powershell
# Remove uv from your PATH and delete the installation directory
# Location is typically in your user profile under .cargo\bin\
```

> **Note**: Only remove `uv` if you're not using it for other Python projects. If you're unsure, just uninstall finarkae-cli and keep `uv` installed.

---

## 🛠️ For Developers

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zyme-dev/finarkae-cli.git
   cd finarkae-cli
   ```

2. **Install development dependencies:**
   ```bash
   make install
   ```
   This will:
   - Install all dependencies with `uv sync`
   - Set up pre-commit hooks
   - Prepare the development environment

3. **Install in development mode:**
   ```bash
   uv tool install --editable .
   ```

### Development Workflow

#### Testing

```bash
# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run tests with coverage report
make test-cov

# Test on sample data
make sample-test
```

#### Code Quality

```bash
# Format code
make format

# Run linting checks
make lint
```

#### Version Management

```bash
# Bump patch version (e.g., 0.1.0 → 0.1.1)
make bump-patch

# Bump minor version (e.g., 0.1.0 → 0.2.0)
make bump-minor

# Bump major version (e.g., 0.1.0 → 1.0.0)
make bump-major
```

#### Available Make Commands

```bash
make help          # Show all available commands
make install       # Install in development mode
make dev           # Install development dependencies
make lint          # Run linting checks
make format        # Format code
make clean         # Clean build artifacts
make test          # Run unit tests
make test-verbose  # Run tests with verbose output
make test-cov      # Run tests with coverage report
make sample-test   # Test on sample data
```

### Project Structure

```
finarkae-cli/
├── finarkae/           # Main package
│   ├── __init__.py
│   ├── main.py         # CLI entry point
│   ├── _version.py     # Version management
│   └── proxity/        # Proxity module
├── tests/              # Unit tests
├── pyproject.toml      # Project configuration
├── Makefile           # Development commands
├── VERSION            # Version number
└── README.md          # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `make test`
5. Commit your changes: `git commit -m "Description"`
6. Push to your fork: `git push origin feature-name`
7. Create a Pull Request

### Development Requirements

- Python ≥ 3.12
- `uv` package manager
- Make (for development commands)

## License

This project is licensed under the MIT License.
