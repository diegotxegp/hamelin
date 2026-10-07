"""
Helper functions for the Ludwig benchmark notebook (ludwig/ludwig_experiment.ipynb).

Everything a user or reviewer may want to change (run mode, time limit, the 80/20 split,
datasets and targets, seeds) is in the notebook's "Parameters" cell, not here. This module
only has functions: loading a dataset, saving and resuming results, recording the machine,
and the helpers Ludwig needs to run unattended (GPU fallback, temp files). They receive
what they need as arguments.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import pandas as pd


# =================================================================
# DATASETS
# =================================================================

def load_dataset(name, datasets, datasets_dir):
    """Reads <datasets_dir>/<group>/<name>.csv, where `datasets[name]` starts with (group, target).

    Returns a dict with the DataFrame (`df`), `target_column`, `group` and `task_type`
    ("classification" for the Binary and Classification groups, "regression" for Regression),
    or None if the file cannot be read or does not have the target column.
    """
    try:
        group, target = datasets[name][:2]
        df = pd.read_csv(os.path.join(datasets_dir, group, f"{name}.csv"))
        if target not in df.columns:
            raise ValueError(f"no column '{target}' (columns: {list(df.columns)})")
        return {
            "df": df,
            "target_column": target,
            "group": group,
            "task_type": "regression" if group == "Regression" else "classification",
        }
    except Exception as e:
        print(f"[ERROR] Reading dataset {name}: {e}")
        return None


# =================================================================
# RESULT FILES
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


def save_parameters(save_dir, parameters):
    """Writes parameters.json: the settings of this launch (the notebook's Parameters cell).

    Overwritten at every launch; the analysis reads it to know the time limit and how many
    runs each dataset should have.
    """
    try:
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, "parameters.json"), "w") as f:
            json.dump(parameters, f, indent=2)
    except Exception as e:
        print(f"[WARN] Could not save parameters.json: {e}")


def save_environment_info(save_dir, parameters, resume):
    """Writes environment_ludwig.json: the machine and library versions of this run.

    Ludwig decides concurrency and device use on its own, so its results depend
    on the hardware; this file is what to quote in the paper (CPU, RAM, GPUs,
    versions, parameters). Never raises.
    """
    import platform
    from datetime import datetime
    from importlib import metadata

    def version(pkg):
        try:
            return metadata.version(pkg)
        except metadata.PackageNotFoundError:
            return None

    info = {
        "tool": "ludwig",
        "date": datetime.now().isoformat(timespec="seconds"),
        "parameters": parameters,
        "os": platform.platform(),
        "python": platform.python_version(),
        "cpu_model": platform.processor() or None,
        "libraries": {p: version(p) for p in ("ludwig", "ray", "torch", "numpy", "pandas")},
    }
    try:
        import psutil
        info["cpu_physical_cores"] = psutil.cpu_count(logical=False)
        info["cpu_logical_cores"] = psutil.cpu_count(logical=True)
        info["ram_gb"] = round(psutil.virtual_memory().total / 1024**3, 1)
        freq = psutil.cpu_freq()
        if freq:
            info["cpu_max_mhz"] = round(freq.max or freq.current)
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
    try:  # code version, so the numbers can be tied to the exact scripts that made them
        here = os.path.dirname(os.path.abspath(__file__))
        git = lambda *a: subprocess.run(["git", "-C", here, *a], capture_output=True,
                                        text=True, timeout=30).stdout.strip()
        info["git_commit"] = git("rev-parse", "HEAD") or None
        info["git_uncommitted_changes"] = bool(git("status", "--porcelain", "--", here))
    except Exception:
        pass
    try:  # static build info only: it must not create a CUDA context
        import torch
        info["torch_cuda_build"] = torch.version.cuda
        info["torch_cuda_arch_list"] = torch.cuda.get_arch_list()
    except Exception:
        pass
    # GPUs present on the machine, and whether they are visible to this run
    # (disable_unsupported_gpu() hides them by setting CUDA_VISIBLE_DEVICES="").
    info["cuda_visible_devices"] = os.environ.get("CUDA_VISIBLE_DEVICES")
    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,compute_cap",
                 "--format=csv,noheader"], capture_output=True, text=True, timeout=30)
            info["gpus_on_machine"] = [g.strip() for g in out.stdout.strip().splitlines() if g.strip()]
        except Exception:
            pass
    info["gpus_used"] = bool(info.get("gpus_on_machine")) and info["cuda_visible_devices"] != ""
    try:
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, "environment_ludwig.json")
        if resume and os.path.isfile(path):
            # Resumed run: keep the original file, and add another one only if the
            # machine or the software differ from it (e.g. resumed on another PC).
            with open(path) as f:
                original = json.load(f)
            same_env = ("os", "python", "cpu_model", "cpu_logical_cores", "ram_gb",
                        "libraries", "gpus_on_machine", "gpus_used", "git_commit")
            if all(original.get(k) == info.get(k) for k in same_env):
                print(f"[ENV] Same machine and versions as {os.path.basename(path)}; nothing new recorded.")
                return
            path = os.path.join(save_dir, "environment_ludwig_resumed_{}.json".format(
                datetime.now().strftime("%Y%m%d_%H%M%S")))
        with open(path, "w") as f:
            json.dump(info, f, indent=2)
        print(f"[SAVE] {os.path.basename(path)}")
    except Exception as e:
        print(f"[WARN] Could not save the environment info: {e}")


def runs_path(save_dir, dataset):
    return os.path.join(save_dir, f"{dataset}_runs.csv")


def save_incremental_results(dataset, group, runs, save_dir):
    """Writes <dataset>_runs.csv: one row per run (seed), with its metrics."""
    try:
        os.makedirs(save_dir, exist_ok=True)
        if not runs:
            return
        rows = [{"dataset": dataset, "group": group, "seed": run["seed"], **run["metrics"]}
                for run in runs]
        pd.DataFrame(rows).to_csv(runs_path(save_dir, dataset), index=False)
        print(f"[SAVE] {dataset}_runs.csv")
    except Exception as e:
        print(f"[ERROR] Saving the results of {dataset}: {e}")


def start_fresh_if_requested(save_dir, resume):
    """With resume=False, moves the previous results of this run mode aside.

    The folder becomes <save_dir>.old_<timestamp> (never overwritten in place, so
    a wrong setting cannot destroy days of results; delete it by hand when
    sure). With resume=True, nothing is touched.
    """
    if resume or not os.path.isdir(save_dir) or not os.listdir(save_dir):
        return
    from datetime import datetime
    backup = f"{save_dir}.old_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.move(save_dir, backup)
    print(f"[FRESH START] Previous results moved to {os.path.relpath(backup, os.path.dirname(save_dir))}")


def archive_dataset_results(save_dir, dataset):
    """Moves a dataset's runs CSV to <save_dir>/discarded/ (kept for inspection; the analysis ignores it)."""
    path = runs_path(save_dir, dataset)
    if not os.path.isfile(path):
        return
    from datetime import datetime
    dest_dir = os.path.join(save_dir, "discarded")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "{}_runs_{}.csv".format(dataset, datetime.now().strftime("%Y%m%d_%H%M%S")))
    shutil.move(path, dest)
    print(f"[DISCARD] {dataset}: previous runs moved to {os.path.relpath(dest, save_dir)}")


def load_completed_runs(save_dir, dataset, expected_runs, resume):
    """Resume point for one dataset, in the format `save_incremental_results` takes.

    - All `expected_runs` runs saved -> returns them (the dataset is skipped).
    - Only some saved -> they are discarded (archived) and the dataset restarts
      from its first seed: returns no runs.
    - Nothing saved, or resume=False -> returns no runs.
    """
    path = runs_path(save_dir, dataset)
    if not resume or not os.path.isfile(path):
        return []
    try:
        df = pd.read_csv(path)
        runs = []
        for _, row in df.iterrows():
            metrics = {k: v for k, v in row.items() if k not in ("dataset", "group", "seed") and pd.notna(v)}
            runs.append({"seed": int(row["seed"]), "metrics": metrics})
        if len(runs) >= expected_runs:
            print(f"[RESUME] {dataset}: all {len(runs)} runs already saved, skipping the dataset.")
            return runs
        print(f"[RESTART] {dataset}: only {len(runs)} of {expected_runs} runs were saved; "
              f"discarding them and starting the dataset over from its first seed.")
    except Exception as e:
        print(f"[WARN] Could not read {path} ({e}); starting this dataset over.")
    archive_dataset_results(save_dir, dataset)
    return []


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


LUDWIG_TMP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ludwig-tmp")


def use_private_tmpdir():
    """Points TMPDIR (this process and the Ray workers it starts) at a private dir.

    Ludwig's hyperopt copies the whole model into a fresh tempfile.mkdtemp()
    on every epoch of every trial and never deletes it, so /tmp fills the
    disk over a long benchmark. Here those copies land in
    .ludwig-tmp/<pid>/, which cleanup_ludwig_artifacts empties. Must run
    before Ray starts so the workers inherit it.
    """
    path = os.path.join(LUDWIG_TMP_ROOT, str(os.getpid()))
    os.makedirs(path, exist_ok=True)
    os.environ["TMPDIR"] = path
    # Ray derives its session dir from TMPDIR, and the socket paths inside it
    # would exceed the 107-byte AF_UNIX limit under this project's path.
    os.environ.setdefault("RAY_TMPDIR", "/tmp")
    tempfile.tempdir = path


def _purge_private_tmpdirs():
    """Deletes this process's private tmp dir and those of processes that no longer exist."""
    if not os.path.isdir(LUDWIG_TMP_ROOT):
        return
    for name in os.listdir(LUDWIG_TMP_ROOT):
        if name == str(os.getpid()) or not (name.isdigit() and os.path.exists(f"/proc/{name}")):
            shutil.rmtree(os.path.join(LUDWIG_TMP_ROOT, name), ignore_errors=True)


def cleanup_ludwig_artifacts(output_dir="."):
    """Removes Ludwig's disposable per-run files (and Ray's session logs) and stops Ray.

    auto_train dumps every hyperopt trial (checkpoints, logs, error files)
    under <output_dir>/hyperopt. The benchmark only needs the metrics, which
    are computed in memory before this is called, so nothing in there is
    needed afterwards (nor are the per-epoch model copies in the private
    tmp dir, see use_private_tmpdir). A stale hyperopt/ is also harmful: Ray auto-resumes
    from it and can poison the next run. Call it before and after each run.
    """
    try:
        import ray
        if ray.is_initialized():
            ray.shutdown()
    except Exception:
        pass
    _purge_private_tmpdirs()
    use_private_tmpdir()
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
        ray_tmp = os.path.join(os.environ.get("RAY_TMPDIR", "/tmp"), "ray")
        if not ray_running and os.path.isdir(ray_tmp):
            shutil.rmtree(ray_tmp, ignore_errors=True)
    except Exception:
        pass

    # Memory of this process: the model of the finished run (and its CUDA cache) must not pile up
    # over the hours a notebook kernel lives.
    import gc
    gc.collect()
    try:
        import torch
        if torch.cuda.is_initialized():
            torch.cuda.empty_cache()
    except Exception:
        pass


def log_available_memory(warn_below_gb=4.0):
    """Prints the RAM available before a run. Ludwig runs as many trials in parallel as it sees
    fit (~0.5-1.5 GB each); if the machine is short of memory Ray kills trials and the run fails."""
    try:
        import psutil
        free_gb = psutil.virtual_memory().available / 1024**3
        warning = "  [WARN] low: Ray may kill trials; close other applications" if free_gb < warn_below_gb else ""
        print(f"[INFO] RAM available: {free_gb:.1f} GB{warning}")
    except Exception:
        pass
