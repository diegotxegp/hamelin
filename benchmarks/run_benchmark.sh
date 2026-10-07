#!/usr/bin/env bash
# Runs the Ludwig benchmark notebook unattended (without opening Jupyter).
#
#   ./run_benchmark.sh full        # the whole experiment (TEST_MODE = False)
#   ./run_benchmark.sh test        # smoke test (TEST_MODE = True), about 7 minutes
#   ./run_benchmark.sh             # whatever TEST_MODE the notebook has
#
# The mode given here overrides TEST_MODE for this launch only; the notebook is not edited.
# The other settings (test or full run, time limit, datasets, seeds, ...) are the ones in the
# "Parameters" cell of ludwig/ludwig_experiment.ipynb: edit them there. The notebook's last
# cell runs the analysis, so the results and tables are left ready.
#
# Safe to interrupt (Ctrl+C, reboot, crash) and to launch again: datasets with all their
# runs saved are skipped and half-done ones are discarded and restarted from their first
# seed. Run it inside tmux/screen or with nohup:
#
#   nohup ./run_benchmark.sh > /dev/null 2>&1 &
#
# The notebook is converted to a plain script and run directly, so progress is printed live
# and there is no per-cell timeout. Everything is also written to results/logs/ (launcher.log
# has the whole session; follow it with tail -f).
#
# Environment: PYTHON (default .venv-bench/bin/python), BENCH_PASSES (default 2: the second
# pass redoes the datasets that did not finish in the first).
set -u
cd "$(dirname "$0")"

MODE=""
case "${1:-}" in
    "") ;;
    full|test) MODE="$1" ;;
    *) echo "Usage: ./run_benchmark.sh [full|test]"; exit 2 ;;
esac

PYTHON="${PYTHON:-.venv-bench/bin/python}"
[ -x "$PYTHON" ] || PYTHON=python3
# Absolute path, so it still resolves after cd'ing into the notebook's folder
case "$PYTHON" in */*) PYTHON="$(cd "$(dirname "$PYTHON")" && pwd)/$(basename "$PYTHON")";; esac
PASSES="${BENCH_PASSES:-2}"
LOGDIR="results/logs"
mkdir -p "$LOGDIR/scripts"

# One launch at a time: two Ludwig jobs would fight over the hyperopt/ folder
exec 9>"$LOGDIR/.lock"
if command -v flock >/dev/null && ! flock -n 9; then
    echo "Another run_benchmark.sh is already running ($LOGDIR/.lock is held)."; exit 1
fi

# Keep a copy of everything this script prints
exec > >(tee -a "$LOGDIR/launcher.log") 2>&1
STAMP=$(date +%Y%m%d_%H%M%S)
echo "[$(date '+%F %T')] Start, python: $PYTHON, mode: ${MODE:-as in the notebook}"

# The notebook's code cells, as a plain script (no nbconvert needed)
SCRIPT="$PWD/$LOGDIR/scripts/ludwig_experiment_$STAMP.py"
"$PYTHON" - "$SCRIPT" "$MODE" <<'PY'
import json, re, sys
notebook = json.load(open("ludwig/ludwig_experiment.ipynb"))
code = "\n\n".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code")
if sys.argv[2]:  # full / test: overrides TEST_MODE in the generated script only
    code, n = re.subn(r"^TEST_MODE = (True|False)", f"TEST_MODE = {sys.argv[2] == 'test'}", code, flags=re.M)
    if n != 1:
        sys.exit("Could not find the TEST_MODE line in the notebook.")
open(sys.argv[1], "w").write(code)
PY
[ -f "$SCRIPT" ] || { echo "Could not extract the notebook's code."; exit 1; }

FAILED=1
for pass in $(seq 1 "$PASSES"); do
    echo "[$(date '+%F %T')] Pass $pass of $PASSES"
    # cwd = the notebook's folder, as the notebook expects
    (cd ludwig && "$PYTHON" -u "$SCRIPT") 2>&1 | tee -a "$LOGDIR/ludwig_${STAMP}.log"
    if [ "${PIPESTATUS[0]}" -eq 0 ]; then FAILED=0; else FAILED=1; fi  # only the last pass counts: a retry may have fixed it
done

if [ "$FAILED" -ne 0 ]; then
    echo "[$(date '+%F %T')] Finished WITH ERRORS: check $LOGDIR/. Launch again to retry what is missing."
    exit 1
fi
echo "[$(date '+%F %T')] Done. The results are in results/<run mode>/ (see the notebook's Parameters cell)."
