#!/usr/bin/env bash
# Runs the benchmark unattended and then the analysis.
#
#   ./run_benchmark.sh              # Ludwig + scikit-learn + analysis (full experiment)
#   ./run_benchmark.sh ludwig       # only Ludwig (or: sklearn)
#   BENCH_TEST_MODE=1 ./run_benchmark.sh    # smoke test instead of the full experiment
#
# Safe to interrupt (Ctrl+C, reboot, crash) and to launch again: runs already
# datasets with all their runs saved are skipped and half-done ones are discarded
# and restarted from fold 0. Run it inside tmux/screen or with nohup:
#
#   nohup ./run_benchmark.sh > /dev/null 2>&1 &
#
# Each notebook is converted to a plain script and run directly, so progress is
# printed live and there is no per-cell timeout. Everything is also written to
# results/<run mode>/logs/ (launcher.log has the whole session; follow it with
# tail -f).
#
# Environment: PYTHON (default .venv-bench/bin/python), BENCH_PASSES (default 2:
# the second pass redoes datasets that did not finish in the first), BENCH_TEST_MODE
# (default 0), plus the BENCH_* variables listed in README.md.
set -u
cd "$(dirname "$0")"

WHAT="${1:-all}"
case "$WHAT" in ludwig|sklearn|all) ;; *) echo "Usage: $0 [ludwig|sklearn|all]"; exit 2;; esac

PYTHON="${PYTHON:-.venv-bench/bin/python}"
[ -x "$PYTHON" ] || PYTHON=python3
export BENCH_TEST_MODE="${BENCH_TEST_MODE:-0}"
PASSES="${BENCH_PASSES:-2}"
MODE=$("$PYTHON" -c "import common_utils as c; print(c.RUN_MODE_NAME)") || { echo "Cannot import common_utils with $PYTHON"; exit 1; }
LOGDIR="results/$MODE/logs"
mkdir -p "$LOGDIR/scripts"

# One launch at a time: two Ludwig jobs would fight over the hyperopt/ folder
exec 9>"$LOGDIR/.lock"
if command -v flock >/dev/null && ! flock -n 9; then
    echo "Another run_benchmark.sh is already running (results/$MODE/logs/.lock is held)."; exit 1
fi

# Keep a copy of everything this script prints
exec > >(tee -a "$LOGDIR/launcher.log") 2>&1
STAMP=$(date +%Y%m%d_%H%M%S)
FAILED=0
echo "[$(date '+%F %T')] Start: $WHAT, run mode '$MODE', python: $PYTHON"

run_tool() {
    local tool="$1"
    local script="$PWD/$LOGDIR/scripts/${tool}_experiment.py" last_ok=0
    rm -f "$script"
    "$PYTHON" -m jupyter nbconvert --to python "$tool/${tool}_experiment.ipynb" \
        --output-dir "$LOGDIR/scripts" --output "${tool}_experiment" >/dev/null 2>&1
    [ -f "$script" ] || { echo "Could not convert the $tool notebook (is jupyter installed in $PYTHON?)"; FAILED=1; return 1; }
    for pass in $(seq 1 "$PASSES"); do
        echo "[$(date '+%F %T')] $tool, pass $pass of $PASSES"
        # cwd = the notebook's folder, as the notebooks expect
        (cd "$tool" && "$PYTHON" -u "$script") 2>&1 | tee -a "$LOGDIR/${tool}_${STAMP}.log"
        if [ "${PIPESTATUS[0]}" -ne 0 ]; then
            echo "[$(date '+%F %T')] $tool pass $pass ended with an error (see $LOGDIR/${tool}_${STAMP}.log)"
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
TOOL=ludwig; [ "$WHAT" = "sklearn" ] && TOOL=sklearn
"$PYTHON" analyze_results.py "$MODE" --tool "$TOOL"
"$PYTHON" analyze_results.py --datasets
if [ "$FAILED" -ne 0 ]; then
    echo "[$(date '+%F %T')] Finished WITH ERRORS: check the logs in $LOGDIR/. Launch again to retry what is missing."
    exit 1
fi
echo "[$(date '+%F %T')] Done. Everything is in results/$MODE/ (ludwig, sklearn, analysis, logs) and results/datasets_summary.csv"
