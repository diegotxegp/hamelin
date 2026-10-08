#!/usr/bin/env bash
# Runs a benchmark notebook unattended. Results and logs go to <tool>/results/.
#
#   ./run_benchmark.sh [ludwig|insuml] [full|test]
#
# full/test override TEST_MODE for this launch; everything else is set in the notebook's
# Parameters cell. Safe to interrupt and relaunch (finished datasets are skipped).
# Environment: PYTHON (default .venv-bench/bin/python), BENCH_PASSES (default 2).
set -u
cd "$(dirname "$0")"

TOOL="ludwig"
MODE=""
for arg in "$@"; do
    case "$arg" in
        ludwig) TOOL="ludwig" ;;
        insuml|InsuML) TOOL="InsuML" ;;
        full|test) MODE="$arg" ;;
        *) echo "Usage: ./run_benchmark.sh [ludwig|insuml] [full|test]"; exit 2 ;;
    esac
done
NOTEBOOK="$TOOL/${TOOL}_experiment.ipynb"

PYTHON="${PYTHON:-.venv-bench/bin/python}"
[ -x "$PYTHON" ] || PYTHON=python3
# Absolute path, so it still resolves after cd'ing into the notebook's folder
case "$PYTHON" in */*) PYTHON="$(cd "$(dirname "$PYTHON")" && pwd)/$(basename "$PYTHON")";; esac
PASSES="${BENCH_PASSES:-2}"
LOGDIR="$TOOL/results/logs"
mkdir -p "$LOGDIR/scripts"

# One launch at a time: two Ludwig jobs would fight over the hyperopt/ folder
exec 9>".run_benchmark.lock"
if command -v flock >/dev/null && ! flock -n 9; then
    echo "Another run_benchmark.sh is already running (.run_benchmark.lock is held)."; exit 1
fi

# Keep a copy of everything this script prints
exec > >(tee -a "$LOGDIR/launcher.log") 2>&1
STAMP=$(date +%Y%m%d_%H%M%S)
echo "[$(date '+%F %T')] Start, tool: $TOOL, python: $PYTHON, mode: ${MODE:-as in the notebook}"

# The notebook's code cells, as a plain script (no nbconvert needed)
SCRIPT="$PWD/$LOGDIR/scripts/${TOOL}_experiment.py"
"$PYTHON" - "$SCRIPT" "$MODE" "$NOTEBOOK" <<'PY'
import json, re, sys
notebook = json.load(open(sys.argv[3]))
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
    (cd "$TOOL" && "$PYTHON" -u "$SCRIPT") 2>&1 | tee -a "$LOGDIR/${TOOL}_${STAMP}.log"
    if [ "${PIPESTATUS[0]}" -eq 0 ]; then FAILED=0; else FAILED=1; fi  # only the last pass counts: a retry may have fixed it
done

if [ "$FAILED" -ne 0 ]; then
    echo "[$(date '+%F %T')] Finished WITH ERRORS: check $LOGDIR/. Launch again to retry what is missing."
    exit 1
fi
echo "[$(date '+%F %T')] Done. The results are in $TOOL/results/<run mode>/ (see the notebook's Parameters cell)."
