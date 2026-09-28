"""
Results Visualizer — Unit Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests for ``build_confusion_matrix_fig`` and ``build_roc_fig``.

All tests are pure-backend (no PySide6 / Qt event loop required).
Matplotlib figures are inspected structurally — axes, collections,
line counts, text annotations — without rendering to screen.

Author: GitHub Copilot AI
Date: February 24, 2026
Sprint: 3, Day 29
"""

from __future__ import annotations

import pytest
from matplotlib.figure import Figure

from hamelin.analytics.results_visualizer import (
    build_confusion_matrix_fig,
    build_roc_fig,
    _placeholder_fig,
    _validate_cm,
    _validate_roc,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def binary_cm() -> list[list[int]]:
    """2×2 confusion matrix: [[TN, FP], [FN, TP]]"""
    return [[50, 5], [8, 37]]


@pytest.fixture
def binary_labels() -> list[str]:
    return ["Negativo", "Positivo"]


@pytest.fixture
def multiclass_cm() -> list[list[int]]:
    """3×3 confusion matrix."""
    return [[30, 2, 1], [3, 25, 2], [1, 1, 20]]


@pytest.fixture
def roc_data() -> tuple[list[float], list[float], float]:
    fpr = [0.0, 0.1, 0.2, 0.4, 0.6, 1.0]
    tpr = [0.0, 0.5, 0.7, 0.85, 0.9, 1.0]
    auc = 0.872
    return fpr, tpr, auc


# ============================================================================
# _validate_cm (private helper)
# ============================================================================

class TestValidateCm:
    def test_valid_2x2_returns_array_and_labels(self, binary_cm, binary_labels):
        result = _validate_cm(binary_cm, binary_labels)
        assert result is not None
        arr, lbls = result
        assert arr.shape == (2, 2)
        assert lbls == binary_labels

    def test_valid_3x3_no_labels_generates_defaults(self, multiclass_cm):
        result = _validate_cm(multiclass_cm, [])
        assert result is not None
        arr, lbls = result
        assert arr.shape == (3, 3)
        assert lbls == ["0", "1", "2"]

    def test_non_square_returns_none(self):
        assert _validate_cm([[1, 2, 3], [4, 5, 6]], []) is None

    def test_empty_returns_none(self):
        assert _validate_cm([], []) is None

    def test_wrong_label_length_autofixes(self, binary_cm):
        result = _validate_cm(binary_cm, ["only_one"])
        assert result is not None
        _, lbls = result
        assert len(lbls) == 2  # auto-generated

    def test_invalid_input_returns_none(self):
        assert _validate_cm("not a list", []) is None  # type: ignore[arg-type]


# ============================================================================
# _validate_roc (private helper)
# ============================================================================

class TestValidateRoc:
    def test_valid_returns_arrays(self, roc_data):
        fpr, tpr, _ = roc_data
        result = _validate_roc(fpr, tpr)
        assert result is not None
        f, t = result
        assert len(f) == len(fpr)
        assert len(t) == len(tpr)

    def test_mismatched_lengths_returns_none(self):
        assert _validate_roc([0.0, 0.5, 1.0], [0.0, 1.0]) is None

    def test_single_point_returns_none(self):
        assert _validate_roc([0.0], [0.0]) is None

    def test_empty_returns_none(self):
        assert _validate_roc([], []) is None

    def test_invalid_input_returns_none(self):
        assert _validate_roc("bad", []) is None  # type: ignore[arg-type]


# ============================================================================
# build_confusion_matrix_fig
# ============================================================================

class TestBuildConfusionMatrixFig:
    def test_returns_figure(self, binary_cm, binary_labels):
        fig = build_confusion_matrix_fig(binary_cm, binary_labels)
        assert isinstance(fig, Figure)

    def test_has_one_axis(self, binary_cm, binary_labels):
        fig = build_confusion_matrix_fig(binary_cm, binary_labels)
        assert len(fig.axes) == 1

    def test_axis_has_image(self, binary_cm, binary_labels):
        """The heatmap must add at least one AxesImage."""
        ax = build_confusion_matrix_fig(binary_cm, binary_labels).axes[0]
        assert len(ax.images) >= 1

    def test_custom_title(self, binary_cm):
        fig = build_confusion_matrix_fig(binary_cm, title="Mi Matriz")
        ax = fig.axes[0]
        assert "Mi Matriz" in ax.get_title()

    def test_default_title(self, binary_cm):
        fig = build_confusion_matrix_fig(binary_cm)
        assert "Confusion" in fig.axes[0].get_title()

    def test_x_axis_label_clinical(self, binary_cm, binary_labels):
        ax = build_confusion_matrix_fig(binary_cm, binary_labels).axes[0]
        assert "prediction" in ax.get_xlabel().lower()

    def test_y_axis_label_clinical(self, binary_cm, binary_labels):
        ax = build_confusion_matrix_fig(binary_cm, binary_labels).axes[0]
        assert "diagnosis" in ax.get_ylabel().lower() or "actual" in ax.get_ylabel().lower()

    def test_tick_labels_match_class_labels(self, binary_cm, binary_labels):
        ax = build_confusion_matrix_fig(binary_cm, binary_labels).axes[0]
        x_lbls = [t.get_text() for t in ax.get_xticklabels()]
        y_lbls = [t.get_text() for t in ax.get_yticklabels()]
        assert "Negativo" in x_lbls
        assert "Positivo" in x_lbls
        assert "Negativo" in y_lbls

    def test_cell_annotations_present(self, binary_cm, binary_labels):
        """Each cell produces a text annotation (count + %)."""
        ax = build_confusion_matrix_fig(binary_cm, binary_labels).axes[0]
        # 2×2 → 4 annotations minimum
        texts = [t for t in ax.texts]
        assert len(texts) >= 4

    def test_multiclass_works(self, multiclass_cm):
        fig = build_confusion_matrix_fig(multiclass_cm)
        assert isinstance(fig, Figure)
        assert len(fig.axes[0].images) >= 1

    def test_empty_cm_returns_placeholder(self):
        fig = build_confusion_matrix_fig([])
        assert isinstance(fig, Figure)
        # placeholder has no AxesImage
        assert len(fig.axes[0].images) == 0

    def test_non_square_returns_placeholder(self):
        fig = build_confusion_matrix_fig([[1, 2, 3], [4, 5, 6]])
        assert isinstance(fig, Figure)
        assert len(fig.axes[0].images) == 0

    def test_no_labels_auto_generates(self, binary_cm):
        fig = build_confusion_matrix_fig(binary_cm, labels=None)
        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        tick_texts = [t.get_text() for t in ax.get_xticklabels()]
        # auto-generated labels are "0" and "1"
        assert "0" in tick_texts or "1" in tick_texts


# ============================================================================
# build_roc_fig
# ============================================================================

class TestBuildRocFig:
    def test_returns_figure(self, roc_data):
        fpr, tpr, auc = roc_data
        fig = build_roc_fig(fpr, tpr, auc)
        assert isinstance(fig, Figure)

    def test_has_one_axis(self, roc_data):
        fpr, tpr, auc = roc_data
        fig = build_roc_fig(fpr, tpr, auc)
        assert len(fig.axes) == 1

    def test_has_two_lines(self, roc_data):
        """ROC curve + reference diagonal = 2 lines."""
        fpr, tpr, auc = roc_data
        ax = build_roc_fig(fpr, tpr, auc).axes[0]
        assert len(ax.lines) == 2

    def test_auc_in_legend(self, roc_data):
        fpr, tpr, auc = roc_data
        ax = build_roc_fig(fpr, tpr, auc).axes[0]
        legend_texts = [t.get_text() for t in ax.get_legend().get_texts()]
        assert any("AUC" in t for t in legend_texts)

    def test_no_auc_still_works(self, roc_data):
        fpr, tpr, _ = roc_data
        fig = build_roc_fig(fpr, tpr, auc=None)
        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        assert len(ax.lines) == 2

    def test_custom_title(self, roc_data):
        fpr, tpr, auc = roc_data
        fig = build_roc_fig(fpr, tpr, auc, title="Curva personalizada")
        assert "personalizada" in fig.axes[0].get_title()

    def test_default_title(self, roc_data):
        fpr, tpr, _ = roc_data
        fig = build_roc_fig(fpr, tpr)
        assert "ROC" in fig.axes[0].get_title()

    def test_x_axis_label_clinical(self, roc_data):
        fpr, tpr, _ = roc_data
        ax = build_roc_fig(fpr, tpr).axes[0]
        assert "specificity" in ax.get_xlabel().lower() or "false" in ax.get_xlabel().lower()

    def test_y_axis_label_clinical(self, roc_data):
        fpr, tpr, _ = roc_data
        ax = build_roc_fig(fpr, tpr).axes[0]
        assert "sensitivity" in ax.get_ylabel().lower() or "true" in ax.get_ylabel().lower()

    def test_legend_has_reference_line(self, roc_data):
        fpr, tpr, auc = roc_data
        ax = build_roc_fig(fpr, tpr, auc).axes[0]
        legend_texts = [t.get_text() for t in ax.get_legend().get_texts()]
        assert any("chance" in t.lower() for t in legend_texts)

    def test_mismatched_arrays_return_placeholder(self):
        fig = build_roc_fig([0.0, 0.5], [0.0])
        assert isinstance(fig, Figure)
        assert len(fig.axes[0].lines) == 0

    def test_empty_arrays_return_placeholder(self):
        fig = build_roc_fig([], [])
        assert isinstance(fig, Figure)
        assert len(fig.axes[0].lines) == 0

    def test_auc_value_in_legend_text(self, roc_data):
        fpr, tpr, auc = roc_data
        ax = build_roc_fig(fpr, tpr, auc).axes[0]
        legend_texts = " ".join(t.get_text() for t in ax.get_legend().get_texts())
        assert "0.872" in legend_texts


# ============================================================================
# _placeholder_fig (shared helper)
# ============================================================================

class TestPlaceholderFig:
    def test_returns_figure(self):
        assert isinstance(_placeholder_fig("Test"), Figure)

    def test_single_axis_no_images(self):
        fig = _placeholder_fig("Test")
        ax = fig.axes[0]
        assert len(ax.images) == 0
        assert len(ax.lines) == 0

    def test_title_text_present(self):
        fig = _placeholder_fig("MiPlaceholder")
        texts = [t.get_text() for t in fig.axes[0].texts]
        assert any("MiPlaceholder" in t for t in texts)

    def test_note_appended(self):
        fig = _placeholder_fig("Título", note="sin datos")
        texts = [t.get_text() for t in fig.axes[0].texts]
        assert any("sin datos" in t for t in texts)
