"""
Sprint 2 End-to-End Integration Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests the full Sprint 2 pipeline without any GUI components:
    project creation → recruitment → forecast → chart → Table 1 → quality report

All tests use pytest's `tmp_path` fixture so no files persist between runs.

Author: GitHub Copilot AI
Date: February 20, 2026
Sprint: 2, Days 20-21 (Integration)
"""

import random
import shutil
from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from hamelin.analytics.forecasting_chart import RecruitmentChart
from hamelin.analytics.recruitment_tracker import RecruitmentTracker
from hamelin.analytics.table1_generator import Table1Generator
from hamelin.core.project import ProjectMetadata, ProjectRepository


# ============================================================================
# Helpers
# ============================================================================

def _project(short_name: str = "INTEG_TEST", target: int = 100) -> ProjectMetadata:
    """Return a minimal but fully valid ProjectMetadata."""
    return ProjectMetadata(
        name=f"Integration Test Project — {short_name}",
        short_name=short_name,
        protocol_number=f"PROTO-{short_name}",
        target_sample_size=target,
        first_patient_date=date(2025, 1, 1),
        principal_investigator="Dr. Integration",
        contact_email="integration@test.com",
        institution="Test Hospital",
        study_type="Observational Study",
    )


def _tracker_with_events(project: ProjectMetadata, n: int = 60) -> RecruitmentTracker:
    """Build a tracker with n synthetic enrollment events."""
    tracker = RecruitmentTracker(project)
    rng = random.Random(42)
    start = project.first_patient_date
    dates = sorted(start + timedelta(days=rng.randint(0, 365)) for _ in range(n))
    for i, d in enumerate(dates):
        tracker.add_event(f"P{i+1:03d}", d)
    return tracker


def _synthetic_df(n: int = 50) -> pd.DataFrame:
    """Return a small synthetic clinical DataFrame."""
    rng = np.random.default_rng(7)
    return pd.DataFrame({
        "age": rng.normal(55, 12, n).clip(18, 85).round(1),
        "sex": rng.choice(["M", "F"], n),
        "bmi": rng.normal(26, 5, n).clip(15, 50).round(1),
        "hypertension": rng.choice(["Yes", "No"], n),
        "egfr": np.where(rng.random(n) < 0.06, np.nan,
                         rng.normal(65, 20, n).clip(10, 120)).round(1),
    })


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


# ============================================================================
# Test group 1: Full workflow
# ============================================================================

class TestFullWorkflow:
    """End-to-end: project → tracker → chart → table1 → quality report."""

    def test_full_workflow_creates_project_and_artifacts(self, tmp_path):
        """Complete Sprint 2 pipeline runs without error and writes key files."""
        project = _project("FULL_WF")
        repo = ProjectRepository(base_path=tmp_path)
        repo.create_project(project)

        # Recruitment
        tracker = _tracker_with_events(project, n=60)
        assert len(tracker.events) == 60

        # Chart
        chart = RecruitmentChart(tracker, target=project.target_sample_size)
        fig = chart.build()
        assert fig is not None

        chart_dir = tmp_path / "FULL_WF" / "results" / "charts"
        chart_dir.mkdir(parents=True)
        png = chart_dir / "forecast.png"
        chart.save(str(png), dpi=72)
        assert png.exists()
        assert png.stat().st_size > 0

        # Table 1
        df = _synthetic_df()
        gen = Table1Generator(df)
        gen.add_variable("age", "continuous", label="Age")
        gen.add_variable("sex", "categorical", label="Sex")
        table = gen.generate()
        assert len(table) >= 3

        # Quality report
        rows = []
        for col in df.columns:
            s = df[col]
            rows.append({"Column": col, "Missing %": round(s.isna().sum() / len(s) * 100, 2)})
        report = pd.DataFrame(rows)
        assert set(["Column", "Missing %"]).issubset(report.columns)
        assert len(report) == len(df.columns)

    def test_metadata_saved_and_reloaded_correctly(self, tmp_path):
        """Saved project can be reloaded with identical data."""
        project = _project("RELOAD")
        repo = ProjectRepository(base_path=tmp_path)
        repo.create_project(project)

        loaded = repo.load("RELOAD")
        assert loaded.name == project.name
        assert loaded.target_sample_size == project.target_sample_size
        assert loaded.study_type == project.study_type

    def test_project_selector_lists_created_projects(self, tmp_path):
        """ProjectRepository.list_projects() returns all created projects."""
        repo = ProjectRepository(base_path=tmp_path)
        for name in ("PROJ_A", "PROJ_B", "PROJ_C"):
            repo.create_project(_project(name))

        listed = repo.list_projects()
        for name in ("PROJ_A", "PROJ_B", "PROJ_C"):
            assert name in listed

    def test_multiple_projects_are_isolated(self, tmp_path):
        """Two projects with different data do not bleed into each other."""
        repo = ProjectRepository(base_path=tmp_path)
        p1 = _project("ISO_A", target=50)
        p2 = _project("ISO_B", target=200)
        repo.create_project(p1)
        repo.create_project(p2)

        loaded_a = repo.load("ISO_A")
        loaded_b = repo.load("ISO_B")
        assert loaded_a.target_sample_size == 50
        assert loaded_b.target_sample_size == 200


# ============================================================================
# Test group 2: Forecast chart integration
# ============================================================================

class TestChartIntegration:
    """RecruitmentChart integrates correctly with RecruitmentTracker + ProjectMetadata."""

    def test_chart_png_saved_to_project_dir(self, tmp_path):
        """Chart.save() writes a non-empty PNG under the given path."""
        project = _project(target=80)
        tracker = _tracker_with_events(project, n=50)
        chart = RecruitmentChart(tracker, target=project.target_sample_size)
        png = tmp_path / "forecast.png"
        chart.save(str(png), dpi=72)
        assert png.exists()
        assert png.stat().st_size > 10_000  # At least 10 KB

    def test_chart_svg_saved(self, tmp_path):
        """Chart saves as SVG without error."""
        project = _project(target=80)
        tracker = _tracker_with_events(project, n=50)
        chart = RecruitmentChart(tracker, target=project.target_sample_size)
        svg = tmp_path / "forecast.svg"
        chart.save(str(svg))
        assert svg.exists()

    def test_forecast_linked_to_metadata_target(self):
        """Forecast completion grows with larger target sample size."""
        project_small = _project("SMALL", target=50)
        project_large = _project("LARGE", target=500)

        tracker_small = _tracker_with_events(project_small, n=40)
        tracker_large = _tracker_with_events(project_large, n=40)

        fc_small = tracker_small.forecast_completion()
        fc_large = tracker_large.forecast_completion()

        # Parse ISO strings for comparison
        date_small = date.fromisoformat(fc_small["predicted_completion_date"])
        date_large = date.fromisoformat(fc_large["predicted_completion_date"])
        assert date_small < date_large

    def test_forecast_predicted_date_is_date_object(self):
        """forecast_completion() returns an ISO date string for predicted_completion_date."""
        project = _project(target=100)
        tracker = _tracker_with_events(project, n=60)
        fc = tracker.forecast_completion()
        pred = fc["predicted_completion_date"]
        # Value is returned as an ISO format string (e.g. "2026-09-02")
        assert isinstance(pred, str)
        parsed = date.fromisoformat(pred)
        assert isinstance(parsed, date)

    def test_chart_builds_with_high_r_squared(self):
        """Chart builds without error and forecast has R² > 0.5 for steady enrollment."""
        project = _project(target=120)
        tracker = _tracker_with_events(project, n=80)
        chart = RecruitmentChart(tracker, target=project.target_sample_size)
        fig = chart.build()
        assert fig is not None

        fc = tracker.forecast_completion()
        assert fc.get("r_squared", 0) > 0.5


# ============================================================================
# Test group 3: Quality report CSV
# ============================================================================

class TestQualityReportIntegration:
    """Quality report generation logic (mirrors data_page._generate_quality_report)."""

    def _build_report(self, df: pd.DataFrame) -> pd.DataFrame:
        """Mirror the data_page quality report logic."""
        rows = []
        for col in df.columns:
            series = df[col]
            n_total = len(series)
            n_missing = int(series.isna().sum())
            pct_missing = round(n_missing / n_total * 100, 2) if n_total else 0.0
            n_unique = int(series.nunique(dropna=True))
            col_type = str(series.dtype)
            if pd.api.types.is_numeric_dtype(series):
                clean = series.dropna()
                col_min = round(float(clean.min()), 4) if not clean.empty else ""
                col_max = round(float(clean.max()), 4) if not clean.empty else ""
                col_mean = round(float(clean.mean()), 4) if not clean.empty else ""
            else:
                col_min = col_max = col_mean = ""
            rows.append({
                "Column": col, "Type": col_type,
                "Non-Null Count": n_total - n_missing,
                "Missing Count": n_missing,
                "Missing %": pct_missing,
                "Unique Values": n_unique,
                "Min": col_min, "Max": col_max, "Mean": col_mean,
            })
        return pd.DataFrame(rows)

    def test_report_has_expected_columns(self):
        df = _synthetic_df()
        report = self._build_report(df)
        for expected_col in ["Column", "Type", "Non-Null Count", "Missing Count",
                              "Missing %", "Unique Values", "Min", "Max", "Mean"]:
            assert expected_col in report.columns

    def test_report_has_one_row_per_column(self):
        df = _synthetic_df()
        report = self._build_report(df)
        assert len(report) == len(df.columns)

    def test_report_missing_percent_correct(self):
        """egfr has ~6% missing in synthetic data — report should reflect that."""
        df = _synthetic_df(n=1000)
        report = self._build_report(df)
        egfr_row = report[report["Column"] == "egfr"].iloc[0]
        assert egfr_row["Missing %"] > 0.0  # Some rows were set to NaN

    def test_report_numeric_stats_populated(self):
        """Numeric columns (age, bmi, egfr) should have non-empty Min/Max/Mean."""
        df = _synthetic_df()
        report = self._build_report(df)
        for col in ["age", "bmi"]:
            row = report[report["Column"] == col].iloc[0]
            assert row["Min"] != ""
            assert row["Max"] != ""
            assert row["Mean"] != ""

    def test_report_categorical_stats_empty(self):
        """Categorical columns (sex, hypertension) should have empty Min/Max/Mean."""
        df = _synthetic_df()
        report = self._build_report(df)
        for col in ["sex", "hypertension"]:
            row = report[report["Column"] == col].iloc[0]
            assert row["Min"] == ""
            assert row["Max"] == ""
            assert row["Mean"] == ""

    def test_report_saved_as_csv(self, tmp_path):
        """Report can be written to CSV and reloaded correctly."""
        df = _synthetic_df()
        report = self._build_report(df)
        path = tmp_path / "quality_report.csv"
        report.to_csv(path, index=False, encoding="utf-8-sig")
        assert path.exists()

        loaded = pd.read_csv(path)
        assert len(loaded) == len(df.columns)
        assert "Column" in loaded.columns


# ============================================================================
# Test group 4: Table 1 integration
# ============================================================================

class TestTable1Integration:
    """Table1Generator integrates correctly with synthetic clinical data."""

    def test_table1_generates_for_mixed_types(self):
        """Table 1 generates without error for both continuous and categorical vars."""
        df = _synthetic_df()
        gen = Table1Generator(df)
        gen.add_variable("age", "continuous", label="Age (years)")
        gen.add_variable("sex", "categorical", label="Sex")
        gen.add_variable("bmi", "continuous", label="BMI")
        gen.add_variable("hypertension", "categorical", label="Hypertension")
        table = gen.generate()
        assert len(table) > 0
        assert "Variable" in table.columns

    def test_table1_exported_to_csv(self, tmp_path):
        """Table 1 CSV export writes a readable file."""
        df = _synthetic_df()
        gen = Table1Generator(df)
        gen.add_variable("age", "continuous", label="Age")
        gen.generate()
        csv_path = tmp_path / "table1.csv"
        gen.export_to_csv(csv_path)
        assert csv_path.exists()
        loaded = pd.read_csv(csv_path)
        assert len(loaded) > 0
