#!/bin/bash
set -e

cases=(C1 C2 C3 C4 C5 C6 C7 C8 C9)

baseDir=$(pwd)

for case in "${cases[@]}"; do
    echo "======================================"
    echo "Running case: $case"
    echo "======================================"

    cd "$baseDir/$case"

    if [ ! -f run_all.sh ]; then
        echo "ERROR: run_all.sh not found in $case"
        exit 1
    fi

    sh run_all.sh 2>&1 | tee log.masterRun

    cd "$baseDir"

    echo "Finished case: $case"
    echo
done

echo "All cases finished."
