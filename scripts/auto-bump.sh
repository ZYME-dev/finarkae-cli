#!/bin/bash

# Auto-bump script for pre-commit hook
# This script increments the patch version and stages the changed files

# Get the latest tag
git fetch --tags
latest_tag=$(git describe --tags --abbrev=0 | sed 's/^v//')
if [ -z "$latest_tag" ]; then
    latest_tag=0.0.0
fi

# Parse version numbers
IFS='.' read -r major minor patch <<< "$latest_tag"
patch=$((patch + 1))
new_version="$major.$minor.$patch"

# Update VERSION file
echo "$new_version" > VERSION
echo "Bumped patch to $new_version"

# Update pyproject.toml files
vver="v$new_version"
for file in $(find . -name pyproject.toml); do
    sed -i.bak -E "s/(^version *= *\")[^\"]+(\")$/\1$vver\2/" "$file"
    rm -f "$file.bak"
done
echo "Updated all pyproject.toml to version $vver"

# Stage the modified files so they are included in the commit
git add VERSION $(find . -name pyproject.toml)

exit 0 