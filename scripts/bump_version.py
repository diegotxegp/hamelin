#!/usr/bin/env python3
"""Set the Hamelin version in every file that carries it, or check they agree.

    python scripts/bump_version.py 0.3.0     # update all files (and the release date)
    python scripts/bump_version.py --check   # exit 1 if the files disagree

Files: src/hamelin/__init__.py (the source the app reads), pyproject.toml and
CITATION.cff. Afterwards run `uv lock` so uv.lock follows (done here if uv is on PATH).
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "src/hamelin/__init__.py"
PYPROJECT = ROOT / "pyproject.toml"
CITATION = ROOT / "CITATION.cff"

INIT_RE = re.compile(r'^__version__ = "([^"]+)"', re.M)
PYPROJECT_RE = re.compile(r'^version = "([^"]+)"', re.M)
CITATION_RE = re.compile(r"^version: (\S+)", re.M)
DATE_RE = re.compile(r"^date-released: \S+\n", re.M)
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def current() -> dict[str, str]:
    return {
        "src/hamelin/__init__.py": INIT_RE.search(INIT.read_text(encoding="utf-8")).group(1),
        "pyproject.toml": PYPROJECT_RE.search(PYPROJECT.read_text(encoding="utf-8")).group(1),
        "CITATION.cff": CITATION_RE.search(CITATION.read_text(encoding="utf-8")).group(1),
    }


def check() -> int:
    versions = current()
    for name, value in versions.items():
        print(f"{name:28} {value}")
    if len(set(versions.values())) > 1:
        print("MISMATCH: the files carry different versions", file=sys.stderr)
        return 1
    return 0


def bump(new: str) -> int:
    if not SEMVER.match(new):
        print(f"'{new}' is not MAJOR.MINOR.PATCH", file=sys.stderr)
        return 2
    for path, regex, line in (
        (INIT, INIT_RE, f'__version__ = "{new}"'),
        (PYPROJECT, PYPROJECT_RE, f'version = "{new}"'),
        (CITATION, CITATION_RE, f"version: {new}"),
    ):
        path.write_text(regex.sub(line, path.read_text(encoding="utf-8"), count=1), encoding="utf-8")
    text = CITATION.read_text(encoding="utf-8")
    released = f"date-released: {date.today().isoformat()}\n"
    text = DATE_RE.sub(released, text, count=1) if DATE_RE.search(text) else \
        CITATION_RE.sub(lambda m: m.group(0) + "\n" + released.rstrip("\n"), text, count=1)
    CITATION.write_text(text, encoding="utf-8")
    try:
        subprocess.run(["uv", "lock"], cwd=ROOT, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Run `uv lock` by hand so uv.lock follows the new version.")
    return check()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(check() if sys.argv[1] == "--check" else bump(sys.argv[1]))
