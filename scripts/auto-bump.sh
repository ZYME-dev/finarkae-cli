#!/bin/bash

# Auto-bump script for pre-commit hook
# This script sets the patch version based on commits since the last tag

# Get the latest tag
git fetch --tags
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//')
if [ -z "$latest_tag" ]; then
    latest_tag=0.0.0
fi

# Parse version numbers
IFS='.' read -r major minor patch <<< "$latest_tag"

# Count commits since the last tag to determine the new patch version
commits_since_tag=$(git rev-list --count v$latest_tag..HEAD 2>/dev/null || echo "0")
new_patch=$((patch + commits_since_tag))

new_version="$major.$minor.$new_patch"

# Update VERSION file
echo "$new_version" > VERSION
echo "Bumped patch to $new_version (based on $commits_since_tag commits since v$latest_tag)"

# Update pyproject.toml files
vver="v$new_version"
find . -name pyproject.toml -not -path "./.venv/*" | while read -r file; do
    if [ -f "$file" ]; then
        sed -i.bak -E "s/(^version *= *\")[^\"]+(\")$/\1$vver\2/" "$file"
        rm -f "$file.bak"
    fi
done
echo "Updated all pyproject.toml to version $vver"

# Stage the modified files so they are included in the commit
git add VERSION
find . -name pyproject.toml -not -path "./.venv/*" | xargs git add

exit 0 