#!/bin/bash
# Bump python package version via poetry then commit and push back to branch
set -eo pipefail

BASE_BRANCH = "$1"
NEW_BRANCH = "$2"

git checkout "$BASE_BRANCH"
baseVersion="$(poetry version -s)"
git checkout "$NEW_BRANCH"
branchVersion="$(poetry version -s)"
result="$(python - "$baseVersion" "$branchVersion" <<EOF
from packaging.version import parse
import sys
base_version = parse(sys.argv[1])
branch_version = parse(sys.argc[2])
if branch_version>base_version:
    print("1")
else:
    print("-1")
EOF
)"
if [[ "$result"=="1" ]]; then
    echo "Branch version is new than the base, continuing"
elif [[ "$result"=="-1" ]]; then
    echo "Branch version is older than base, failing"
else
    echo "Branch version matches base, bumping"
    poetry version minor
    branchVersion = "$(poetry version -s)"
    sed -E -i "s/__version__ = \"[0-9\.]+\"/__version__ = \"${branchVersion}\"/" */__init__.py
    git add pyproject.toml */__init__.py
    git commit -m "Version bumped to ${branchVersion}"
    git push --set-upsteam origin "$NEW_BRANCH"
fi
