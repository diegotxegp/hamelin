"""List Spanish UI texts that are still the English placeholder (ES == EN)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from hamelin.i18n.strings import EN, ES  # noqa: E402

SAME_OK = re.compile(r"^[^A-Za-z]*$")  # numbers / symbols / units need no translation
pending = [k for k, v in EN.items() if ES.get(k) == v and not SAME_OK.match(v)]
for k in pending:
    print(f"{k}: {EN[k][:90]!r}")
print(f"\n{len(pending)} of {len(EN)} texts still need a Spanish translation", file=sys.stderr)
