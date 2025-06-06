#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path

PYPROJECT = Path("pyproject.toml")
INIT = Path("finarkae/__init__.py")


# Check for staged changes (excluding version files)
def has_staged_changes():
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    files = [f for f in result.stdout.splitlines() if f not in ("pyproject.toml", "finarkae/__init__.py")]
    return bool(files)


def get_version_from_pyproject():
    content = PYPROJECT.read_text()
    m = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if not m:
        print("No version found in pyproject.toml", file=sys.stderr)
        sys.exit(1)
    return tuple(map(int, m.groups()))


def bump_version(version, bump_type):
    major, minor, patch = version
    if bump_type == "major":
        return (major + 1, 0, 0)
    elif bump_type == "minor":
        return (major, minor + 1, 0)
    else:
        return (major, minor, patch + 1)


def set_version_in_pyproject(new_version):
    content = PYPROJECT.read_text()
    new_content = re.sub(
        r'(version = ")[0-9]+\.[0-9]+\.[0-9]+("\n)', lambda m: f"{m.group(1)}{new_version}{m.group(2)}", content
    )
    PYPROJECT.write_text(new_content)


def set_version_in_init(new_version):
    content = INIT.read_text()
    new_content = re.sub(
        r'(__version__ = ")[0-9]+\.[0-9]+\.[0-9]+("\n)', lambda m: f"{m.group(1)}{new_version}{m.group(2)}", content
    )
    INIT.write_text(new_content)


def main():
    bump_type = "patch"
    if len(sys.argv) > 1:
        bump_type = sys.argv[1].lower()
        if bump_type not in ("patch", "minor", "major"):
            print("Usage: bump_version.py [patch|minor|major]", file=sys.stderr)
            sys.exit(1)
    # For pre-commit, only bump if there are staged changes
    if "PRE_COMMIT" in os.environ or "PRE_COMMIT_HOME" in os.environ:
        if not has_staged_changes():
            sys.exit(0)
    version = get_version_from_pyproject()
    new_version_tuple = bump_version(version, bump_type)
    new_version = f"{new_version_tuple[0]}.{new_version_tuple[1]}.{new_version_tuple[2]}"
    set_version_in_pyproject(new_version)
    set_version_in_init(new_version)
    # Stage the changes if in pre-commit
    if "PRE_COMMIT" in os.environ or "PRE_COMMIT_HOME" in os.environ:
        subprocess.run(["git", "add", "pyproject.toml", "finarkae/__init__.py"])
    print(f"[bump-version] Version bumped to {new_version}")


if __name__ == "__main__":
    main()
