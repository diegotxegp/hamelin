# HAMELIN — Building and moving the standalone executable

This guide explains how to build a single-file executable of HAMELIN and how to run it on another machine, for example a virtual machine.

## 1. What you get

A single Linux x86-64 executable (`hamelin`, about 700 MB) that contains Python, PySide6, Ludwig, PyTorch (CPU) and Ray. It needs no Python installation on the target machine. It runs on the CPU only.

> A standalone executable is built for one operating system and one processor architecture. An executable built on Linux does not run on Windows or macOS; build it on the same kind of system where it will run.

## 2. Building it

Use a virtual environment with the **CPU-only** PyTorch. The default environment ships the CUDA libraries (about 4 GB) and the executable would be several times larger for no benefit on a machine without a GPU.

```bash
# 1. Environment with the pinned dependencies, without CUDA packages
uv venv --python 3.12 .venv-build
grep -viE "^(nvidia|cuda|triton|torch==|torchaudio==|torchvision==|torchcodec)" requirements.txt > /tmp/req_nocuda.txt
uv pip install --python .venv-build/bin/python --no-deps -r /tmp/req_nocuda.txt
uv pip install --python .venv-build/bin/python --no-deps --index-url https://download.pytorch.org/whl/cpu \
    "torch==2.14.0+cpu" "torchvision==0.29.0+cpu" "torchaudio==2.11.0+cpu"
uv pip install --python .venv-build/bin/python --no-deps -e .
uv pip install --python .venv-build/bin/python pyinstaller altgraph pyinstaller-hooks-contrib setuptools packaging

# 2. One-file build (10–25 minutes)
HAMELIN_ONEFILE=1 .venv-build/bin/pyinstaller --noconfirm --clean hamelin.spec
```

The result is `dist/hamelin`. `hamelin.spec` also builds a folder version (without `HAMELIN_ONEFILE=1`), which starts faster but must be copied as a whole folder.

## 3. Moving it to a virtual machine

**Before you start**
- The VM must be Linux x86-64 with a glibc **at least as recent as the build machine's** (`ldd --version`; the build made on Ubuntu 22.04 needs glibc 2.35 or newer, i.e. Ubuntu 22.04+, Debian 12+, Fedora 36+ …). To support older systems, build on the oldest system you need to support.
- It needs a graphical desktop (X11 or Wayland). On a headless server the window cannot open.
- Resources: 4 GB of RAM at the very least, 8 GB or more recommended; 4 GB of free disk space (the executable unpacks itself into `/tmp` every time it starts, about 2 GB).
- Qt needs a few system libraries. On a minimal Ubuntu/Debian install:
  ```bash
  sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
      libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 libxcb-xkb1 libegl1 libgl1 libglib2.0-0
  ```

**Steps**
1. Copy the `hamelin` file to the VM (shared folder, `scp hamelin user@vm:~/`, or a USB disk).
2. Make it executable: `chmod +x hamelin`.
3. Copy your datasets to the VM if you want to use them (any folder).
4. Run it from a terminal: `./hamelin`. The first start takes 20–60 seconds because the file unpacks itself; the console shows the log.

**Where the data is kept.** The application creates a `workspace/` folder **next to the executable** (settings, logs, projects, results). Keep the executable in a folder you own (for example `~/hamelin/`) and do not run it from a read-only location. To store the data somewhere else, set the environment variable before starting: `HAMELIN_WORKSPACE=/path/to/data ./hamelin`. Projects can be moved between machines by copying their folder from `workspace/Projects/`.

**Things to keep in mind**
- Training runs on the CPU. Give the VM as many cores as you can; the default number of parallel trials is computed from the cores and RAM it sees. With few cores, use a longer time limit.
- Do not start two copies of HAMELIN at the same time on the same workspace.
- If the temporary folder is small, point it to a larger disk: `TMPDIR=/big/disk/tmp ./hamelin`.
- On a VM without 3D acceleration, if the window is blank or the application does not start, try `QT_QUICK_BACKEND=software LIBGL_ALWAYS_SOFTWARE=1 ./hamelin`, or `QT_QPA_PLATFORM=xcb ./hamelin` to force X11.
- No internet connection is needed to run it; nothing is sent anywhere.
- Ray (used for the hyperparameter search) opens local ports on `127.0.0.1` only; a firewall does not need changing.
- Give the VM a fixed clock/time zone; the dates in the change records and reports use the system time.

## 4. Checking that it works

```bash
./hamelin --version
QT_QPA_PLATFORM=offscreen timeout 60 ./hamelin      # should log "GUI launched successfully"
```

To test a complete training without the interface (the executable accepts `-c`, like Python):

```bash
./hamelin -c "$(cat smoke_train.py)" diabetes.csv     # tools/smoke_train.py in the repository
```
