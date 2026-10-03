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
# Each setting can be overridden from the environment (run_screening.py does this),
# so the file does not have to be edited to launch an automated run.
def _env_bool(name, default):
    value = os.environ.get(name)
    return default if value is None else value.strip().lower() in ("1", "true", "yes")


def _env_int(name, default):
    value = os.environ.get(name)
    return default if not value else int(value)


TEST_MODE = _env_bool("BENCH_TEST_MODE", True)
SINGLE_TASK_MODE = _env_bool("BENCH_SINGLE_TASK_MODE", False)
TEST_TASK_ID = 37          # diabetes
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
# which always runs fold 0). Useful for a cheap screening of the Ludwig variants.
MAX_FOLDS = _env_int("BENCH_MAX_FOLDS", None)

TIME_LIMIT_S = TIME_LIMIT_OVERRIDE_S or (300 if TEST_MODE else 1000)

if TEST_MODE:
    TASK_IDS, RUN_MODE_NAME = [TEST_TASK_ID], "test"
elif SINGLE_TASK_MODE:
    TASK_IDS = [SINGLE_TASK_ID]
    # The name encodes folds and time so runs with different settings never share a folder.
    RUN_MODE_NAME = f"single_task_{MAX_FOLDS or 'all'}f_{TIME_LIMIT_S}s"
else:
    TASK_IDS = ALL_TASK_IDS
    RUN_MODE_NAME = f"full_{MAX_FOLDS or 'all'}f_{TIME_LIMIT_S}s"

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
# (same approach as Hamelin's utils/gpu_check.py and ludwig_backend.py)
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
    # removed when no Ray is running at all (e.g. Hamelin training in
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
