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
