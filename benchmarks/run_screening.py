"""Runs the whole variant screening unattended.

Executes sklearn_experiment.ipynb once and ludwig_experiment.ipynb once per
variant, one after another (each in its own process, so memory is released and
Ray is fully shut down between runs), then prints the comparison.

Usage (from benchmarks/, with the project's .venv):
    ../.venv/bin/python run_screening.py                  # 3 folds, 300 s, default+ple+concat
    ../.venv/bin/python run_screening.py --max-folds 10   # all folds of the task
    ../.venv/bin/python run_screening.py --test           # smoke test: fold 0 only
    ../.venv/bin/python run_screening.py --dry-run        # show the plan, run nothing

Settings reach the notebooks through BENCH_* environment variables read by
common_utils.py, so no file has to be edited. Executed copies of every
notebook (with their output) are kept in logs/<timestamp>/.
"""

import argparse
import datetime
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LUDWIG_NB = os.path.join(HERE, "ludwig", "ludwig_experiment.ipynb")
SKLEARN_NB = os.path.join(HERE, "sklearn", "sklearn_experiment.ipynb")
VARIANTS = ("default", "ple", "concat")
LUDWIG_OVERHEAD_S = 100  # observed: Ludwig runs ~100 s past its time limit


def _execute_notebook(nb_path, out_path):
    """Child-process entry point: runs one notebook and saves the executed copy."""
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(nb_path, as_version=4)
    client = NotebookClient(
        nb, timeout=None, kernel_name="python3",
        resources={"metadata": {"path": os.path.dirname(nb_path)}},
    )
    try:
        client.execute()
    finally:
        nbformat.write(nb, out_path)


def _fmt(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s:02d}s"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variants", default=",".join(VARIANTS), help="comma separated Ludwig variants")
    ap.add_argument("--max-folds", type=int, default=3, help="folds per task (default 3)")
    ap.add_argument("--time-limit", type=int, default=300, help="seconds per run (default 300)")
    ap.add_argument("--trials", type=int, default=2,
                    help="Ludwig trials running in parallel (default 2; 3 ran out of memory on 8 GB)")
    ap.add_argument("--test", action="store_true", help="smoke test: fold 0 only, 300 s")
    ap.add_argument("--skip-sklearn", action="store_true")
    ap.add_argument("--skip-ludwig", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--_execute", nargs=2, metavar=("NB", "OUT"), help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args._execute:
        _execute_notebook(*args._execute)
        return 0

    variants = [v for v in args.variants.split(",") if v]
    bad = [v for v in variants if v not in VARIANTS]
    if bad:
        ap.error(f"unknown variant(s): {bad}; valid: {VARIANTS}")

    env = dict(os.environ)
    if args.test:
        env.update(BENCH_TEST_MODE="1", BENCH_SINGLE_TASK_MODE="0")
        env.pop("BENCH_MAX_FOLDS", None)
        env.pop("BENCH_TIME_LIMIT_S", None)
    else:
        env.update(BENCH_TEST_MODE="0", BENCH_SINGLE_TASK_MODE="1",
                   BENCH_MAX_FOLDS=str(args.max_folds), BENCH_TIME_LIMIT_S=str(args.time_limit))
    env["BENCH_LUDWIG_TRIALS"] = str(args.trials)
    # Same settings in this process, to learn the task id and results folder name.
    os.environ.update({k: v for k, v in env.items() if k.startswith("BENCH_")})
    for k in ("BENCH_MAX_FOLDS", "BENCH_TIME_LIMIT_S"):
        if k not in env:
            os.environ.pop(k, None)
    sys.path.insert(0, HERE)
    import common_utils as cu

    n_folds = 1 if args.test else args.max_folds
    limit = cu.TIME_LIMIT_S
    steps = []
    if not args.skip_sklearn:
        steps.append(("sklearn", SKLEARN_NB, {}))
    if not args.skip_ludwig:
        steps += [(f"ludwig_{v}", LUDWIG_NB, {"LUDWIG_VARIANT": v}) for v in variants]

    est = sum(60 * n_folds if name == "sklearn" else n_folds * (limit + LUDWIG_OVERHEAD_S)
              for name, _, _ in steps)
    print(f"Task {cu.TASK_IDS[0]} | results folder '{cu.RUN_MODE_NAME}' | {n_folds} fold(s) | "
          f"{limit} s per run | Ludwig: {args.trials} parallel trial(s)")
    print("Plan: " + " -> ".join(name for name, _, _ in steps))
    print(f"Estimated total: ~{_fmt(est)} (Ludwig adds ~{LUDWIG_OVERHEAD_S} s per run)")
    if args.dry_run or not steps:
        return 0

    log_dir = os.path.join(HERE, "logs", datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(log_dir, exist_ok=True)
    start, report = time.time(), []
    for name, nb, extra in steps:
        out = os.path.join(log_dir, f"{name}.ipynb")
        print(f"\n[{_fmt(time.time() - start)}] Running {name} ...", flush=True)
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--_execute", nb, out],
            env={**env, **extra}, cwd=os.path.dirname(nb),
        )
        tool = "sklearn" if name == "sklearn" else "ludwig"
        sub = "" if tool == "sklearn" else extra["LUDWIG_VARIANT"]
        csv = os.path.join(HERE, tool, "results", cu.RUN_MODE_NAME, sub,
                           f"task_{cu.TASK_IDS[0]}_{tool}_all_runs.csv")
        rows = sum(1 for _ in open(csv)) - 1 if os.path.isfile(csv) else 0
        ok = proc.returncode == 0 and rows > 0
        report.append((name, ok, rows, time.time() - t0))
        print(f"[{_fmt(time.time() - start)}] {name}: {'OK' if ok else 'FAILED'} "
              f"({rows} fold(s) saved, {_fmt(time.time() - t0)}). Log: {out}", flush=True)

    print("\n=== Summary ===")
    for name, ok, rows, secs in report:
        print(f"  {name:<16} {'OK    ' if ok else 'FAILED'} {rows} fold(s)  {_fmt(secs)}")
    print(f"Total time: {_fmt(time.time() - start)}\n")

    try:
        import compare_variants
        compare_variants.compare(cu.RUN_MODE_NAME, cu.TASK_IDS[0])
    except SystemExit as exc:
        print(f"Comparison skipped: {exc}")
    return 0 if all(ok for _, ok, _, _ in report) else 1


if __name__ == "__main__":
    sys.exit(main())
