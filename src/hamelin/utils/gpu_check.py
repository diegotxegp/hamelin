"""
GPU compatibility check
~~~~~~~~~~~~~~~~~~~~~~~

Hides a CUDA GPU that the installed PyTorch build cannot use, so training
falls back to the CPU instead of failing deep inside a Ray worker.  The probe
imports torch in a throwaway subprocess, which takes seconds, so it runs on a
background thread: ``start_gpu_probe()`` at launch, ``wait_for_gpu_probe()``
right before a training run needs the verdict.
"""

import os
import shutil
import subprocess
import sys
import threading

from hamelin.utils.logger import log

_thread: threading.Thread | None = None


def disable_unsupported_gpu():
    """Hide the GPU from this process (and, via inherited env, every Ray/
    Ludwig worker subprocess) if it exists but isn't one the installed
    PyTorch build actually has kernels for.

    Ray/Ludwig auto-detect any CUDA-capable GPU and schedule training
    trials on it unconditionally - on an old/unsupported GPU (e.g. compute
    capability sm_50 when the installed torch only ships sm_75+ kernels)
    this doesn't fail until deep inside a Ray worker mid-training, as a
    cryptic ``CUBLAS_STATUS_ARCH_MISMATCH``, long after the point where a
    clean CPU fallback would have been simple. Checked once at startup, in
    throwaway subprocesses, so a CUDA context doesn't get pinned to *this*
    process before we've decided whether the GPU should be visible at all.
    """
    if "CUDA_VISIBLE_DEVICES" in os.environ:
        return  # already explicitly configured - respect it

    if shutil.which("nvidia-smi") is None:
        return  # no NVIDIA driver/GPU on this machine - nothing to check

    try:
        smi = subprocess.run(
            ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
            timeout=5, capture_output=True, text=True,
        )
        if smi.returncode != 0 or not smi.stdout.strip():
            return
    except Exception:
        return  # no usable nvidia-smi - let torch/ray behave as normal

    # The verdict is printed rather than signalled through sys.exit(1): a
    # debugger set to break on raised exceptions pauses on that SystemExit
    # inside this throwaway subprocess, which looked like a second process
    # to close every time the app was started under it.
    probe = (
        "import torch\n"
        "verdict = 'ok'\n"
        "if torch.cuda.is_available():\n"
        "    major, minor = torch.cuda.get_device_capability(0)\n"
        "    arch = f'sm_{major}{minor}'\n"
        "    supported = torch.cuda.get_arch_list()\n"
        "    if supported and arch not in supported:\n"
        "        verdict = 'unsupported'\n"
        "print(verdict)\n"
    )
    try:
        # sys.executable [-c] is the same subprocess re-entry pattern Ray
        # itself relies on, already handled by _run_as_python_interpreter
        # above when this is a frozen build.
        probe_result = subprocess.run(
            [sys.executable, "-c", probe], timeout=30, capture_output=True,
        )
    except Exception:
        log.warning("GPU compatibility probe failed to run; leaving GPU visible")
        return

    if probe_result.returncode == 0 and b"unsupported" in probe_result.stdout:
        log.warning(
            "Detected GPU's compute capability isn't supported by the "
            "installed PyTorch build - disabling GPU for this session "
            "(training will run on CPU instead of crashing mid-run)."
        )
        os.environ["CUDA_VISIBLE_DEVICES"] = ""


def start_gpu_probe() -> None:
    """Run the probe once, on a daemon thread (no-op if already started)."""
    global _thread
    if _thread is None:
        _thread = threading.Thread(target=disable_unsupported_gpu, name="gpu-probe", daemon=True)
        _thread.start()


def wait_for_gpu_probe(timeout: float = 40.0) -> None:
    """Block until the probe has decided whether the GPU stays visible."""
    if _thread is not None:
        _thread.join(timeout)


# --- GPU wait shared with the desktop -------------------------------------

GPU_WAIT_MARGIN = 0.02  # fraction of GPU memory allowed above the idle baseline


def gpu_wait_thresholds(memory_utils: dict, margin: float = GPU_WAIT_MARGIN) -> dict:
    """Per-GPU memory fraction a new trial may find in use, keyed by GPU id.

    ``memory_utils`` maps GPU id -> fraction of its memory in use right now.
    """
    return {str(gpu): util + margin for gpu, util in memory_utils.items()}


def init_ray_for_training() -> None:
    """Start Ray so Ludwig's per-trial GPU wait tolerates what the desktop uses.

    Before every trial Ludwig calls ``ray.tune.utils.wait_for_gpu``, which
    blocks until the GPU uses at most 1% of its memory (the previous trial may
    not have freed it yet) and otherwise fails the trial with "GPU memory was
    not freed". The 1% is hard-coded in Ludwig. A GPU that also draws the
    screen (Xorg, remote desktop, browser) is never below it, so on a
    typical computer with a single GPU every trial would fail.

    Here the limit becomes each GPU's memory use right now, before any trial,
    plus ``GPU_WAIT_MARGIN``: a trial that has not released its memory (a CUDA
    context alone is ~300 MB) is still waited for. Call it right before
    ``train_with_config``; Ludwig then reuses this Ray instead of starting its
    own. Without GPUtil or GPUs it does nothing and Ludwig starts Ray itself.
    """
    try:
        import GPUtil
        import ray
        if ray.is_initialized():
            return
        baseline = {str(g.id): g.memoryUtil for g in GPUtil.getGPUs()}
    except Exception:  # noqa: BLE001 - no GPU stack: Ludwig's own init
        return
    if not baseline:
        return
    thresholds = gpu_wait_thresholds(baseline)

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

    log.info("GPU memory in use before training: "
             + ", ".join(f"GPU {g} {u:.1%}" for g, u in baseline.items()))
    os.environ.setdefault("TUNE_FORCE_TRIAL_CLEANUP_S", "120")  # as Ludwig's own init
    try:
        ray.init(ignore_reinit_error=True,
                 runtime_env={"worker_process_setup_hook": relax_gpu_wait})
    except Exception as exc:  # noqa: BLE001 - let Ludwig start Ray its own way
        log.warning(f"Could not start Ray with the relaxed GPU wait: {exc}")
