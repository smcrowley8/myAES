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


pushd "$REPO_ROOT" > /dev/null
if [[ "$CI" != 'true' ]]; then
    rm -r docs

    mkdir docs

    python -m pdoc --force --html --config show_source_code=False --output-dir docs katan_ai

    mv docs/katan_ai/* docs

    rmdir docs/katan_ai
fi

if [[ "$CI" != 'true' ]]; then
   git add docs/\*
fi
#print errors
popd > /dev/null
