# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for HAMELIN.

Build (onedir, faster to build/debug):
    uv run pyinstaller hamelin.spec
Output: dist/hamelin/hamelin (+ dist/hamelin/_internal/...)

Build (single file, easiest to copy to another machine):
    HAMELIN_ONEFILE=1 pyinstaller hamelin.spec
Output: dist/hamelin  (one executable; the user's data lives in a "workspace"
folder created next to it, or wherever the HAMELIN_WORKSPACE variable points)

For a machine without a GPU (a virtual machine, say) build inside a
virtual environment that has the CPU-only PyTorch: it is several GB smaller.

Notes:
- src/hamelin/main.py already has a `sys.frozen` shim (_run_as_python_
  interpreter) so Ray's own subprocess workers, which invoke
  `sys.executable [-u] script.py ...`, still work when sys.executable is
  this frozen binary rather than a real python interpreter.
- src/hamelin/utils/paths.py resolves resources/ via sys._MEIPASS when
  frozen instead of a source-relative __file__ walk - see its docstring.
  The `datas` entry below bundles src/hamelin/resources at the matching
  hamelin/resources path inside the build.
- Heavy ML deps (torch, ray, ludwig, dask) are only lazily imported by
  the app itself (see e.g. analytics/automl/ludwig_backend.py's own
  "imported lazily so app startup isn't penalised" comment), so
  PyInstaller's static import analysis can miss submodules they pull in
  dynamically at runtime - the hiddenimports/collect_* calls below are a
  first-pass guess based on what's already known to matter (Ray's own
  subprocess re-entry, Ludwig's schema/registry system); expect to need
  more after the first real run against a trained model.
"""

import os

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

block_cipher = None
ONEFILE = os.environ.get("HAMELIN_ONEFILE") == "1"

hiddenimports = (
    collect_submodules("ludwig")
    + collect_submodules("ray")
    + collect_submodules("dask")
    + collect_submodules("torchmetrics")
    + collect_submodules("qfluentwidgets")
)

datas = [
    ("src/hamelin/resources", "hamelin/resources"),
]
datas += collect_data_files("ludwig")
datas += collect_data_files("ray")

# torchvision 0.29 ships its compiled ops extension as _C_stable.so /
# image_stable.so (not the older torchvision._C the PyInstaller stdhook
# still hardcodes as a hiddenimport), so that hook's hiddenimports=
# ["torchvision._C"] silently no-ops and the .so never gets collected -
# torchmetrics (pulled in by ludwig) imports torchvision unconditionally,
# and its ops end up unregistered at runtime ("RuntimeError: operator
# torchvision::nms does not exist"). Collect the actual shared libraries
# directly instead of relying on that hook - collect_dynamic_libs's default
# search_patterns only match "lib*.so", which misses these (no "lib"
# prefix), so pass an explicit "*.so" pattern too.
binaries = collect_dynamic_libs("torchvision", search_patterns=["*.dll", "*.dylib", "lib*.so", "*.so"])

a = Analysis(
    ["src/hamelin/main.py"],
    pathex=["src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    # Ray's own internal agents (runtime_env agent, dashboard agent/server)
    # are spawned as `sys.executable <path-to-their-.py-file>` - real
    # subprocesses expecting an actual file on disk at that path, not code
    # packed into the PYZ archive. Force ray to also be collected as loose
    # .py source (alongside the normal PYZ copy used for everything else's
    # `import ray`) so those file paths resolve for real.
    module_collection_mode={"ray": "pyz+py"},
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if ONEFILE:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name="hamelin",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=True,  # keep a console: training logs print here
        disable_windowed_traceback=False,
        argv_emulation=False,
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="hamelin",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=True,  # keep a console for now - training logs print here
        disable_windowed_traceback=False,
        argv_emulation=False,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name="hamelin",
    )
