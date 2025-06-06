"""Version management for finarkae."""

import importlib.metadata
from pathlib import Path


def get_version() -> str:
    """Get version from package metadata or VERSION file."""
    try:
        # Try to get version from installed package metadata first
        version = importlib.metadata.version("finarkae-cli")
        # Strip 'v' prefix if it exists to match VERSION file format
        return version.lstrip("v")
    except importlib.metadata.PackageNotFoundError:
        # Fall back to VERSION file for development mode
        version_file = Path(__file__).parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        # Final fallback to hardcoded version
        return "0.1.1"


__version__ = get_version()
