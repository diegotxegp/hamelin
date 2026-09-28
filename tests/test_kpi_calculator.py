"""
Tests for KPICalculator
~~~~~~~~~~~~~~~~~~~~~~~

Tests cover all 8 KPI fields, edge cases, and the public calculate() API.

No PySide6 required — uses plain Mock objects for metadata and tracker.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, PropertyMock

from hamelin.analytics.kpi_calculator import KPICalculator, KPIResult


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_event(patient_id: str, enrollment_date: date, event_type: str = "enrollment"):
    """Create a minimal RecruitmentEvent-like mock."""
    e = MagicMock()
    e.patient_id = patient_id
    e.enrollment_date = enrollment_date
    e.event_type = event_type
    return e


def _make_meta(
    target: int = 100,
    first_patient_date: date | None = date(2025, 1, 1),
    estimated_completion_date: date | None = date(2026, 12, 31),
):
    """Create a minimal ProjectMetadata-like mock."""
    meta = MagicMock()
    meta.target_sample_size = target
    meta.first_patient_date = first_patient_date
    meta.estimated_completion_date = estimated_completion_date
    return meta


def _make_tracker(events=None, velocity: float = 5.0):
    """Create a minimal RecruitmentTracker-like mock."""
    tracker = MagicMock()
    tracker.events = events if events is not None else []
    tracker.calculate_velocity.return_value = velocity
    return tracker


# ── Fixtures ───────────────────────────────────────────────────────────────────

REF_DATE = date(2026, 2, 23)

EVENTS_30 = [
    _make_event(f"P{i:03d}", REF_DATE - timedelta(days=60 - i))
    for i in range(30)
]


# ── TestKPICalculatorInit ──────────────────────────────────────────────────────

class TestKPICalculatorInit:

    def test_stores_metadata(self):
        meta = _make_meta()
        tracker = _make_tracker()
        calc = KPICalculator(meta, tracker)
        assert calc.metadata is meta

    def test_stores_tracker(self):
        meta = _make_meta()
        tracker = _make_tracker()
        calc = KPICalculator(meta, tracker)
        assert calc.tracker is tracker


# ── TestCountRecruited ────────────────────────────────────────────────────────

class TestCountRecruited:

    def test_no_events_returns_zero(self):
        calc = KPICalculator(_make_meta(), _make_tracker(events=[]))
        assert calc._count_recruited() == 0

    def test_counts_enrollment_events_only(self):
        events = [
            _make_event("P001", REF_DATE - timedelta(days=10), "enrollment"),
            _make_event("P002", REF_DATE - timedelta(days=5), "enrollment"),
            _make_event("P003", REF_DATE - timedelta(days=1), "withdrawal"),
        ]
        calc = KPICalculator(_make_meta(), _make_tracker(events=events))
        assert calc._count_recruited() == 2

    def test_all_withdrawals_returns_zero(self):
        events = [_make_event("P001", REF_DATE, "withdrawal")]
        calc = KPICalculator(_make_meta(), _make_tracker(events=events))
        assert calc._count_recruited() == 0

    def test_counts_all_enrollment_events(self):
        calc = KPICalculator(_make_meta(), _make_tracker(events=EVENTS_30))
        assert calc._count_recruited() == 30


# ── TestCompletionPct ─────────────────────────────────────────────────────────

class TestCompletionPct:

    def test_zero_target_returns_zero(self):
        assert KPICalculator._completion_pct(50, 0) == 0.0

    def test_negative_target_returns_zero(self):
        assert KPICalculator._completion_pct(10, -5) == 0.0

    def test_half_completion(self):
        assert KPICalculator._completion_pct(50, 100) == 50.0

    def test_full_completion(self):
        assert KPICalculator._completion_pct(100, 100) == 100.0

    def test_over_enrolled_capped_at_100(self):
        assert KPICalculator._completion_pct(110, 100) == 100.0

    def test_decimal_precision(self):
        result = KPICalculator._completion_pct(1, 3)
        assert result == round(1 / 3 * 100, 2)


# ── TestRatePerMonth ──────────────────────────────────────────────────────────

class TestRatePerMonth:

    def test_delegates_to_calculate_velocity(self):
        tracker = _make_tracker(velocity=7.5)
        calc = KPICalculator(_make_meta(), tracker)
        assert calc._rate_per_month() == 7.5
        tracker.calculate_velocity.assert_called_once_with(window_days=30)

    def test_returns_zero_on_exception(self):
        tracker = _make_tracker()
        tracker.calculate_velocity.side_effect = Exception("no data")
        calc = KPICalculator(_make_meta(), tracker)
        assert calc._rate_per_month() == 0.0

    def test_empty_tracker_returns_zero(self):
        tracker = _make_tracker(events=[], velocity=0.0)
        calc = KPICalculator(_make_meta(), tracker)
        assert calc._rate_per_month() == 0.0


# ── TestEstimateEndDate ───────────────────────────────────────────────────────

class TestEstimateEndDate:

    def _calc(self, **kw):
        return KPICalculator(_make_meta(), _make_tracker())

    def test_zero_target_returns_none(self):
        calc = self._calc()
        result = calc._estimate_end_date(REF_DATE, 10, 0, 0, 5.0)
        assert result is None

    def test_already_complete_returns_last_enrollment_date(self):
        last = REF_DATE - timedelta(days=3)
        events = [
            _make_event("P001", REF_DATE - timedelta(days=10)),
            _make_event("P002", last),
        ]
        calc = KPICalculator(_make_meta(), _make_tracker(events=events))
        result = calc._estimate_end_date(REF_DATE, 100, 100, 0, 5.0)
        assert result == last

    def test_zero_rate_returns_none(self):
        calc = self._calc()
        result = calc._estimate_end_date(REF_DATE, 50, 100, 50, 0.0)
        assert result is None

    def test_positive_rate_returns_future_date(self):
        calc = self._calc()
        # 60 remaining at 6 per month → 10 months → 300 days
        result = calc._estimate_end_date(REF_DATE, 40, 100, 60, 6.0)
        expected = REF_DATE + timedelta(days=300)
        assert result == expected

    def test_no_events_complete_returns_today(self):
        """When already complete but no events, fall back to today."""
        calc = KPICalculator(_make_meta(), _make_tracker(events=[]))
        result = calc._estimate_end_date(REF_DATE, 100, 100, 0, 0.0)
        assert result == REF_DATE


# ── TestDaysElapsed ───────────────────────────────────────────────────────────

class TestDaysElapsed:

    def test_no_first_patient_date_returns_zero(self):
        meta = _make_meta(first_patient_date=None)
        calc = KPICalculator(meta, _make_tracker())
        assert calc._days_elapsed(REF_DATE) == 0

    def test_same_day_returns_zero(self):
        meta = _make_meta(first_patient_date=REF_DATE)
        calc = KPICalculator(meta, _make_tracker())
        assert calc._days_elapsed(REF_DATE) == 0

    def test_correct_days_count(self):
        start = REF_DATE - timedelta(days=100)
        meta = _make_meta(first_patient_date=start)
        calc = KPICalculator(meta, _make_tracker())
        assert calc._days_elapsed(REF_DATE) == 100

    def test_future_start_date_returns_zero(self):
        """first_patient_date in the future should not give negative days."""
        meta = _make_meta(first_patient_date=REF_DATE + timedelta(days=10))
        calc = KPICalculator(meta, _make_tracker())
        assert calc._days_elapsed(REF_DATE) == 0


# ── TestOnTrack ───────────────────────────────────────────────────────────────

class TestOnTrack:

    def test_already_complete_returns_true(self):
        calc = KPICalculator(_make_meta(target=100), _make_tracker())
        assert calc._on_track(100, 100, None) is True

    def test_over_recruited_returns_true(self):
        calc = KPICalculator(_make_meta(target=100), _make_tracker())
        assert calc._on_track(105, 100, None) is True

    def test_no_planned_end_returns_false(self):
        meta = _make_meta(estimated_completion_date=None)
        calc = KPICalculator(meta, _make_tracker())
        assert calc._on_track(50, 100, REF_DATE + timedelta(days=100)) is False

    def test_none_estimated_end_returns_false(self):
        calc = KPICalculator(_make_meta(), _make_tracker())
        assert calc._on_track(50, 100, None) is False

    def test_before_deadline_returns_true(self):
        meta = _make_meta(estimated_completion_date=REF_DATE + timedelta(days=200))
        calc = KPICalculator(meta, _make_tracker())
        assert calc._on_track(50, 100, REF_DATE + timedelta(days=100)) is True

    def test_after_deadline_returns_false(self):
        meta = _make_meta(estimated_completion_date=REF_DATE + timedelta(days=50))
        calc = KPICalculator(meta, _make_tracker())
        assert calc._on_track(50, 100, REF_DATE + timedelta(days=200)) is False

    def test_exact_deadline_returns_true(self):
        deadline = REF_DATE + timedelta(days=100)
        meta = _make_meta(estimated_completion_date=deadline)
        calc = KPICalculator(meta, _make_tracker())
        assert calc._on_track(50, 100, deadline) is True


# ── TestCalculate (integration) ───────────────────────────────────────────────

class TestCalculate:

    def test_returns_kpi_result_instance(self):
        calc = KPICalculator(_make_meta(), _make_tracker(events=EVENTS_30[:10]))
        result = calc.calculate(reference_date=REF_DATE)
        assert isinstance(result, KPIResult)

    def test_fields_consistent(self):
        """remaining = target - recruited; completion_pct matches."""
        events = EVENTS_30  # 30 events
        calc = KPICalculator(_make_meta(target=100), _make_tracker(events=events, velocity=4.0))
        r = calc.calculate(reference_date=REF_DATE)
        assert r.total_recruited == 30
        assert r.target_sample_size == 100
        assert r.remaining == 70
        assert r.completion_pct == 30.0

    def test_no_events_all_zeros(self):
        calc = KPICalculator(_make_meta(target=50), _make_tracker(events=[], velocity=0.0))
        r = calc.calculate(reference_date=REF_DATE)
        assert r.total_recruited == 0
        assert r.remaining == 50
        assert r.completion_pct == 0.0
        assert r.rate_per_month == 0.0
        assert r.estimated_end_date is None
        assert r.on_track is False

    def test_zero_target_does_not_crash(self):
        calc = KPICalculator(_make_meta(target=0), _make_tracker())
        r = calc.calculate(reference_date=REF_DATE)
        assert r.target_sample_size == 0
        assert r.completion_pct == 0.0
        assert r.estimated_end_date is None

    def test_completed_study_is_on_track(self):
        events = [_make_event(f"P{i}", REF_DATE - timedelta(days=i)) for i in range(100)]
        calc = KPICalculator(_make_meta(target=100), _make_tracker(events=events, velocity=10.0))
        r = calc.calculate(reference_date=REF_DATE)
        assert r.remaining == 0
        assert r.completion_pct == 100.0
        assert r.on_track is True

    def test_result_is_frozen(self):
        calc = KPICalculator(_make_meta(), _make_tracker())
        r = calc.calculate(reference_date=REF_DATE)
        with pytest.raises((AttributeError, TypeError)):
            r.total_recruited = 999  # type: ignore[misc]

    def test_reference_date_used_for_days_elapsed(self):
        start = REF_DATE - timedelta(days=50)
        meta = _make_meta(first_patient_date=start)
        calc = KPICalculator(meta, _make_tracker())
        r = calc.calculate(reference_date=REF_DATE)
        assert r.days_elapsed == 50
