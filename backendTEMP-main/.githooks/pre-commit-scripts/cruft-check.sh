#!/bin/bash

cruft check
if [[ $? -ne 0 ]]; then
    echo "This project's cruft is out of date"
    echo "run 'cruft update' to update"
fi
