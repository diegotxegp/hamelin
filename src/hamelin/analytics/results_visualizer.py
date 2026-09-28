"""
Results Visualizer — HAMELIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pure-matplotlib functions that generate ``Figure`` objects for model
evaluation results.  No PySide6 dependency — callers wrap the returned
``Figure`` in a ``FigureCanvasQTAgg`` widget as needed.

Design philosophy (HGML / Gil et al. 2019)
-------------------------------------------
Every visualisation is built for a **clinical researcher who is not an ML
expert**.  Concretely:

* Labels are in plain English, avoiding ML jargon.
* Confusion-matrix cells are annotated with counts *and* percentages.
* A diagonal dashed reference line is drawn on the ROC plot so the
  clinician can instantly see whether the model is better than chance.
* Colour choices are neutral and accessible (no red/green alone).
* Axis titles explain what the axis *means* clinically.

All functions follow the same contract
---------------------------------------
    - Accept plain Python lists / floats (JSON-serialisable).
    - Return a ``matplotlib.figure.Figure``.
    - Never raise on bad input — return a labelled placeholder figure
      instead so the UI always has something sensible to show.

Author: GitHub Copilot AI
Date: February 24, 2026
Sprint: 3, Day 29
"""

from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure
from matplotlib import colormaps

from hamelin.utils.logger import log
# hamelin.utils.theme_colors, not hamelin.view.widgets.theme_colors - this module
# is deliberately free of any PySide6/hamelin.view dependency (see the module
# docstring above), and importing anything under hamelin.view here would
# circularly import back into the widgets that import this module.
from hamelin.utils.theme_colors import colors, style_figure


# ── Colour constants ──────────────────────────────────────────────────────────
# _BLUE/_GREY are data/text accents, not backgrounds - left as fixed
# accessible colours; figure/axes background and axis text/spine colour
# come from theme_colors.colors() via style_figure() instead (see below).

_BLUE   = "#3498db"   # primary accent
_GREY   = "#9CA3AF"   # placeholder / secondary text


# ── Private helpers ───────────────────────────────────────────────────────────

def _placeholder_fig(title: str, note: str = "") -> Figure:
    """Return a minimal placeholder Figure with *title* centred."""
    c = colors()
    fig = Figure(figsize=(7, 3))
    fig.patch.set_facecolor(c.chart_face)
    ax = fig.add_subplot(111)
    ax.axis("off")
    message = title if not note else f"{title}\n{note}"
    ax.text(
        0.5, 0.5, message,
        ha="center", va="center", transform=ax.transAxes,
        fontsize=10, color=c.text_secondary,
    )
    return fig


def _validate_cm(
    cm: list[list[int]],
    labels: list[str],
) -> tuple[np.ndarray, list[str]] | None:
    """
    Validate and normalise confusion-matrix inputs.

    Returns (cm_array, labels) or None on invalid input.
    """
    try:
        arr = np.array(cm, dtype=float)
        if arr.ndim != 2 or arr.shape[0] != arr.shape[1] or arr.shape[0] == 0:
            return None
        n = arr.shape[0]
        if not labels:
            labels = [str(i) for i in range(n)]
        elif len(labels) != n:
            labels = [str(i) for i in range(n)]
        return arr, list(labels)
    except Exception:
        return None


def _validate_roc(
    fpr: list[float],
    tpr: list[float],
) -> tuple[np.ndarray, np.ndarray] | None:
    """Validate ROC curve arrays.  Returns (fpr, tpr) arrays or None."""
    try:
        f = np.asarray(fpr, dtype=float)
        t = np.asarray(tpr, dtype=float)
        if f.ndim != 1 or t.ndim != 1 or len(f) != len(t) or len(f) < 2:
            return None
        return f, t
    except Exception:
        return None


# ── Public API ────────────────────────────────────────────────────────────────

def build_confusion_matrix_fig(
    cm: list[list[int]],
    labels: list[str] | None = None,
    title: str = "Confusion Matrix",
) -> Figure:
    """
    Build a confusion-matrix heatmap annotated for clinical interpretation.

    Each cell shows:
        * Absolute count (large, bold)
        * Percentage of the total (small, grey)

    The diagonal (correct predictions) uses a lighter shade; off-diagonal
    (errors) a darker shade so errors are visually salient without relying
    on red-only colour coding.

    Parameters
    ----------
    cm:
        Square list-of-lists of integer counts, row = true class,
        col = predicted class.  Example: ``[[50, 5], [8, 37]]``.
    labels:
        Class label strings.  Length must match ``cm`` dimension.
        Defaults to ``["0", "1", …]``.
    title:
        Figure title shown above the matrix.

    Returns
    -------
    matplotlib.figure.Figure

    Notes
    -----
    Returns a placeholder figure (no exception raised) if *cm* is empty,
    non-square, or otherwise invalid.
    """
    validated = _validate_cm(cm, labels or [])
    if validated is None:
        log.warning("build_confusion_matrix_fig: invalid cm — returning placeholder")
        return _placeholder_fig(
            title,
            "(confusion matrix data not available)",
        )

    arr, lbls = validated
    n = arr.shape[0]
    total = arr.sum()

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    # ── Heatmap ──────────────────────────────────────────────────────
    cmap = colormaps.get_cmap("Blues")
    im = ax.imshow(arr, interpolation="nearest", cmap=cmap)

    # ── Cell annotations ─────────────────────────────────────────────
    thresh = arr.max() / 2.0
    for i in range(n):
        for j in range(n):
            count = int(arr[i, j])
            pct = arr[i, j] / total * 100 if total > 0 else 0.0
            colour = "white" if arr[i, j] > thresh else "#1a1a2e"
            ax.text(
                j, i,
                f"{count}\n({pct:.1f}%)",
                ha="center", va="center",
                fontsize=10, color=colour,
                fontweight="bold" if i == j else "normal",
            )

    # ── Axes decoration ──────────────────────────────────────────────
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(lbls, fontsize=9)
    ax.set_yticklabels(lbls, fontsize=9)
    ax.set_xlabel("Model prediction", fontsize=10, labelpad=8)
    ax.set_ylabel("Actual diagnosis", fontsize=10, labelpad=8)
    ax.set_title(title, fontsize=11, pad=12, fontweight="bold")

    style_figure(fig, ax)
    fig.tight_layout(pad=1.5)
    log.debug(f"build_confusion_matrix_fig: built {n}×{n} matrix")
    return fig


def build_roc_fig(
    fpr: list[float],
    tpr: list[float],
    auc: float | None = None,
    title: str = "ROC Curve",
) -> Figure:
    """
    Build a ROC curve figure with a reference diagonal and AUC annotation.

    Clinical framing
    ----------------
    * X axis: "False Positive Rate (1 − Specificity)"
    * Y axis: "Sensitivity (True Positive Rate)"
    * The dashed diagonal represents "random chance" so the clinician
      can intuitively grasp whether the model adds value.
    * AUC is shown in the legend in plain language when provided.

    Parameters
    ----------
    fpr:
        False-positive rates (x-axis), typically from scikit-learn or
        Ludwig's ``roc_curve`` output.
    tpr:
        True-positive rates (y-axis), same length as *fpr*.
    auc:
        Scalar AUC value (0–1).  If provided, appears in the legend.
    title:
        Figure title.

    Returns
    -------
    matplotlib.figure.Figure

    Notes
    -----
    Returns a placeholder figure on invalid input with no exception raised.
    """
    validated = _validate_roc(fpr, tpr)
    if validated is None:
        log.warning("build_roc_fig: invalid ROC data — returning placeholder")
        return _placeholder_fig(
            title,
            "(ROC curve data not available)",
        )

    f_arr, t_arr = validated

    auc_label = ""
    if auc is not None:
        auc_label = f"  (AUC = {auc:.3f})"

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    # ── ROC curve ────────────────────────────────────────────────────
    ax.plot(
        f_arr, t_arr,
        color=_BLUE, linewidth=2,
        label=f"Model{auc_label}",
    )

    # ── Reference diagonal ("random chance") ──────────────────────────────────────────────
    ax.plot(
        [0, 1], [0, 1],
        color=_GREY, linewidth=1, linestyle="--",
        label="Random chance",
    )

    # ── Axes decoration ──────────────────────────────────────────────
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel(
        "False Positive Rate  (1 − Specificity)",
        fontsize=9, labelpad=8,
    )
    ax.set_ylabel(
        "Sensitivity  (True Positive Rate)",
        fontsize=9, labelpad=8,
    )
    ax.set_title(title, fontsize=11, pad=12, fontweight="bold")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)

    style_figure(fig, ax)
    fig.tight_layout(pad=1.5)
    log.debug("build_roc_fig: ROC figure built")
    return fig
