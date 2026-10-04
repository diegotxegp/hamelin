"""
Shared utilities for the Ludwig and scikit-learn benchmark notebooks.

This module is intentionally lightweight (openml, pandas, numpy only) so
it can be installed without conflict in either the Ludwig venv or the
scikit-learn venv. Both notebooks import from here to guarantee they use
the EXACT SAME task list, fold/seed assignment, and I/O format — this is
required for the two sets of results to be directly comparable.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import numpy as np
import pandas as pd
import openml


# =================================================================
# SHARED EXPERIMENTAL CONFIGURATION
# =================================================================

# Run modes (set at most one to True; both False -> full experiment):
#   TEST_MODE        -> smoke test: TEST_TASK_ID, fold 0 only, short time limit.
#   SINGLE_TASK_MODE -> one task (SINGLE_TASK_ID) with ALL its OpenML folds,
#                       full time limit. Cheap way to compare both tools.
#   neither          -> every task in ALL_TASK_IDS with all their folds.
# Each setting can be overridden from the environment (BENCH_* variables),
# so the file does not have to be edited to launch an automated run.
def _env_bool(name, default):
    value = os.environ.get(name)
    return default if value is None else value.strip().lower() in ("1", "true", "yes")


def _env_int(name, default):
    value = os.environ.get(name)
    return default if not value else int(value)


TEST_MODE = _env_bool("BENCH_TEST_MODE", True)
# True -> a dataset that already has all its runs saved is skipped, and one that
# is only partly done is discarded and restarted from fold 0 (so an interrupted
# experiment continues dataset by dataset). False -> start over (overwrites).
RESUME = _env_bool("BENCH_RESUME", True)
# Times a dataset is started over from fold 0 when one of its runs fails. Its
# earlier runs are discarded (moved to <results>/discarded/) so every dataset
# comes from one uninterrupted, homogeneous series of runs.
DATASET_RETRIES = _env_int("BENCH_DATASET_RETRIES", 1)
SINGLE_TASK_MODE = _env_bool("BENCH_SINGLE_TASK_MODE", False)
TEST_TASK_ID = _env_int("BENCH_TEST_TASK_ID", 37)  # 37 = diabetes
SINGLE_TASK_ID = TEST_TASK_ID  # same task as the smoke test, so both modes are comparable

ALL_TASK_IDS = [
    10101, 15, 31, 37, 9957,         # Binary classification
    3560, 23, 3011, 18, 53,          # Multi-class classification
    2295, 2301, 52948, 4839          # Regression
]

if TEST_MODE and SINGLE_TASK_MODE:
    raise ValueError("Set only one of TEST_MODE / SINGLE_TASK_MODE to True.")

# Time limit per run (seconds) for BOTH tools. None -> 300 s in TEST_MODE, else 1000 s.
TIME_LIMIT_OVERRIDE_S = _env_int("BENCH_TIME_LIMIT_S", None)
# Folds per task: None -> every OpenML fold; N -> only the first N (ignored in TEST_MODE,
# which always runs fold 0). Useful for a shorter run.
MAX_FOLDS = _env_int("BENCH_MAX_FOLDS", None)

TIME_LIMIT_S = TIME_LIMIT_OVERRIDE_S or (300 if TEST_MODE else 1000)

FOLDS_LABEL = f"{MAX_FOLDS}folds" if MAX_FOLDS else "all_folds"

if TEST_MODE:
    TASK_IDS, RUN_MODE_NAME = [TEST_TASK_ID], "test"
elif SINGLE_TASK_MODE:
    TASK_IDS = [SINGLE_TASK_ID]
    # The name encodes folds and time so runs with different settings never share a folder.
    RUN_MODE_NAME = f"single_task_{FOLDS_LABEL}_{TIME_LIMIT_S}s"
else:
    TASK_IDS = ALL_TASK_IDS
    RUN_MODE_NAME = f"full_{FOLDS_LABEL}_{TIME_LIMIT_S}s"

# Everything the benchmark writes lives under results/<run mode>/:
#   ludwig/  sklearn/  analysis/  logs/      (and results/datasets_summary.csv)
BENCHMARKS_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_ROOT = os.path.join(BENCHMARKS_DIR, "results")


def results_dir(tool):
    """results/<run mode>/<tool>: where one tool's runs, summary and logs are saved."""
    return os.path.join(RESULTS_ROOT, RUN_MODE_NAME, tool)


# One distinct seed per official fold (fold i -> SEEDS[i]).
SEEDS = [123, 2027, 99, 7, 42, 1984, 2024, 555, 314, 271]

# True  -> one run per official fold, seeds assigned without repetition.
# False -> every official fold repeated with every seed (fully-crossed
#          design; N_folds x N_seeds runs per task).
ROTATE_SEEDS_ACROSS_FOLDS = True


# =================================================================
# PROTOCOL: FOLD/REPEAT DISCOVERY AND DATA RETRIEVAL
# =================================================================

def get_fold_repeat_seed_plan(task):
    """
    Builds the list of (repeat, fold, seed) runs for a task, based on
    the fold/repeat structure OpenML actually defines for it.
    """
    try:
        n_repeats, n_folds, _n_samples = task.get_split_dimensions()
    except Exception as e:
        print(f"[WARN] Could not read split dimensions for task "
              f"{task.task_id}: {e}. Falling back to (repeat=0, fold=0).")
        n_repeats, n_folds = 1, 1

    if TEST_MODE:
        n_repeats, n_folds = 1, 1
    elif MAX_FOLDS:
        n_folds = min(n_folds, MAX_FOLDS)

    plan = []
    idx = 0
    for r in range(n_repeats):
        for f in range(n_folds):
            if ROTATE_SEEDS_ACROSS_FOLDS:
                seed = SEEDS[idx % len(SEEDS)]
                plan.append((r, f, seed))
                idx += 1
            else:
                for seed in SEEDS:
                    plan.append((r, f, seed))

    print(f"[INFO] Task {task.task_id}: n_repeats={n_repeats}, n_folds={n_folds} "
          f"-> {len(plan)} runs planned.")
    return plan


def download_openml_task_split(task, repeat, fold):
    """Retrieves a specific (repeat, fold) train/test split for a task."""
    try:
        dataset = task.get_dataset()
        X, y, categorical_indicator, attribute_names = dataset.get_data(
            dataset_format="dataframe", target=task.target_name
        )

        train_indices, test_indices = task.get_train_test_split_indices(
            repeat=repeat, fold=fold
        )

        X_train = X.iloc[train_indices].copy()
        X_test = X.iloc[test_indices].copy()
        y_train = y.iloc[train_indices].copy()
        y_test = y.iloc[test_indices].copy()

        train_df = X_train.copy()
        train_df[task.target_name] = y_train

        test_df = X_test.copy()
        test_df[task.target_name] = y_test

        return {
            "train_df": train_df,
            "test_df": test_df,
            "target_column": task.target_name,
            "evaluation_measure": task.evaluation_measure,
            "dataset_name": dataset.name,
            "task_type": task.task_type,
            "categorical_indicator": categorical_indicator,
            "attribute_names": attribute_names,
        }
    except Exception as e:
        print(f"[ERROR] Downloading task {task.task_id} (repeat={repeat}, fold={fold}): {e}")
        return None


# =================================================================
# SHARED UTILITIES
# =================================================================

def safe_metric_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        if value.lower() in ["nan", "inf", "-inf", "null", "none"]:
            return None
        try:
            return float(value)
        except Exception:
            return None
    if isinstance(value, (int, float)):
        if str(value).lower() in ["nan", "inf", "-inf"]:
            return None
    return value


def extra_classification_metrics(y_true, y_pred):
    """Balanced accuracy and macro-F1 from predicted labels (robust to class imbalance).

    Computed with scikit-learn's own definitions for both tools, so they are
    directly comparable. Evaluation only: it does not touch how models are trained.
    Returns {} if the metrics cannot be computed.
    """
    try:
        from sklearn.metrics import balanced_accuracy_score, f1_score
        y_true = pd.Series(y_true).astype(str).to_numpy()
        y_pred = pd.Series(y_pred).astype(str).to_numpy()
        if len(y_true) != len(y_pred):
            raise ValueError(f"{len(y_true)} labels vs {len(y_pred)} predictions")
        return {
            "balanced_accuracy": safe_metric_value(balanced_accuracy_score(y_true, y_pred)),
            "f1_macro": safe_metric_value(f1_score(y_true, y_pred, average="macro")),
        }
    except Exception as e:
        print(f"[WARN] Could not compute balanced accuracy / macro-F1: {e}")
        return {}


def save_environment_info(save_dir, tool):
    """Writes environment_<tool>.json: the machine and library versions of this run.

    Ludwig decides concurrency and device use on its own, so its results depend
    on the hardware; this file is what to quote in the paper (CPU, RAM, GPUs,
    versions, time limit, run mode). Never raises.
    """
    import json
    import platform
    from datetime import datetime
    from importlib import metadata

    def version(pkg):
        try:
            return metadata.version(pkg)
        except metadata.PackageNotFoundError:
            return None

    info = {
        "tool": tool,
        "date": datetime.now().isoformat(timespec="seconds"),
        "run_mode": RUN_MODE_NAME,
        "time_limit_s": TIME_LIMIT_S,
        "max_folds": MAX_FOLDS,
        "seeds": SEEDS,
        "os": platform.platform(),
        "python": platform.python_version(),
        "cpu_model": platform.processor() or None,
        "libraries": {p: version(p) for p in (
            "ludwig", "ray", "torch", "scikit-learn", "openml", "numpy", "pandas")},
    }
    try:
        import psutil
        info["cpu_physical_cores"] = psutil.cpu_count(logical=False)
        info["cpu_logical_cores"] = psutil.cpu_count(logical=True)
        info["ram_gb"] = round(psutil.virtual_memory().total / 1024**3, 1)
    except Exception:
        pass
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    info["cpu_model"] = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    # GPUs present on the machine, and whether they are visible to this run
    # (disable_unsupported_gpu() hides them by setting CUDA_VISIBLE_DEVICES="").
    try:
        import psutil
        freq = psutil.cpu_freq()
        if freq:
            info["cpu_max_mhz"] = round(freq.max or freq.current)
    except Exception:
        pass
    try:  # code version, so the numbers can be tied to the exact scripts that made them
        here = os.path.dirname(os.path.abspath(__file__))
        git = lambda *a: subprocess.run(["git", "-C", here, *a], capture_output=True,
                                        text=True, timeout=30).stdout.strip()
        info["git_commit"] = git("rev-parse", "HEAD") or None
        info["git_uncommitted_changes"] = bool(git("status", "--porcelain", "--", here))
    except Exception:
        pass
    if tool == "ludwig":
        try:  # static build info only: it must not create a CUDA context
            import torch
            info["torch_cuda_build"] = torch.version.cuda
            info["torch_cuda_arch_list"] = torch.cuda.get_arch_list()
        except Exception:
            pass
    info["cuda_visible_devices"] = os.environ.get("CUDA_VISIBLE_DEVICES")
    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,compute_cap",
                 "--format=csv,noheader"], capture_output=True, text=True, timeout=30)
            info["gpus_on_machine"] = [g.strip() for g in out.stdout.strip().splitlines() if g.strip()]
        except Exception:
            pass
    # scikit-learn never uses the GPU; only Ludwig does, if it stays visible.
    info["gpus_used"] = (tool == "ludwig" and bool(info.get("gpus_on_machine"))
                         and info["cuda_visible_devices"] != "")
    try:
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, f"environment_{tool}.json")
        if RESUME and os.path.isfile(path):
            # Resumed run: keep the original file, and add another one only if the
            # machine or the software differ from it (e.g. resumed on another PC).
            with open(path) as f:
                original = json.load(f)
            same_env = ("os", "python", "cpu_model", "cpu_logical_cores", "ram_gb",
                        "libraries", "gpus_on_machine", "gpus_used", "git_commit")
            if all(original.get(k) == info.get(k) for k in same_env):
                print(f"[ENV] Same machine and versions as {os.path.basename(path)}; nothing new recorded.")
                return
            path = os.path.join(save_dir, "environment_{}_resumed_{}.json".format(
                tool, datetime.now().strftime("%Y%m%d_%H%M%S")))
        with open(path, "w") as f:
            json.dump(info, f, indent=2)
        print(f"[SAVE] {os.path.basename(path)}")
    except Exception as e:
        print(f"[WARN] Could not save the environment info: {e}")


def is_binary_classification(task_type, y_train):
    return "classification" in task_type.lower() and y_train.nunique() == 2


def save_incremental_results(task_id, method, runs, dataset_name, task_type,
                              evaluation_measure, save_dir):
    """Writes results to disk incrementally, one CSV per task/method."""
    try:
        os.makedirs(save_dir, exist_ok=True)
        if not runs:
            return
        rows = []
        for run in runs:
            row = {
                "task_id": task_id,
                "method": method,
                "repeat": run["repeat"],
                "fold": run["fold"],
                "seed": run["seed"],
                "dataset_name": dataset_name,
                "task_type": task_type,
                "evaluation_measure": evaluation_measure,
            }
            row.update(run["metrics"])
            rows.append(row)
        df = pd.DataFrame(rows)
        filename = f"task_{task_id}_{method}_all_runs.csv"
        df.to_csv(os.path.join(save_dir, filename), index=False)
        print(f"[SAVE] {filename}")
    except Exception as e:
        print(f"[ERROR] Saving incremental results for {method}: {e}")


def start_fresh_if_requested(save_dir):
    """With BENCH_RESUME=0, moves the previous results of this run mode aside.

    The folder becomes <save_dir>.old_<timestamp> (never overwritten in place, so
    a mistyped variable cannot destroy days of results; delete it by hand when
    sure). With the default RESUME on, nothing is touched.
    """
    if RESUME or not os.path.isdir(save_dir) or not os.listdir(save_dir):
        return
    from datetime import datetime
    backup = f"{save_dir}.old_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.move(save_dir, backup)
    print(f"[FRESH START] Previous results moved to {os.path.relpath(backup, os.path.dirname(save_dir))}")


def archive_task_results(save_dir, task_id, method):
    """Moves a dataset's runs CSV to <save_dir>/discarded/ (kept for inspection; the analysis ignores it)."""
    path = os.path.join(save_dir, f"task_{task_id}_{method}_all_runs.csv")
    if not os.path.isfile(path):
        return
    from datetime import datetime
    dest_dir = os.path.join(save_dir, "discarded")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "task_{}_{}_all_runs_{}.csv".format(
        task_id, method, datetime.now().strftime("%Y%m%d_%H%M%S")))
    shutil.move(path, dest)
    print(f"[DISCARD] task {task_id}: previous runs moved to {os.path.relpath(dest, save_dir)}")


def load_completed_runs(save_dir, task_id, method, expected_runs):
    """Resume point for one dataset, in the format `save_incremental_results` takes.

    - All `expected_runs` runs saved -> returns them (the dataset is skipped).
    - Only some saved -> they are discarded (archived) and the dataset restarts
      from fold 0: returns no runs.
    - Nothing saved, or RESUME off -> returns no runs.
    Returns (runs, (dataset_name, task_type, evaluation_measure)).
    """
    empty = ([], (None, None, None))
    path = os.path.join(save_dir, f"task_{task_id}_{method}_all_runs.csv")
    if not RESUME or not os.path.isfile(path):
        return empty
    try:
        df = pd.read_csv(path)
        id_cols = ["task_id", "method", "repeat", "fold", "seed",
                   "dataset_name", "task_type", "evaluation_measure"]
        runs = []
        for _, row in df.iterrows():
            metrics = {k: v for k, v in row.items() if k not in id_cols and pd.notna(v)}
            runs.append({"repeat": int(row["repeat"]), "fold": int(row["fold"]),
                         "seed": int(row["seed"]), "metrics": metrics})
        if len(runs) >= expected_runs:
            first = df.iloc[0]
            meta = (first["dataset_name"], first["task_type"],
                    first["evaluation_measure"] if pd.notna(first["evaluation_measure"]) else None)
            print(f"[RESUME] task {task_id}: all {len(runs)} runs already saved, skipping the dataset.")
            return runs, meta
        print(f"[RESTART] task {task_id}: only {len(runs)} of {expected_runs} runs were saved; "
              f"discarding them and starting the dataset over from fold 0.")
    except Exception as e:
        print(f"[WARN] Could not read {path} ({e}); starting this task over.")
    archive_task_results(save_dir, task_id, method)
    return empty


def save_summary(save_dir, method):
    """Writes summary_<method>.csv: mean and std of every numeric metric per task.

    Built from the task_*_<method>_all_runs.csv files already in save_dir, so
    it can be called at any time (it covers whatever tasks have finished).
    Std is the sample std (ddof=1); it is empty when a task has a single run.
    """
    try:
        frames = [
            pd.read_csv(os.path.join(save_dir, f))
            for f in sorted(os.listdir(save_dir))
            if f.startswith("task_") and f.endswith(f"_{method}_all_runs.csv")
        ]
        if not frames:
            return
        df = pd.concat(frames, ignore_index=True)
        id_cols = ["task_id", "method", "dataset_name", "task_type", "evaluation_measure"]
        skip = set(id_cols) | {"repeat", "fold", "seed"}
        metric_cols = [c for c in df.columns
                       if c not in skip and pd.api.types.is_numeric_dtype(df[c])]
        rows = []
        for keys, g in df.groupby(id_cols, sort=False, dropna=False):
            row = dict(zip(id_cols, keys))
            row["n_runs"] = len(g)
            for c in metric_cols:
                row[f"{c}_mean"] = g[c].mean()
                row[f"{c}_std"] = g[c].std()
            rows.append(row)
        pd.DataFrame(rows).to_csv(
            os.path.join(save_dir, f"summary_{method}.csv"), index=False)
        print(f"[SAVE] summary_{method}.csv")
    except Exception as e:
        print(f"[ERROR] Saving summary for {method}: {e}")


# =================================================================
# LUDWIG HELPERS: GPU FALLBACK AND TEMPORARY FILES
# =================================================================

def disable_unsupported_gpu():
    """Hides a CUDA GPU the installed PyTorch build has no kernels for.

    Without this, Ray/Ludwig schedule trials on the GPU and every one of
    them dies with CUBLAS_STATUS_ARCH_MISMATCH (e.g. compute capability
    sm_50 with a torch build that only ships sm_75+). Must be called BEFORE
    importing ludwig/torch so Ray workers inherit CUDA_VISIBLE_DEVICES.
    The check runs in throwaway subprocesses so no CUDA context is created
    in this process.
    """
    if "CUDA_VISIBLE_DEVICES" in os.environ:
        return  # already explicitly configured - respect it
    if shutil.which("nvidia-smi") is None:
        return  # no NVIDIA GPU
    probe = (
        "import torch\n"
        "verdict = 'ok'\n"
        "if torch.cuda.is_available():\n"
        "    major, minor = torch.cuda.get_device_capability(0)\n"
        "    supported = torch.cuda.get_arch_list()\n"
        "    if supported and f'sm_{major}{minor}' not in supported:\n"
        "        verdict = 'unsupported'\n"
        "print(verdict)\n"
    )
    try:
        out = subprocess.run([sys.executable, "-c", probe], timeout=60,
                             capture_output=True)
    except Exception:
        print("[WARN] GPU compatibility probe failed; leaving GPU visible")
        return
    if out.returncode == 0 and b"unsupported" in out.stdout:
        print("[INFO] GPU not supported by the installed PyTorch build - "
              "running on CPU.")
        os.environ["CUDA_VISIBLE_DEVICES"] = ""


GPU_WAIT_MARGIN = 0.02  # fraction of GPU memory above the idle baseline


def init_ray_for_ludwig():
    """Starts Ray so Ludwig's per-trial GPU wait tolerates the desktop's memory use.

    Before each trial Ludwig calls ray.tune.utils.wait_for_gpu, which blocks
    until the GPU uses at most 1% of its memory, to avoid starting on top of
    a previous trial that has not freed it yet. On a GPU that also drives
    the desktop (Xorg, remote desktop, browser) that never happens, so the
    trial fails with "GPU memory was not freed" and is retried or lost.
    Here the threshold becomes each GPU's memory use now, before any trial,
    plus GPU_WAIT_MARGIN: a leftover trial (a CUDA context alone is ~300 MB)
    is still waited for. Call it right before auto_train (after
    cleanup_ludwig_artifacts, which stops Ray); Ludwig reuses this Ray.
    Without GPUtil or GPUs it does nothing and Ludwig starts Ray itself.
    """
    try:
        import GPUtil
        import ray
        baseline = {str(g.id): g.memoryUtil for g in GPUtil.getGPUs()}
    except Exception:
        return
    if not baseline or ray.is_initialized():
        return
    thresholds = {gpu: util + GPU_WAIT_MARGIN for gpu, util in baseline.items()}

    def relax_gpu_wait():
        # Runs in every Ray worker before Ludwig is imported there, so
        # Ludwig's `from ray.tune.utils import wait_for_gpu` gets this one.
        # Nested (not module level) so Ray ships it by value.
        import ray.tune.utils
        original = ray.tune.utils.wait_for_gpu

        def wait_for_gpu(gpu_id=None, target_util=0.01, **kwargs):
            limit = max(target_util, thresholds.get(str(gpu_id), target_util))
            return original(gpu_id, target_util=limit, **kwargs)

        ray.tune.utils.wait_for_gpu = wait_for_gpu

    print("[INFO] GPU memory in use before the trials: "
          + ", ".join(f"GPU {g} {u:.1%}" for g, u in baseline.items()))
    os.environ.setdefault("TUNE_FORCE_TRIAL_CLEANUP_S", "120")  # as Ludwig's own init
    ray.init(ignore_reinit_error=True,
             runtime_env={"worker_process_setup_hook": relax_gpu_wait})


def cleanup_ludwig_artifacts(output_dir="."):
    """Removes Ludwig's disposable per-run files (and Ray's session logs) and stops Ray.

    auto_train dumps every hyperopt trial (checkpoints, logs, error files)
    under <output_dir>/hyperopt. The benchmark only needs the metrics, which
    are computed in memory before this is called, so nothing in there is
    needed afterwards. A stale hyperopt/ is also harmful: Ray auto-resumes
    from it and can poison the next run. Call it before and after each run.
    """
    try:
        import ray
        if ray.is_initialized():
            ray.shutdown()
    except Exception:
        pass
    hyperopt_dir = os.path.join(output_dir, "hyperopt")
    if os.path.isdir(hyperopt_dir):
        try:
            shutil.rmtree(hyperopt_dir)
        except OSError as e:
            print(f"[WARN] Could not remove {hyperopt_dir}: {e}")

    # Ray's own session logs/spill files live outside the project. Only
    # removed when no Ray is running at all (e.g. another Ludwig job in
    # parallel), since deleting them from under a live cluster breaks it.
    try:
        import psutil
        ray_running = any(
            (p.info["name"] or "").startswith(("raylet", "gcs_server"))
            for p in psutil.process_iter(["name"])
        )
        ray_tmp = os.path.join(tempfile.gettempdir(), "ray")
        if not ray_running and os.path.isdir(ray_tmp):
            shutil.rmtree(ray_tmp, ignore_errors=True)
    except Exception:
        pass
