#!/usr/bin/env bash
# Runs the benchmark unattended and then the analysis.
#
#   ./run_benchmark.sh              # Ludwig + scikit-learn + analysis (full experiment)
#   ./run_benchmark.sh ludwig       # only Ludwig (or: sklearn)
#   BENCH_TEST_MODE=1 ./run_benchmark.sh    # smoke test instead of the full experiment
#
# Safe to interrupt (Ctrl+C, reboot, crash) and to launch again: runs already
# saved in the CSVs are skipped. Run it inside tmux/screen or with nohup:
#
#   mkdir -p logs && nohup ./run_benchmark.sh > logs/launcher.log 2>&1 &
#
# Each notebook is converted to a plain script and run directly, so progress is
# printed live and there is no per-cell timeout. Logs go to logs/.
#
# Environment: PYTHON (default .venv-bench/bin/python), BENCH_PASSES (default 2:
# the second pass retries runs that failed in the first), BENCH_TEST_MODE
# (default 0), plus the BENCH_* variables listed in README.md.
set -u
cd "$(dirname "$0")"

WHAT="${1:-all}"
case "$WHAT" in ludwig|sklearn|all) ;; *) echo "Usage: $0 [ludwig|sklearn|all]"; exit 2;; esac

PYTHON="${PYTHON:-.venv-bench/bin/python}"
[ -x "$PYTHON" ] || PYTHON=python3
export BENCH_TEST_MODE="${BENCH_TEST_MODE:-0}"
PASSES="${BENCH_PASSES:-2}"
mkdir -p logs/scripts

# One launch at a time: two Ludwig jobs would fight over the hyperopt/ folder
exec 9>logs/.lock
if command -v flock >/dev/null && ! flock -n 9; then
    echo "Another run_benchmark.sh is already running (logs/.lock is held)."; exit 1
fi

MODE=$("$PYTHON" -c "import common_utils as c; print(c.RUN_MODE_NAME)") || { echo "Cannot import common_utils with $PYTHON"; exit 1; }
STAMP=$(date +%Y%m%d_%H%M%S)
FAILED=0
echo "[$(date '+%F %T')] Start: $WHAT, run mode '$MODE', python: $PYTHON"

run_tool() {
    local tool="$1"
    local script="$PWD/logs/scripts/${tool}_experiment.py" last_ok=0
    rm -f "$script"
    "$PYTHON" -m jupyter nbconvert --to python "$tool/${tool}_experiment.ipynb" \
        --output-dir logs/scripts --output "${tool}_experiment" >/dev/null 2>&1
    [ -f "$script" ] || { echo "Could not convert the $tool notebook (is jupyter installed in $PYTHON?)"; FAILED=1; return 1; }
    for pass in $(seq 1 "$PASSES"); do
        echo "[$(date '+%F %T')] $tool, pass $pass of $PASSES"
        # cwd = the notebook's folder, as the notebooks expect
        (cd "$tool" && "$PYTHON" -u "$script") 2>&1 | tee -a "logs/${tool}_${STAMP}.log"
        if [ "${PIPESTATUS[0]}" -ne 0 ]; then
            echo "[$(date '+%F %T')] $tool pass $pass ended with an error (see logs/${tool}_${STAMP}.log)"
            last_ok=0
        else
            last_ok=1
        fi
    done
    [ "$last_ok" -eq 1 ] || FAILED=1  # only the last pass counts: a retry may have fixed it
}

[ "$WHAT" = "all" ] || [ "$WHAT" = "ludwig" ] && run_tool ludwig
[ "$WHAT" = "all" ] || [ "$WHAT" = "sklearn" ] && run_tool sklearn

echo "[$(date '+%F %T')] Analysis"
"$PYTHON" analyze_results.py "$MODE" 2>&1 | tee -a "logs/analysis_${STAMP}.log"
"$PYTHON" analyze_results.py --datasets 2>&1 | tee -a "logs/analysis_${STAMP}.log"
if [ "$FAILED" -ne 0 ]; then
    echo "[$(date '+%F %T')] Finished WITH ERRORS: check the logs in logs/. Launch again to retry what is missing."
    exit 1
fi
echo "[$(date '+%F %T')] Done. Results: ludwig/results/$MODE, sklearn/results/$MODE, analysis_$MODE/, datasets_summary.csv"
