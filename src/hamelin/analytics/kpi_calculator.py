"""
KPI Calculator
~~~~~~~~~~~~~~

Pure-logic computation of project Key Performance Indicators.
No PySide6 imports — usable in tests and background workers alike.

Inputs
------
    ProjectMetadata  (hamelin.core.project)
    RecruitmentTracker  (hamelin.analytics.recruitment_tracker)

Output
------
    KPIResult  — frozen dataclass with all 8 KPI values

Usage
-----
    from hamelin.analytics.kpi_calculator import KPICalculator

    calc = KPICalculator(metadata, tracker)
    result = calc.calculate()
    print(result.completion_pct)          # e.g. 63.3
    print(result.on_track)                # True / False

Author: AI Assistant
Date: February 23, 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from hamelin.utils.logger import log


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class KPIResult:
    """
    Snapshot of all KPIs for a clinical study.

    Attributes
    ----------
    total_recruited : int
        Number of patients enrolled so far.
    target_sample_size : int
        Target number of patients per protocol.
    remaining : int
        Patients still needed  (max(0, target - recruited)).
    completion_pct : float
        Enrollment progress as a percentage 0–100.
    rate_per_month : float
        Rolling 30-day recruitment velocity (patients / month).
    estimated_end_date : Optional[date]
        Projected date of reaching *target_sample_size*.
        None when rate_per_month == 0 and study is not yet complete.
    days_elapsed : int
        Calendar days since *first_patient_date* (0 if date unknown).
    on_track : bool
        True when *estimated_end_date* ≤ *estimated_completion_date*,
        or when the study is already complete.
        False when projection exceeds planned end, or when on-track
        status cannot be assessed (no planned end date).
    """
    total_recruited: int
    target_sample_size: int
    remaining: int
    completion_pct: float
    rate_per_month: float
    estimated_end_date: Optional[date]
    days_elapsed: int
    on_track: bool


# ── Calculator ─────────────────────────────────────────────────────────────────

class KPICalculator:
    """
    Compute KPIs from project metadata and recruitment history.

    Parameters
    ----------
    metadata : ProjectMetadata
        Project metadata (name, target_sample_size, dates, …)
    tracker : RecruitmentTracker
        Recruitment tracker with enrollment events loaded.

    Example
    -------
    >>> calc = KPICalculator(metadata, tracker)
    >>> kpi = calc.calculate()
    >>> print(f"{kpi.completion_pct:.1f}% enrolled — on_track={kpi.on_track}")
    """

    def __init__(self, metadata, tracker) -> None:
        self.metadata = metadata
        self.tracker = tracker

    # ── Public API ─────────────────────────────────────────────────────

    def calculate(self, reference_date: Optional[date] = None) -> KPIResult:
        """
        Compute all KPIs and return a :class:`KPIResult`.

        Parameters
        ----------
        reference_date : date, optional
            The "today" reference for all calculations.  Defaults to
            ``date.today()``.  Passing an explicit date makes the method
            fully deterministic and easy to unit-test.

        Returns
        -------
        KPIResult
        """
        today: date = reference_date or date.today()

        total_recruited = self._count_recruited()
        target = max(0, int(getattr(self.metadata, "target_sample_size", 0) or 0))
        remaining = max(0, target - total_recruited)
        completion_pct = self._completion_pct(total_recruited, target)
        rate_per_month = self._rate_per_month()
        estimated_end_date = self._estimate_end_date(
            today, total_recruited, target, remaining, rate_per_month
        )
        days_elapsed = self._days_elapsed(today)
        on_track = self._on_track(total_recruited, target, estimated_end_date)

        result = KPIResult(
            total_recruited=total_recruited,
            target_sample_size=target,
            remaining=remaining,
            completion_pct=completion_pct,
            rate_per_month=rate_per_month,
            estimated_end_date=estimated_end_date,
            days_elapsed=days_elapsed,
            on_track=on_track,
        )
        log.debug(
            f"KPICalculator: {total_recruited}/{target} ({completion_pct:.1f}%) "
            f"rate={rate_per_month:.2f}/mo  on_track={on_track}"
        )
        return result

    # ── Private helpers ────────────────────────────────────────────────

    def _count_recruited(self) -> int:
        """Return the number of enrollment events in the tracker."""
        events = getattr(self.tracker, "events", []) or []
        return sum(
            1 for e in events
            if getattr(e, "event_type", "enrollment") == "enrollment"
        )

    @staticmethod
    def _completion_pct(recruited: int, target: int) -> float:
        """Return percentage 0.0–100.0, capped at 100 even if over-enrolled."""
        if target <= 0:
            return 0.0
        return min(100.0, round(recruited / target * 100, 2))

    def _rate_per_month(self) -> float:
        """
        Delegate to tracker.calculate_velocity(30).
        Returns 0.0 safely when tracker has no events or the method fails.
        """
        try:
            return float(self.tracker.calculate_velocity(window_days=30))
        except Exception as exc:
            log.debug(f"KPICalculator._rate_per_month: {exc}")
            return 0.0

    def _estimate_end_date(
        self,
        today: date,
        recruited: int,
        target: int,
        remaining: int,
        rate_per_month: float,
    ) -> Optional[date]:
        """
        Project the date at which *target* will be reached.

        Rules
        -----
        * Already complete (remaining == 0) → last enrollment date, else *today*
        * rate_per_month > 0               → today + (remaining / rate * 30) days
        * rate_per_month == 0              → None (indeterminate)
        """
        if target <= 0:
            return None

        if remaining <= 0:
            # Already completed — find last enrollment date
            events = getattr(self.tracker, "events", []) or []
            enrollment_dates = [
                e.enrollment_date for e in events
                if getattr(e, "event_type", "enrollment") == "enrollment"
            ]
            return max(enrollment_dates) if enrollment_dates else today

        if rate_per_month > 0:
            days_needed = int((remaining / rate_per_month) * 30)
            return today + timedelta(days=days_needed)

        return None  # Cannot estimate

    def _days_elapsed(self, today: date) -> int:
        """Days since first_patient_date; 0 when the date is not set."""
        first = getattr(self.metadata, "first_patient_date", None)
        if first is None:
            return 0
        delta = (today - first).days
        return max(0, delta)

    def _on_track(
        self,
        recruited: int,
        target: int,
        estimated_end_date: Optional[date],
    ) -> bool:
        """
        Assess whether the study is on schedule.

        Logic
        -----
        1. Already complete → True
        2. No planned completion date → False (cannot assess)
        3. estimated_end_date is None (rate=0) → False
        4. estimated_end_date ≤ planned_completion_date → True
        """
        if target > 0 and recruited >= target:
            return True   # Complete

        planned = getattr(self.metadata, "estimated_completion_date", None)
        if planned is None:
            return False  # Cannot assess

        if estimated_end_date is None:
            return False  # Rate is zero — stuck

        return estimated_end_date <= planned
