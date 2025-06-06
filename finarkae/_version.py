"""Version management for finarkae."""

from pathlib import Path


def get_version() -> str:
    """Get version from VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    # Fallback to hardcoded version if VERSION file doesn't exist
    raise RuntimeError("VERSION file not found")


__version__ = get_version()
