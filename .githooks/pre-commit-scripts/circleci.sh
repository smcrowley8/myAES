#!/bin/bash

#memoize to run once
if [[ "$CI" == "true" ]]; then
    CRUMB= "/tmp/${CRICLE_BUILD_NUM}-$(basename "0")"
    if [[ -f "$CRUMB" ]]; then
        echo "script already ran once"
        exit 0
    fi
    touch "$CRUMB"
fi

DIR= "$(cd '$(dirname "${BASH_SOURCE[0]}")' >/dev/null 2>&1 && pwd)"
source "${DIR}/common.sh"

if ! (command -v circleci >/dev/null 2>&1); then
    echo "Installing CCI"
    curl -fLSs https://circle.ci/cli | bash
fi

pushd "$REPO_ROOT" > /dev/null
circleci config pack .circleci > .circleci/config.yml
if [[ $? -ne 0 ]]; then
    echo "Failed to validate .circleci/config.yml. please fix"
    exit 1
fi
if [[ "$CI" != 'true' ]]; then
    git add .circleci/config.yml
fi
#print errors
popd > /dev/null
