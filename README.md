# finarkae-cli

CLI tools for finarkae, installable from the repo through uvx.

## Installation

### Prerequisites

First, you need to install `uv` (the Python package manager). Choose your preferred method:

**Via Homebrew (macOS):**
```bash
brew install uv
```

**Via curl (Linux/macOS):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Via PowerShell (Windows):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For more installation options, visit: https://docs.astral.sh/uv/getting-started/installation/

### Install finarkae-cli

Once `uv` is installed, you can install `finarkae-cli` directly from this GitHub repository:

```bash
uvx install git+https://github.com/zyme-dev/finarkae-cli.git
```

This will make the `finarkae` command globally available in your terminal.

## Usage

The CLI is organized into submodules. Currently available:

### Proxity Module

#### compile-ops

Read all CSV and XLS/XLSX files from a directory and display them in a formatted table.

**Features:**
- Supports both CSV and Excel files (.csv, .xls, .xlsx)
- Intelligent CSV parsing with French encoding support
- Handles complex CSV structures with metadata headers
- Displays file information including row/column counts
- Verbose mode with encoding details

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

## Getting Help

```bash
# General help
finarkae --help

# Help for proxity module
finarkae proxity --help

# Help for specific command
finarkae proxity compile-ops --help

# Show version
finarkae --version
```

## Development

To contribute to this project:

1. Clone the repository
2. Install dependencies: `uv sync`
3. Run in development mode: `uv run finarkae`

### Testing

The project includes comprehensive unit tests:

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

### Available Make Commands

```bash
make help          # Show all available commands
make install       # Install in development mode
make dev           # Install development dependencies
make lint          # Run linting checks
make format        # Format code
make clean         # Clean build artifacts
```

## License

This project is licensed under the MIT License.
# Testing the new VERSION file approach
