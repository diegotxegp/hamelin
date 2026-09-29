"""Every t("key") in the code base exists, and every t("key").format(...)
call passes the arguments its template needs."""
import ast
import string
from pathlib import Path

from hamelin.i18n.strings import EN, ES

SRC = Path(__file__).resolve().parent.parent / "src" / "hamelin"


def _t_calls():
    for path in SRC.rglob("*.py"):
        if "interface" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "t"
                    and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                yield path, node


def test_every_key_used_in_code_exists():
    # keys that predate this test and were never defined (the preset buttons
    # fall back to the key itself); listed so a new missing key is caught
    known_missing = {"training.btn.save_preset", "training.btn.reset_preset"}
    missing = sorted({(p.name, n.args[0].value) for p, n in _t_calls()
                      if n.args[0].value not in EN and n.args[0].value not in known_missing})
    assert not missing, missing


def test_format_calls_pass_enough_arguments():
    problems = []
    parents = {}
    for path in SRC.rglob("*.py"):
        if "interface" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format"
                    and isinstance(node.func.value, ast.Call) and isinstance(node.func.value.func, ast.Name)
                    and node.func.value.func.id == "t" and node.func.value.args
                    and isinstance(node.func.value.args[0], ast.Constant)):
                key = node.func.value.args[0].value
                for lang in (EN, ES):
                    template = lang.get(key)
                    if template is None:
                        continue
                    fields = [f for _, f, _, _ in string.Formatter().parse(template) if f is not None]
                    positional = {int(f) for f in fields if f.isdigit()}
                    named = {f.split(".")[0].split("[")[0] for f in fields if f and not f[0].isdigit()}
                    kw = {k.arg for k in node.keywords if k.arg}
                    if positional and max(positional) >= len(node.args):
                        problems.append((path.name, key, "positional", positional, len(node.args)))
                    if named - kw:
                        problems.append((path.name, key, "named", named - kw))
    assert not problems, problems
