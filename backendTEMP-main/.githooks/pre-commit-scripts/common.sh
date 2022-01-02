#!/bin/bash

export REPO_ROOT = "$(git rev-parse --show-toplevel)"

function checkAWSCLI(){
    if [[ ! $(which aws) ]]; then
        echo "Instal AWS CLI V2 following these instructions"
        echo "https://docs.aws.amazon.com/cli/latest/userguide/"
    fi
}
