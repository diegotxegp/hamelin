"""
Test Suite for RecruitmentChart

Tests cover:
  - Happy path: >= 5 events → full figure with all chart elements
  - Insufficient data: < 3 events → empty figure with explanatory message
  - Forecast unavailable: 3–4 events → forecast raises ValidationError → empty figure
  - Save: writes PNG/SVG to disk; auto-builds if build() not called first
  - Static helper: _build_empty_figure returns a valid Figure for any message

Author: GitHub Copilot AI
Date: February 20, 2026
Sprint: 2, Day 14
"""

import pytest
from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # ensure non-interactive backend in tests
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from hamelin.analytics.forecasting_chart import RecruitmentChart
from hamelin.analytics.recruitment_tracker import RecruitmentTracker
from hamelin.core.project import ProjectMetadata


# ============================================================================
# Session-level setup
# ============================================================================

@pytest.fixture(autouse=True)
def close_matplotlib_figures():
    """Close all matplotlib figures after every test to prevent memory warnings."""
    yield
    plt.close("all")


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def valid_project():
    """Project with target_sample_size=100."""
    return ProjectMetadata(
        name="Test Study",
        short_name="TS",
        protocol_number="PROTO-2024-001",
        target_sample_size=100,
        first_patient_date=date(2024, 1, 1),
        principal_investigator="Dr. Test",
        contact_email="test@example.com",
        institution="Test Hospital",
    )


def _make_tracker(project: ProjectMetadata, n_events: int) -> RecruitmentTracker:
    """Helper: create a tracker with *n_events* events spaced 7 days apart."""
    tracker = RecruitmentTracker(project)
    base = date(2024, 1, 7)
    for i in range(n_events):
        tracker.add_event(f"P{i+1:03d}", base + timedelta(days=i * 7))
    return tracker


@pytest.fixture
def tracker_0(valid_project):
    return _make_tracker(valid_project, 0)


@pytest.fixture
def tracker_2(valid_project):
    return _make_tracker(valid_project, 2)


@pytest.fixture
def tracker_4(valid_project):
    """4 events: passes the ≥3 chart guard but forecast_completion needs ≥5."""
    return _make_tracker(valid_project, 4)


@pytest.fixture
def tracker_10(valid_project):
    """10 events spread over ~10 weeks → full happy-path chart."""
    return _make_tracker(valid_project, 10)


# ============================================================================
# TestRecruitmentChartInit
# ============================================================================

class TestRecruitmentChartInit:
    """Chart stores its constructor arguments correctly."""

    def test_stores_tracker(self, tracker_10, valid_project):
        chart = RecruitmentChart(tracker_10, target=100)
        assert chart._tracker is tracker_10

    def test_stores_target(self, tracker_10):
        chart = RecruitmentChart(tracker_10, target=75)
        assert chart._target == 75

    def test_figure_none_before_build(self, tracker_10):
        chart = RecruitmentChart(tracker_10, target=100)
        assert chart._fig is None


# ============================================================================
# TestRecruitmentChartHappyPath
# ============================================================================

class TestRecruitmentChartHappyPath:
    """With >=5 events build() returns a fully populated figure."""

    def test_build_returns_figure(self, tracker_10):
        chart = RecruitmentChart(tracker_10, target=100)
        fig = chart.build()
        assert isinstance(fig, Figure)

    def test_figure_stored_after_build(self, tracker_10):
        chart = RecruitmentChart(tracker_10, target=100)
        fig = chart.build()
        assert chart._fig is fig

    def test_figure_has_axes(self, tracker_10):
        chart = RecruitmentChart(tracker_10, target=100)
        fig = chart.build()
        assert len(fig.get_axes()) == 1

    def test_axes_has_lines(self, tracker_10):
        """Historical line + trend dashed line → at least 2 Line2D artists."""
        chart = RecruitmentChart(tracker_10, target=100)
        fig = chart.build()
        ax = fig.get_axes()[0]
        assert len(ax.get_lines()) >= 2

    def test_axes_has_legend(self, tracker_10):
        chart = RecruitmentChart(tracker_10, target=100)
        fig = chart.build()
        ax = fig.get_axes()[0]
        assert ax.get_legend() is not None

    def test_axes_ylabel_set(self, tracker_10):
        chart = RecruitmentChart(tracker_10, target=100)
        fig = chart.build()
        ax = fig.get_axes()[0]
        assert "Patient" in ax.get_ylabel()

    def test_axes_title_set(self, tracker_10):
        chart = RecruitmentChart(tracker_10, target=100)
        fig = chart.build()
        ax = fig.get_axes()[0]
        assert ax.get_title() != ""

    def test_build_idempotent(self, tracker_10):
        """Calling build() twice returns consistent figures, no exception."""
        chart = RecruitmentChart(tracker_10, target=100)
        fig1 = chart.build()
        fig2 = chart.build()
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


# ============================================================================
# TestRecruitmentChartInsufficientData
# ============================================================================

class TestRecruitmentChartInsufficientData:
    """< 3 events → empty figure, no exception raised."""

    def test_zero_events_returns_figure(self, tracker_0):
        chart = RecruitmentChart(tracker_0, target=100)
        fig = chart.build()
        assert isinstance(fig, Figure)

    def test_two_events_returns_figure(self, tracker_2):
        chart = RecruitmentChart(tracker_2, target=100)
        fig = chart.build()
        assert isinstance(fig, Figure)

    def test_empty_figure_has_no_legend(self, tracker_2):
        """Empty/error figures do not have a legend."""
        chart = RecruitmentChart(tracker_2, target=100)
        fig = chart.build()
        ax = fig.get_axes()[0]
        # Empty figure has axes hidden; legend is None or has 0 handles
        legend = ax.get_legend()
        assert legend is None or len(legend.get_texts()) == 0

    def test_empty_figure_axes_are_off(self, tracker_2):
        """Empty figure: axes visibility is off."""
        chart = RecruitmentChart(tracker_2, target=100)
        fig = chart.build()
        ax = fig.get_axes()[0]
        assert not ax.axison


# ============================================================================
# TestRecruitmentChartForecastUnavailable
# ============================================================================

class TestRecruitmentChartForecastUnavailable:
    """3–4 events: passes chart guard (≥3) but forecast_completion raises
    ValidationError (needs ≥5). Chart must silently return an empty figure."""

    def test_four_events_returns_figure(self, tracker_4):
        chart = RecruitmentChart(tracker_4, target=100)
        fig = chart.build()
        assert isinstance(fig, Figure)

    def test_four_events_no_exception(self, tracker_4):
        chart = RecruitmentChart(tracker_4, target=100)
        # Must not raise
        try:
            chart.build()
        except Exception as exc:
            pytest.fail(f"build() raised unexpectedly: {exc}")

    def test_four_events_empty_figure_has_no_lines(self, tracker_4):
        chart = RecruitmentChart(tracker_4, target=100)
        fig = chart.build()
        ax = fig.get_axes()[0]
        # Error figure axes are off → no plotted lines
        assert len(ax.get_lines()) == 0


# ============================================================================
# TestRecruitmentChartSave
# ============================================================================

class TestRecruitmentChartSave:
    """save() writes a valid image file to disk."""

    def test_save_png_creates_file(self, tracker_10, tmp_path):
        path = tmp_path / "forecast.png"
        chart = RecruitmentChart(tracker_10, target=100)
        chart.build()
        chart.save(str(path))
        assert path.exists()
        assert path.stat().st_size > 0

    def test_save_svg_creates_file(self, tracker_10, tmp_path):
        path = tmp_path / "forecast.svg"
        chart = RecruitmentChart(tracker_10, target=100)
        chart.build()
        chart.save(str(path))
        assert path.exists()
        assert path.stat().st_size > 0

    def test_save_without_prior_build_creates_file(self, tracker_10, tmp_path):
        """save() must call build() automatically if _fig is None."""
        path = tmp_path / "forecast_auto.png"
        chart = RecruitmentChart(tracker_10, target=100)
        chart.save(str(path))  # no explicit build()
        assert path.exists()
        assert path.stat().st_size > 0

    def test_save_custom_dpi(self, tracker_10, tmp_path):
        """save() accepts a custom dpi without error."""
        path = tmp_path / "hires.png"
        chart = RecruitmentChart(tracker_10, target=100)
        chart.build()
        chart.save(str(path), dpi=150)
        assert path.exists()


# ============================================================================
# TestBuildEmptyFigure
# ============================================================================

class TestBuildEmptyFigure:
    """Static helper returns a valid Figure for any message string."""

    def test_returns_figure(self):
        fig = RecruitmentChart._build_empty_figure("Test message")
        assert isinstance(fig, Figure)

    def test_has_one_axes(self):
        fig = RecruitmentChart._build_empty_figure("No data")
        assert len(fig.get_axes()) == 1

    def test_axes_are_off(self):
        fig = RecruitmentChart._build_empty_figure("No data")
        ax = fig.get_axes()[0]
        assert not ax.axison

    def test_empty_string_message(self):
        """Empty message string must not raise."""
        fig = RecruitmentChart._build_empty_figure("")
        assert isinstance(fig, Figure)

    def test_long_message(self):
        msg = "Line 1\nLine 2\nLine 3\nLine 4"
        fig = RecruitmentChart._build_empty_figure(msg)
        assert isinstance(fig, Figure)
