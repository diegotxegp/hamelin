"""
Resource path resolution
~~~~~~~~~~~~~~~~~~~~~~~~~

Resolves the bundled-assets directory (logo, help images, ...) whether
running from a source checkout or from a PyInstaller-frozen build - a
plain ``Path(__file__).resolve().parent...`` walk only works for the
former, since a frozen module's ``__file__`` doesn't point at a real
on-disk path for anything packed into the PYZ archive.
"""

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
