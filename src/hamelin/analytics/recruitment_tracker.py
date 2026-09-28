"""
Recruitment Tracker System for HAMELIN

This module tracks patient enrollment in clinical studies, analyzes recruitment
patterns, and forecasts study completion dates.

Features:
- Process datasets to extract enrollment events
- Track cumulative enrollment over time
- Calculate enrollment velocity and trends
- Detect enrollment gaps
- Forecast completion dates with confidence intervals
- Save/load recruitment logs

Author: AI Assistant
Date: February 18, 2026
Version: 2.0
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import json
import pandas as pd
import numpy as np
from scipy import stats

from hamelin.core.project import ProjectMetadata
from hamelin.utils.logger import log
from hamelin.utils.exceptions import (
    ValidationError,
    DataLoadError,
    DataSaveError
)


@dataclass
class RecruitmentEvent:
    """
    Single patient enrollment event.
    
    Attributes:
        patient_id: Unique patient identifier
        enrollment_date: Date of enrollment
        event_type: Type of event (enrollment, withdrawal, etc.)
    
    Example:
        >>> event = RecruitmentEvent(
        ...     patient_id="P001",
        ...     enrollment_date=date(2024, 2, 1),
        ...     event_type="enrollment"
        ... )
    """
    patient_id: str
    enrollment_date: date
    event_type: str = "enrollment"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'patient_id': self.patient_id,
            'enrollment_date': self.enrollment_date.isoformat(),
            'event_type': self.event_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecruitmentEvent':
        """Create from dictionary."""
        return cls(
            patient_id=data['patient_id'],
            enrollment_date=date.fromisoformat(data['enrollment_date']),
            event_type=data.get('event_type', 'enrollment')
        )


class RecruitmentTracker:
    """
    Track and analyze patient recruitment in clinical studies.
    
    This class manages recruitment events, calculates enrollment statistics,
    and forecasts study completion dates based on enrollment trends.
    
    Example:
        >>> from hamelin.core.project import create_sample_project
        >>> project = create_sample_project()
        >>> tracker = RecruitmentTracker(project)
        >>> 
        >>> # Add enrollment events
        >>> tracker.add_event("P001", date(2024, 2, 1))
        >>> tracker.add_event("P002", date(2024, 2, 5))
        >>> 
        >>> # Get timeline
        >>> timeline = tracker.get_timeline()
        >>> 
        >>> # Forecast completion
        >>> forecast = tracker.forecast_completion()
        >>> print(forecast['predicted_completion_date'])
    """
    
    def __init__(self, project_metadata: ProjectMetadata):
        """
        Initialize recruitment tracker.
        
        Args:
            project_metadata: Project metadata with target sample size and dates
        """
        self.project_metadata = project_metadata
        self.events: List[RecruitmentEvent] = []
        self._timeline_cache: Optional[pd.DataFrame] = None
        
        log.info(
            f"Initialized RecruitmentTracker for project '{project_metadata.short_name}' "
            f"(target: {project_metadata.target_sample_size} patients)"
        )
    
    def add_event(self, patient_id: str, enrollment_date: date, event_type: str = "enrollment") -> None:
        """
        Add a single recruitment event.
        
        Args:
            patient_id: Unique patient identifier
            enrollment_date: Date of enrollment
            event_type: Type of event (default: "enrollment")
        
        Raises:
            ValidationError: If patient_id already exists or date is invalid
        """
        # Check for duplicate patient ID
        if any(e.patient_id == patient_id for e in self.events):
            raise ValidationError(f"Patient ID '{patient_id}' already enrolled")
        
        # Validate date range
        if self.project_metadata.first_patient_date:
            if enrollment_date < self.project_metadata.first_patient_date:
                log.warning(
                    f"Enrollment date {enrollment_date} is before first_patient_date "
                    f"{self.project_metadata.first_patient_date}"
                )
        
        event = RecruitmentEvent(
            patient_id=patient_id,
            enrollment_date=enrollment_date,
            event_type=event_type
        )
        
        self.events.append(event)
        self._timeline_cache = None  # Invalidate cache
        
        log.debug(f"Added enrollment event: {patient_id} on {enrollment_date}")
    
    def process_dataset(
        self,
        df: pd.DataFrame,
        date_column: str,
        id_column: Optional[str] = None
    ) -> int:
        """
        Extract recruitment events from a dataset.
        
        Args:
            df: DataFrame containing patient data
            date_column: Name of column containing enrollment dates
            id_column: Name of column with patient IDs (optional, uses index if None)
        
        Returns:
            Number of events processed
        
        Raises:
            ValidationError: If date_column not found or data invalid
        """
        if date_column not in df.columns:
            raise ValidationError(
                f"Date column '{date_column}' not found in dataset. "
                f"Available columns: {', '.join(df.columns)}"
            )
        
        # Use index as patient ID if not specified
        if id_column is None:
            df = df.copy()
            df['_patient_id'] = df.index.astype(str)
            id_column = '_patient_id'
        elif id_column not in df.columns:
            raise ValidationError(
                f"ID column '{id_column}' not found in dataset. "
                f"Available columns: {', '.join(df.columns)}"
            )
        
        # Convert date column to datetime
        try:
            dates = pd.to_datetime(df[date_column])
        except Exception as e:
            raise ValidationError(
                f"Failed to parse dates in column '{date_column}': {e}"
            )
        
        # Process each row
        events_added = 0
        for idx, row in df.iterrows():
            patient_id = str(row[id_column])
            enrollment_date = dates.loc[idx]
            
            # Skip if date is NaT (missing)
            if pd.isna(enrollment_date):
                log.warning(f"Skipping patient {patient_id}: missing enrollment date")
                continue
            
            # Convert to date
            enrollment_date = enrollment_date.date()
            
            # Check for duplicate
            if any(e.patient_id == patient_id for e in self.events):
                log.debug(f"Skipping duplicate patient ID: {patient_id}")
                continue
            
            # Add event
            event = RecruitmentEvent(
                patient_id=patient_id,
                enrollment_date=enrollment_date,
                event_type="enrollment"
            )
            self.events.append(event)
            events_added += 1
        
        # Sort events by date
        self.events.sort(key=lambda e: e.enrollment_date)
        self._timeline_cache = None  # Invalidate cache
        
        log.info(
            f"Processed dataset: {events_added} enrollment events "
            f"({len(df) - events_added} skipped/duplicates)"
        )
        
        return events_added
    
    def get_timeline(self) -> pd.DataFrame:
        """
        Get cumulative enrollment timeline.
        
        Returns:
            DataFrame with columns: date, cumulative_enrolled, patients_enrolled
        
        Example:
            >>> timeline = tracker.get_timeline()
            >>> print(timeline.tail())
                       date  patients_enrolled  cumulative_enrolled
            90  2025-01-10                  1                   91
            91  2025-01-12                  1                   92
            92  2025-01-13                  2                   94
            93  2025-01-14                  1                   95
            94  2025-01-15                  0                   95
        """
        # Return cached version if available
        if self._timeline_cache is not None:
            return self._timeline_cache
        
        if not self.events:
            log.warning("No enrollment events to generate timeline")
            return pd.DataFrame(columns=['date', 'patients_enrolled', 'cumulative_enrolled'])
        
        # Create DataFrame from events
        event_dates = [e.enrollment_date for e in self.events]
        
        # Count enrollments per date
        date_counts = pd.Series(event_dates).value_counts().sort_index()
        
        # Create complete date range
        min_date = min(event_dates)
        max_date = max(event_dates)
        
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        
        # Build timeline
        timeline_data = []
        cumulative = 0
        
        for current_date in date_range:
            current_date_obj = current_date.date()
            enrolled_today = date_counts.get(current_date_obj, 0)
            cumulative += enrolled_today
            
            timeline_data.append({
                'date': current_date_obj,
                'patients_enrolled': int(enrolled_today),
                'cumulative_enrolled': cumulative
            })
        
        timeline = pd.DataFrame(timeline_data)
        self._timeline_cache = timeline  # Cache result
        
        return timeline
    
    def calculate_velocity(self, window_days: int = 30) -> float:
        """
        Calculate rolling enrollment velocity.
        
        Args:
            window_days: Rolling window size in days (default: 30)
        
        Returns:
            Average patients enrolled per month over the window
        
        Example:
            >>> velocity = tracker.calculate_velocity(window_days=30)
            >>> print(f"Enrollment rate: {velocity:.1f} patients/month")
        """
        if not self.events:
            return 0.0
        
        timeline = self.get_timeline()
        
        if len(timeline) < window_days:
            # Use all available data if less than window
            window_days = len(timeline)
        
        # Get last window_days
        recent = timeline.tail(window_days)
        
        # Calculate patients enrolled in window
        patients_in_window = recent['patients_enrolled'].sum()
        
        # Convert to patients per month
        days_in_window = len(recent)
        patients_per_day = patients_in_window / days_in_window
        patients_per_month = patients_per_day * 30
        
        return patients_per_month
    
    def detect_gaps(self, max_gap_days: int = 60) -> List[Tuple[date, date]]:
        """
        Identify periods with no enrollment activity.
        
        Args:
            max_gap_days: Minimum gap length to report (default: 60 days)
        
        Returns:
            List of (start_date, end_date) tuples representing gaps
        
        Example:
            >>> gaps = tracker.detect_gaps(max_gap_days=30)
            >>> for start, end in gaps:
            ...     print(f"Gap: {start} to {end} ({(end - start).days} days)")
        """
        if len(self.events) < 2:
            return []
        
        # Sort events by date
        sorted_events = sorted(self.events, key=lambda e: e.enrollment_date)
        
        gaps = []
        
        for i in range(len(sorted_events) - 1):
            current = sorted_events[i].enrollment_date
            next_event = sorted_events[i + 1].enrollment_date
            
            gap_days = (next_event - current).days
            
            if gap_days > max_gap_days:
                gaps.append((current, next_event))
        
        if gaps:
            log.info(f"Detected {len(gaps)} enrollment gaps (>{max_gap_days} days)")
        
        return gaps
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get recruitment summary statistics.
        
        Returns:
            Dictionary with recruitment statistics
        
        Example:
            >>> summary = tracker.get_summary()
            >>> print(f"Enrolled: {summary['total_enrolled']}/{summary['target_sample_size']}")
            >>> print(f"Progress: {summary['percent_complete']:.1f}%")
        """
        if not self.events:
            return {
                'total_enrolled': 0,
                'target_sample_size': self.project_metadata.target_sample_size,
                'percent_complete': 0.0,
                'first_enrollment': None,
                'last_enrollment': None,
                'duration_days': 0,
                'avg_patients_per_month': 0.0,
                'enrollment_gaps': []
            }
        
        # Get timeline
        timeline = self.get_timeline()
        
        # Calculate statistics
        total_enrolled = len(self.events)
        target = self.project_metadata.target_sample_size
        percent_complete = (total_enrolled / target * 100) if target > 0 else 0
        
        first_date = min(e.enrollment_date for e in self.events)
        last_date = max(e.enrollment_date for e in self.events)
        duration = (last_date - first_date).days
        
        # Average patients per month
        if duration > 0:
            avg_per_month = (total_enrolled / duration) * 30
        else:
            avg_per_month = 0.0
        
        # Detect gaps
        gaps = self.detect_gaps()
        
        summary = {
            'total_enrolled': total_enrolled,
            'target_sample_size': target,
            'percent_complete': round(percent_complete, 1),
            'first_enrollment': first_date.isoformat(),
            'last_enrollment': last_date.isoformat(),
            'duration_days': duration,
            'avg_patients_per_month': round(avg_per_month, 2),
            'enrollment_gaps': len(gaps),
            'current_velocity': round(self.calculate_velocity(), 2)
        }
        
        return summary
    
    def forecast_completion(self, method: str = "linear") -> Dict[str, Any]:
        """
        Forecast study completion date based on enrollment trends.
        
        Args:
            method: Forecasting method ("linear" supported)
        
        Returns:
            Dictionary with forecast results:
                - predicted_completion_date: Estimated completion date
                - confidence_interval_days: ±days for 95% CI
                - current_velocity: Current enrollment rate
                - days_remaining: Estimated days to completion
                - patients_remaining: Patients still needed
                - on_track: Whether enrollment is on schedule
        
        Raises:
            ValidationError: If insufficient data for forecasting
        
        Example:
            >>> forecast = tracker.forecast_completion()
            >>> print(f"Predicted completion: {forecast['predicted_completion_date']}")
            >>> print(f"On track: {forecast['on_track']}")
        """
        if len(self.events) < 5:
            raise ValidationError(
                f"Insufficient data for forecasting (need ≥5 events, have {len(self.events)})"
            )
        
        target = self.project_metadata.target_sample_size
        enrolled = len(self.events)
        
        if enrolled >= target:
            # Already completed
            last_date = max(e.enrollment_date for e in self.events)
            return {
                'predicted_completion_date': last_date.isoformat(),
                'confidence_interval_days': 0,
                'current_velocity': 0.0,
                'days_remaining': 0,
                'patients_remaining': 0,
                'on_track': True,
                'status': 'completed'
            }
        
        # Get timeline
        timeline = self.get_timeline()
        
        # Prepare data for linear regression
        # X = days since start, Y = cumulative enrollment
        first_date = timeline['date'].min()
        
        # Convert dates to pandas datetime for arithmetic
        timeline['days_since_start'] = timeline['date'].apply(
            lambda d: (d - first_date).days
        )
        
        X = timeline['days_since_start'].values
        y = timeline['cumulative_enrolled'].values
        
        # Fit linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
        
        # Predict when we'll reach target
        # target = slope * days + intercept
        # days = (target - intercept) / slope
        
        if slope <= 0:
            raise ValidationError(
                "Enrollment rate is zero or negative, cannot forecast completion"
            )
        
        days_to_target = (target - intercept) / slope
        completion_date = first_date + timedelta(days=int(days_to_target))
        
        # Calculate confidence interval
        # Use standard error to estimate uncertainty
        days_std = std_err * (target - y.mean())
        confidence_interval_days = int(1.96 * days_std)  # 95% CI
        
        # Calculate current velocity
        velocity = slope * 30  # patients per month
        
        # Days and patients remaining
        current_date = max(e.enrollment_date for e in self.events)
        days_remaining = (completion_date - current_date).days
        patients_remaining = target - enrolled
        
        # Check if on track
        if self.project_metadata.estimated_completion_date:
            expected_date = self.project_metadata.estimated_completion_date
            on_track = abs((completion_date - expected_date).days) <= 60  # Within 2 months
        else:
            on_track = True  # No baseline to compare
        
        forecast = {
            'predicted_completion_date': completion_date.isoformat(),
            'confidence_interval_days': confidence_interval_days,
            'current_velocity': round(velocity, 2),
            'days_remaining': max(0, days_remaining),
            'patients_remaining': max(0, patients_remaining),
            'on_track': on_track,
            'r_squared': round(r_value ** 2, 3),
            'status': 'active'
        }
        
        log.info(
            f"Forecast completion: {completion_date.isoformat()} "
            f"(±{confidence_interval_days} days, R²={forecast['r_squared']})"
        )
        
        return forecast
    
    def is_on_track(self, tolerance: float = 0.10) -> bool:
        """
        Check if enrollment is on track compared to target timeline.
        
        Args:
            tolerance: Acceptable deviation (default: 0.10 = 10%)
        
        Returns:
            True if enrollment is within tolerance, False otherwise
        
        Example:
            >>> if tracker.is_on_track():
            ...     print("Enrollment is on schedule")
            ... else:
            ...     print("Enrollment is behind/ahead of schedule")
        """
        if not self.events:
            return True  # No data yet
        
        # Check if we have target dates
        if not (self.project_metadata.first_patient_date and 
                self.project_metadata.estimated_completion_date):
            log.warning("Cannot determine on-track status: missing project dates")
            return True
        
        first_date = self.project_metadata.first_patient_date
        end_date = self.project_metadata.estimated_completion_date
        target = self.project_metadata.target_sample_size
        
        # Calculate expected enrollment at current date
        current_date = max(e.enrollment_date for e in self.events)
        
        total_days = (end_date - first_date).days
        elapsed_days = (current_date - first_date).days
        
        if total_days <= 0:
            return True
        
        # Expected enrollment = (elapsed / total) * target
        expected_enrollment = (elapsed_days / total_days) * target
        actual_enrollment = len(self.events)
        
        # Check if within tolerance
        deviation = abs(actual_enrollment - expected_enrollment) / expected_enrollment
        
        return deviation <= tolerance
    
    def save(self, project_path: Path) -> None:
        """
        Save recruitment log to JSON file.
        
        Args:
            project_path: Path to project directory
        
        Raises:
            DataSaveError: If save operation fails
        """
        recruitment_file = project_path / "recruitment_log.json"
        
        try:
            data = {
                'project_short_name': self.project_metadata.short_name,
                'events': [e.to_dict() for e in self.events],
                'summary': self.get_summary() if self.events else {},
                'saved_at': datetime.now().isoformat()
            }
            
            with open(recruitment_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            log.info(
                f"Saved recruitment log for '{self.project_metadata.short_name}' "
                f"({len(self.events)} events) to {recruitment_file}"
            )
            
        except Exception as e:
            raise DataSaveError(f"Failed to save recruitment log: {e}") from e
    
    def load(self, project_path: Path) -> int:
        """
        Load recruitment log from JSON file.
        
        Args:
            project_path: Path to project directory
        
        Returns:
            Number of events loaded
        
        Raises:
            DataLoadError: If load operation fails
        """
        recruitment_file = project_path / "recruitment_log.json"
        
        if not recruitment_file.exists():
            raise DataLoadError(f"Recruitment log not found: {recruitment_file}")
        
        try:
            with open(recruitment_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear existing events
            self.events = []
            
            # Load events
            for event_data in data.get('events', []):
                event = RecruitmentEvent.from_dict(event_data)
                self.events.append(event)
            
            # Sort by date
            self.events.sort(key=lambda e: e.enrollment_date)
            
            # Invalidate cache
            self._timeline_cache = None
            
            log.info(
                f"Loaded recruitment log for '{self.project_metadata.short_name}' "
                f"({len(self.events)} events)"
            )
            
            return len(self.events)
            
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Corrupted recruitment log: {e}") from e
        except Exception as e:
            raise DataLoadError(f"Failed to load recruitment log: {e}") from e
