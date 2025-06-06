#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path

VERSION_FILE = Path("VERSION")


# Check for staged changes (excluding version files)
def has_staged_changes():
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    files = [f for f in result.stdout.splitlines() if f not in ("VERSION", "pyproject.toml")]
    return bool(files)


def get_version_from_file():
    if not VERSION_FILE.exists():
        print("No VERSION file found", file=sys.stderr)
        sys.exit(1)
    content = VERSION_FILE.read_text().strip()
    m = re.match(r'^(\d+)\.(\d+)\.(\d+)$', content)
    if not m:
        print("Invalid version format in VERSION file", file=sys.stderr)
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


def set_version_in_file(new_version):
    VERSION_FILE.write_text(f"{new_version}\n")


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
    
    version = get_version_from_file()
    new_version_tuple = bump_version(version, bump_type)
    new_version = f"{new_version_tuple[0]}.{new_version_tuple[1]}.{new_version_tuple[2]}"
    
    # Update VERSION file
    set_version_in_file(new_version)
    
    # Stage the changes if in pre-commit
    if "PRE_COMMIT" in os.environ or "PRE_COMMIT_HOME" in os.environ:
        subprocess.run(["git", "add", "VERSION"])
    
    print(f"[bump-version] Version bumped to {new_version}")


if __name__ == "__main__":
    main()
