"""
Resource path resolution
~~~~~~~~~~~~~~~~~~~~~~~~~

Resolves the bundled-assets directory (logo, help images, ...) whether
running from a source checkout or from a PyInstaller-frozen build - a
plain ``Path(__file__).resolve().parent...`` walk only works for the
former, since a frozen module's ``__file__`` doesn't point at a real
on-disk path for anything packed into the PYZ archive.
"""

import os
import sys
from pathlib import Path


def resources_dir() -> Path:
    """Base directory for bundled app assets (``assets/``, ``help_images/``).

    - Source checkout: ``src/hamelin/resources/``.
    - PyInstaller build (onefile or onedir): ``sys._MEIPASS/hamelin/resources/``
      — ``_MEIPASS`` is set by the bootloader at runtime in both modes;
      ``hamelin.spec`` bundles ``src/hamelin/resources`` there under the
      matching ``hamelin/resources`` path.
    """
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return base / "hamelin" / "resources"
    return Path(__file__).resolve().parent.parent / "resources"


def workspace_dir() -> Path:
    """Folder that holds the user's data: ``config/``, ``logs/``, ``Projects/``, ``data/``.

    - ``HAMELIN_WORKSPACE`` environment variable, when set (portable/VM use).
    - Source checkout: ``<repository>/workspace``.
    - PyInstaller build (onefile or onedir): ``workspace/`` next to the
      executable, never inside the temporary extraction folder (which is
      deleted every time a onefile build exits).
    """
    override = os.environ.get("HAMELIN_WORKSPACE")
    if override:
        return Path(override).expanduser()
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "workspace"
    return Path(__file__).resolve().parents[3] / "workspace"
