#!/bin/bash -
set -eu -o pipefail
exec 2>&1
cd "$(dirname "$0")"
run="run-$(date '+%s')"
time python3 -u git-sqlite-bench.py "$@" | tee "$run.log"
! which Rscript || Rscript plot.R
cp work/millisec "$run.millisec"
for x in millisec*.png; do mv "$x" "$run.$x"; done
