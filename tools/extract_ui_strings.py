"""
Move hard-coded, user-visible English texts in the view layer into
hamelin/i18n/strings.py (as t("key") calls).

Only literals passed to user-facing calls are touched:
  InfoBar.<kind>(title=..., content=...), label / button constructors
  (BodyLabel("..."), PushButton("..."), ...), setText / setToolTip /
  setPlaceholderText / setWindowTitle, attach_help_popup(w, "..."),
  HelpButton("..."), and QFileDialog captions.
f-strings become str.format templates ("{0}", "{1:.2f}" ...). Only calls
inside functions are rewritten (a t() at import time would run before the
language is set). The English text is the source of truth; the Spanish
dictionary gets the same text as a placeholder until it is translated.

Usage:  python tools/extract_ui_strings.py [--write]   (dry run by default)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEW = ROOT / "src" / "hamelin" / "view"
STRINGS = ROOT / "src" / "hamelin" / "i18n" / "strings.py"

PREFIX = {
    "training_page.py": "training", "data_page.py": "data", "forecasting_page.py": "forecasting",
    "metadata_page.py": "metadata", "table1_page.py": "table1", "home_page.py": "home",
    "settings_page.py": "settings", "dashboard_page.py": "dashboard",
    "model_results_widget.py": "common", "kpi_card_widget.py": "common",
    "model_history_widget.py": "common", "rule_builder.py": "common",
    "training_timeline_widget.py": "common", "recruitment_chart_widget.py": "common",
    "help_button.py": "common", "page_help.py": "common",
}
SKIP_FILES = {"help_page.py", "main_window.py", "dashboard_page.py", "settings_page.py"}  # dashboard: hidden + mixed-language texts; settings: author list
TEXT_CTORS = {"BodyLabel", "StrongBodyLabel", "CaptionLabel", "SubtitleLabel", "TitleLabel",
              "PushButton", "PrimaryPushButton", "CheckBox", "RadioButton", "QLabel", "QPushButton",
              "HelpButton", "PageHelpButton", "TransparentPushButton", "HyperlinkButton"}
TEXT_METHODS = {"setText", "setToolTip", "setPlaceholderText", "setWindowTitle", "setTitle"}
INFOBAR = {"info", "success", "warning", "error", "custom"}
FILE_DIALOGS = {"getSaveFileName", "getOpenFileName", "getExistingDirectory", "getOpenFileNames"}


def has_letters(s: str) -> bool:
    return len(re.findall(r"[A-Za-z]{2,}", s)) > 0


def slug(text: str) -> str:
    words = re.findall(r"[a-z0-9]+", text.lower())[:6]
    return "_".join(words)[:40] or "text"


def call_name(node: ast.Call) -> tuple[str, str]:
    f = node.func
    if isinstance(f, ast.Name):
        return "", f.id
    if isinstance(f, ast.Attribute):
        base = f.value.id if isinstance(f.value, ast.Name) else ""
        return base, f.attr
    return "", ""


class Rewriter:
    def __init__(self, path: Path, source: str):
        self.path, self.source = path, source
        self.tree = ast.parse(source)
        self.parents = {}
        for parent in ast.walk(self.tree):
            for child in ast.iter_child_nodes(parent):
                self.parents[child] = parent
        self.line_start = [0]
        for line in source.encode("utf-8").split(b"\n"):
            self.line_start.append(self.line_start[-1] + len(line) + 1)
        self.raw = source.encode("utf-8")
        self.edits: list[tuple[int, int, str, str, str]] = []   # start, end, key, text, replacement-suffix
        self.skipped: list[str] = []

    def in_function(self, node) -> bool:
        while node in self.parents:
            node = self.parents[node]
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                return True
        return False

    def span(self, node) -> tuple[int, int]:
        return (self.line_start[node.lineno - 1] + node.col_offset,
                self.line_start[node.end_lineno - 1] + node.end_col_offset)

    def template(self, node):
        """(template, [arg source, ...]) for a str Constant or simple f-string, else None."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value, []
        if isinstance(node, ast.JoinedStr):
            out, args = [], []
            for part in node.values:
                if isinstance(part, ast.Constant):
                    out.append(part.value.replace("{", "{{").replace("}", "}}"))
                elif isinstance(part, ast.FormattedValue):
                    if part.conversion not in (-1,):
                        return None
                    spec = ""
                    if part.format_spec is not None:
                        if not all(isinstance(v, ast.Constant) for v in part.format_spec.values):
                            return None
                        spec = ":" + "".join(v.value for v in part.format_spec.values)
                    out.append("{" + str(len(args)) + spec + "}")
                    s, e = self.span(part.value)
                    args.append(self.raw[s:e].decode("utf-8"))
                else:
                    return None
            return "".join(out), args
        return None

    def consider(self, node, where: str) -> None:
        if not self.in_function(node):
            return
        tpl = self.template(node)
        if tpl is None:
            if isinstance(node, (ast.JoinedStr, ast.Constant)):
                self.skipped.append(f"{self.path.name}:{node.lineno} complex f-string ({where})")
            return
        text, args = tpl
        if not has_letters(re.sub(r"\{[^}]*\}", "", text)):
            return
        s, e = self.span(node)
        self.edits.append((s, e, text, "", ", ".join(args)))

    def collect(self) -> None:
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            base, name = call_name(node)
            if base == "InfoBar" and name in INFOBAR:
                for kw in node.keywords:
                    if kw.arg in ("title", "content"):
                        self.consider(kw.value, f"InfoBar.{kw.arg}")
            elif name in TEXT_CTORS and node.args:
                self.consider(node.args[0], name)
            elif name in TEXT_METHODS and node.args:
                self.consider(node.args[0], name)
            elif name in ("attach_help_popup", "attach_help_popup_hover") and len(node.args) >= 2:
                self.consider(node.args[1], name)
            elif name in FILE_DIALOGS:
                for idx in (1, 3):
                    if len(node.args) > idx:
                        self.consider(node.args[idx], f"{name}[{idx}]")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    existing_en = {}
    ns: dict = {}
    exec(compile(STRINGS.read_text(encoding="utf-8"), str(STRINGS), "exec"), ns)
    text_to_key = {}
    used_keys = set(ns["EN"])
    new_entries: dict[str, str] = {}
    total = 0
    for path in sorted(VIEW.rglob("*.py")):
        if path.name in SKIP_FILES or path.name.startswith("eval_") or path.name in ("evaluation_page.py", "prediction_page.py", "config_dialog.py", "__init__.py"):
            continue
        prefix = PREFIX.get(path.name)
        if prefix is None:
            print(f"# no prefix mapping, skipped: {path.name}")
            continue
        src = path.read_text(encoding="utf-8")
        rw = Rewriter(path, src)
        rw.collect()
        if not rw.edits and not rw.skipped:
            continue
        raw = rw.raw
        out = raw
        for s, e, text, _, argstr in sorted(rw.edits, reverse=True):
            key = text_to_key.get(text)
            if key is None:
                base = f"{prefix}.txt.{slug(text)}"
                key, n = base, 2
                while key in used_keys:
                    key, n = f"{base}_{n}", n + 1
                used_keys.add(key)
                text_to_key[text] = key
                new_entries[key] = text
            call = f't("{key}")' + (f".format({argstr})" if argstr else "")
            out = out[:s] + call.encode("utf-8") + out[e:]
        new_src = out.decode("utf-8")
        if rw.edits and not re.search(r"^from hamelin\.i18n import .*\bt\b", new_src, re.M):
            new_src = re.sub(r"^(from hamelin\.utils\.logger import log\n)", r"\1from hamelin.i18n import t\n", new_src, count=1, flags=re.M) \
                if "from hamelin.utils.logger import log\n" in new_src else "from hamelin.i18n import t\n" + new_src
        total += len(rw.edits)
        print(f"{path.relative_to(ROOT)}: {len(rw.edits)} texts" + (f", {len(rw.skipped)} skipped" if rw.skipped else ""))
        for s_ in rw.skipped:
            print("    skipped:", s_)
        if args.write and rw.edits:
            path.write_text(new_src, encoding="utf-8")

    print(f"total: {total} call sites, {len(new_entries)} distinct texts")
    if args.write and new_entries:
        lines = STRINGS.read_text(encoding="utf-8").split("\n")
        starts = [i for i, l in enumerate(lines) if re.match(r"^(EN|ES)\b.*= \{", l)]
        ends = [i for i, l in enumerate(lines) if l == "}"]
        def kv(k, v):
            return f"    {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},"
        for (a, b), label in reversed(list(zip(zip(starts, ends), ("EN", "ES")))):
            body = lines[a:b]
            while body and body[-1].strip() == "":
                body.pop()
            body.append("")
            body.append("    # Texts moved out of the view code" + (" (English)" if label == "EN" else " - English placeholders, Spanish pending"))
            body += [kv(k, v) for k, v in new_entries.items()]
            lines[a:b] = body
        STRINGS.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
