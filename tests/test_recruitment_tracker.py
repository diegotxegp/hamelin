"""
Test Suite for Recruitment Tracker System

This module tests recruitment tracking, analytics, and forecasting functionality.

Author: AI Assistant
Date: February 18, 2026
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import json

from hamelin.analytics.recruitment_tracker import RecruitmentEvent, RecruitmentTracker
from hamelin.core.project import ProjectMetadata
from hamelin.utils.exceptions import ValidationError, DataLoadError, DataSaveError


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def valid_project():
    """Create a valid project metadata for testing."""
    return ProjectMetadata(
        name="Test Clinical Study",
        short_name="TCS",
        protocol_number="PROTO-2024-001",
        target_sample_size=100,
        first_patient_date=date(2024, 1, 1),
        estimated_completion_date=date(2025, 1, 1),
        principal_investigator="Dr. Test",
        contact_email="test@example.com",
        institution="Test Hospital"
    )


@pytest.fixture
def tracker(valid_project):
    """Create recruitment tracker with valid project."""
    return RecruitmentTracker(valid_project)


@pytest.fixture
def sample_enrollment_data():
    """Generate sample enrollment dataset."""
    # Simulate 50 patients enrolled over 6 months
    start_date =date(2024, 1, 15)
    
    data = []
    for i in range(50):
        # Stagger enrollments (2-3 per week on average)
        days_offset = i * 4  # ~2 per week
        enrollment_date = start_date + timedelta(days=days_offset)
        
        data.append({
            'patient_id': f'P{i+1:03d}',
            'enrollment_date': enrollment_date,
            'age': 45 + (i % 30),
            'gender': 'F' if i % 2 == 0 else 'M'
        })
    
    return pd.DataFrame(data)


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


# ============================================================================
# Test RecruitmentEvent
# ============================================================================

class TestRecruitmentEvent:
    """Test recruitment event data structure."""
    
    def test_event_creation(self):
        """Test creating a recruitment event."""
        event = RecruitmentEvent(
            patient_id="P001",
            enrollment_date=date(2024, 2, 1),
            event_type="enrollment"
        )
        
        assert event.patient_id == "P001"
        assert event.enrollment_date == date(2024, 2, 1)
        assert event.event_type == "enrollment"
    
    def test_event_serialization(self):
        """Test event to_dict conversion."""
        event = RecruitmentEvent(
            patient_id="P001",
            enrollment_date=date(2024, 2, 1)
        )
        
        data = event.to_dict()
        
        assert data['patient_id'] == "P001"
        assert data['enrollment_date'] == "2024-02-01"
        assert data['event_type'] == "enrollment"
    
    def test_event_deserialization(self):
        """Test event from_dict creation."""
        data = {
            'patient_id': "P002",
            'enrollment_date': "2024-03-15",
            'event_type': "enrollment"
        }
        
        event = RecruitmentEvent.from_dict(data)
        
        assert event.patient_id == "P002"
        assert event.enrollment_date == date(2024, 3, 15)
        assert event.event_type == "enrollment"
    
    def test_event_roundtrip(self):
        """Test serialization roundtrip."""
        original = RecruitmentEvent(
            patient_id="P003",
            enrollment_date=date(2024, 5, 20),
            event_type="enrollment"
        )
        
        # Serialize and deserialize
        data = original.to_dict()
        restored = RecruitmentEvent.from_dict(data)
        
        assert restored.patient_id == original.patient_id
        assert restored.enrollment_date == original.enrollment_date
        assert restored.event_type == original.event_type


# ============================================================================
# Test RecruitmentTracker Initialization
# ============================================================================

class TestRecruitmentTrackerInitialization:
    """Test tracker initialization."""
    
    def test_tracker_creation(self, valid_project):
        """Test creating a tracker."""
        tracker = RecruitmentTracker(valid_project)
        
        assert tracker.project_metadata == valid_project
        assert len(tracker.events) == 0
        assert tracker._timeline_cache is None
    
    def test_tracker_stores_project_info(self, tracker, valid_project):
        """Test tracker stores project metadata."""
        assert tracker.project_metadata.short_name == "TCS"
        assert tracker.project_metadata.target_sample_size == 100


# ============================================================================
# Test Adding Individual Events
# ============================================================================

class TestAddingEvents:
    """Test manual event addition."""
    
    def test_add_single_event(self, tracker):
        """Test adding one event."""
        tracker.add_event("P001", date(2024, 2, 1))
        
        assert len(tracker.events) == 1
        assert tracker.events[0].patient_id == "P001"
        assert tracker.events[0].enrollment_date == date(2024, 2, 1)
    
    def test_add_multiple_events(self, tracker):
        """Test adding multiple events."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))
        tracker.add_event("P003", date(2024, 2, 10))
        
        assert len(tracker.events) == 3
    
    def test_add_duplicate_patient_id_raises_error(self, tracker):
        """Test that duplicate patient IDs are rejected."""
        tracker.add_event("P001", date(2024, 2, 1))
        
        with pytest.raises(ValidationError, match="already enrolled"):
            tracker.add_event("P001", date(2024, 2, 2))
    
    def test_add_event_invalidates_cache(self, tracker):
        """Test that adding event clears timeline cache."""
        tracker.add_event("P001", date(2024, 2, 1))
        
        # Access timeline to populate cache
        timeline = tracker.get_timeline()
        assert tracker._timeline_cache is not None
        
        # Add another event
        tracker.add_event("P002", date(2024, 2, 2))
        
        # Cache should be invalidated
        assert tracker._timeline_cache is None


# ============================================================================
# Test Dataset Processing
# ============================================================================

class TestDatasetProcessing:
    """Test processing enrollment data from DataFrames."""
    
    def test_process_dataset_basic(self, tracker):
        """Test processing a simple dataset."""
        df = pd.DataFrame({
            'patient_id': ['P001', 'P002', 'P003'],
            'enrollment_date': ['2024-02-01', '2024-02-05', '2024-02-10']
        })
        
        count = tracker.process_dataset(df, date_column='enrollment_date', id_column='patient_id')
        
        assert count == 3
        assert len(tracker.events) == 3
    
    def test_process_dataset_uses_index_when_no_id_column(self, tracker):
        """Test that index is used if no ID column specified."""
        df = pd.DataFrame({
            'enrollment_date': ['2024-02-01', '2024-02-05']
        })
        
        count = tracker.process_dataset(df, date_column='enrollment_date')
        
        assert count == 2
        assert tracker.events[0].patient_id == '0'
        assert tracker.events[1].patient_id == '1'
    
    def test_process_dataset_skips_missing_dates(self, tracker):
        """Test that rows with missing dates are skipped."""
        df = pd.DataFrame({
            'patient_id': ['P001', 'P002', 'P003'],
            'enrollment_date': ['2024-02-01', None, '2024-02-10']
        })
        
        count = tracker.process_dataset(df, date_column='enrollment_date', id_column='patient_id')
        
        assert count == 2  # P002 skipped
        assert len(tracker.events) == 2
    
    def test_process_dataset_skips_duplicates(self, tracker):
        """Test that duplicate patient IDs are skipped."""
        # Add existing event
        tracker.add_event("P001", date(2024, 2, 1))
        
        df = pd.DataFrame({
            'patient_id': ['P001', 'P002', 'P003'],
            'enrollment_date': ['2024-02-02', '2024-02-05', '2024-02-10']
        })
        
        count = tracker.process_dataset(df, date_column='enrollment_date', id_column='patient_id')
        
        assert count == 2  # P001 skipped (duplicate)
        assert len(tracker.events) == 3  # 1 existing + 2 new
    
    def test_process_dataset_missing_date_column_raises_error(self, tracker):
        """Test error when date column not found."""
        df = pd.DataFrame({
            'patient_id': ['P001', 'P002'],
            'other_column': ['A', 'B']
        })
        
        with pytest.raises(ValidationError, match="Date column.*not found"):
            tracker.process_dataset(df, date_column='enrollment_date', id_column='patient_id')
    
    def test_process_dataset_missing_id_column_raises_error(self, tracker):
        """Test error when ID column not found."""
        df = pd.DataFrame({
            'enrollment_date': ['2024-02-01', '2024-02-05']
        })
        
        with pytest.raises(ValidationError, match="ID column.*not found"):
            tracker.process_dataset(df, date_column='enrollment_date', id_column='patient_id')
    
    def test_process_dataset_sorts_by_date(self, tracker):
        """Test that events are sorted chronologically."""
        df = pd.DataFrame({
            'patient_id': ['P003', 'P001', 'P002'],
            'enrollment_date': ['2024-02-10', '2024-02-01', '2024-02-05']
        })
        
        tracker.process_dataset(df, date_column='enrollment_date', id_column='patient_id')
        
        # Events should be sorted by date
        assert tracker.events[0].patient_id == 'P001'  # Feb 1
        assert tracker.events[1].patient_id == 'P002'  # Feb 5
        assert tracker.events[2].patient_id == 'P003'  # Feb 10
    
    def test_process_large_dataset(self, tracker, sample_enrollment_data):
        """Test processing realistic dataset."""
        count = tracker.process_dataset(
            sample_enrollment_data,
            date_column='enrollment_date',
            id_column='patient_id'
        )
        
        assert count == 50
        assert len(tracker.events) == 50


# ============================================================================
# Test Timeline Generation
# ============================================================================

class TestTimeline:
    """Test cumulative enrollment timeline."""
    
    def test_get_timeline_empty(self, tracker):
        """Test timeline with no events."""
        timeline = tracker.get_timeline()
        
        assert len(timeline) == 0
        assert list(timeline.columns) == ['date', 'patients_enrolled', 'cumulative_enrolled']
    
    def test_get_timeline_basic(self, tracker):
        """Test timeline with basic events."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 3))
        tracker.add_event("P003", date(2024, 2, 5))
        
        timeline = tracker.get_timeline()
        
        assert len(timeline) == 5  # Feb 1-5
        assert timeline.iloc[0]['patients_enrolled'] == 1  # Day 1
        assert timeline.iloc[0]['cumulative_enrolled'] == 1
        assert timeline.iloc[2]['patients_enrolled'] == 1  # Day 3
        assert timeline.iloc[2]['cumulative_enrolled'] == 2
        assert timeline.iloc[4]['cumulative_enrolled'] == 3  # Day 5
    
    def test_get_timeline_multiple_same_day(self, tracker):
        """Test timeline with multiple enrollments on same day."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 1))
        tracker.add_event("P003", date(2024, 2, 1))
        
        timeline = tracker.get_timeline()
        
        assert len(timeline) == 1
        assert timeline.iloc[0]['patients_enrolled'] == 3
        assert timeline.iloc[0]['cumulative_enrolled'] == 3
    
    def test_get_timeline_includes_gap_days(self, tracker):
        """Test timeline includes days with zero enrollment."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))  # 3-day gap
        
        timeline = tracker.get_timeline()
        
        assert len(timeline) == 5  # Feb 1-5
        # Days 2-4 should have 0 enrollments
        assert timeline.iloc[1]['patients_enrolled'] == 0
        assert timeline.iloc[2]['patients_enrolled'] == 0
        assert timeline.iloc[3]['patients_enrolled'] == 0
        # But cumulative should remain constant
        assert timeline.iloc[1]['cumulative_enrolled'] == 1
        assert timeline.iloc[2]['cumulative_enrolled'] == 1
        assert timeline.iloc[3]['cumulative_enrolled'] == 1
    
    def test_timeline_caching(self, tracker):
        """Test that timeline is cached for performance."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))
        
        # First call
        timeline1 = tracker.get_timeline()
        assert tracker._timeline_cache is not None
        
        # Second call should return cached version
        timeline2 = tracker.get_timeline()
        
        # Should be the same object (cached)
        assert timeline1 is timeline2


# ============================================================================
# Test Velocity Calculation
# ============================================================================

class TestVelocity:
    """Test enrollment velocity metrics."""
    
    def test_calculate_velocity_empty(self, tracker):
        """Test velocity with no events."""
        velocity = tracker.calculate_velocity()
        
        assert velocity == 0.0
    
    def test_calculate_velocity_basic(self, tracker):
        """Test velocity calculation."""
        # Add 10 patients over 30 days (10 patients/month)
        start = date(2024, 2, 1)
        for i in range(10):
            tracker.add_event(f'P{i+1:03d}', start + timedelta(days=i*3))
        
        velocity = tracker.calculate_velocity(window_days=30)
        
        # Should be approximately 10 patients/month
        assert 9.0 <= velocity <= 11.0
    
    def test_calculate_velocity_with_small_dataset(self, tracker):
        """Test velocity with less data than window."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))
        
        # Window is 30 days but only 5 days of data
        velocity = tracker.calculate_velocity(window_days=30)
        
        # Should use all available data (5 days)
        assert velocity > 0


# ============================================================================
# Test Gap Detection
# ============================================================================

class TestGapDetection:
    """Test enrollment gap identification."""
    
    def test_detect_gaps_none(self, tracker):
        """Test gap detection with continuous enrollment."""
        # Add patients every few days
        start = date(2024, 2, 1)
        for i in range(10):
            tracker.add_event(f'P{i+1:03d}', start + timedelta(days=i*3))
        
        gaps = tracker.detect_gaps(max_gap_days=30)
        
        assert len(gaps) == 0
    
    def test_detect_gaps_found(self, tracker):
        """Test detection of enrollment gaps."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))
        tracker.add_event("P003", date(2024, 5, 1))  # 85-day gap
        tracker.add_event("P004", date(2024, 5, 5))
        
        gaps = tracker.detect_gaps(max_gap_days=30)
        
        assert len(gaps) == 1
        assert gaps[0][0] == date(2024, 2, 5)
        assert gaps[0][1] == date(2024, 5, 1)
        assert (gaps[0][1] - gaps[0][0]).days == 86
    
    def test_detect_gaps_multiple(self, tracker):
        """Test detection of multiple gaps."""
        tracker.add_event("P001", date(2024, 1, 1))
        tracker.add_event("P002", date(2024, 3, 1))  # 60-day gap
        tracker.add_event("P003", date(2024, 5, 1))  # 61-day gap
        tracker.add_event("P004", date(2024, 5, 5))
        
        gaps = tracker.detect_gaps(max_gap_days=30)
        
        assert len(gaps) == 2
    
    def test_detect_gaps_empty(self, tracker):
        """Test gap detection with no events."""
        gaps = tracker.detect_gaps()
        
        assert len(gaps) == 0


# ============================================================================
# Test Summary Statistics
# ============================================================================

class TestSummaryStatistics:
    """Test recruitment summary generation."""
    
    def test_get_summary_empty(self, tracker):
        """Test summary with no events."""
        summary = tracker.get_summary()
        
        assert summary['total_enrolled'] == 0
        assert summary['target_sample_size'] == 100
        assert summary['percent_complete'] == 0.0
        assert summary['first_enrollment'] is None
        assert summary['last_enrollment'] is None
    
    def test_get_summary_with_events(self, tracker):
        """Test summary with enrollments."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 10))
        tracker.add_event("P003", date(2024, 2, 20))
        
        summary = tracker.get_summary()
        
        assert summary['total_enrolled'] == 3
        assert summary['target_sample_size'] == 100
        assert summary['percent_complete'] == 3.0
        assert summary['first_enrollment'] == "2024-02-01"
        assert summary['last_enrollment'] == "2024-02-20"
        assert summary['duration_days'] == 19
        assert summary['avg_patients_per_month'] > 0


# ============================================================================
# Test Forecasting
# ============================================================================

class TestForecasting:
    """Test completion date forecasting."""
    
    def test_forecast_insufficient_data_raises_error(self, tracker):
        """Test forecast with too few events."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))
        
        with pytest.raises(ValidationError, match="Insufficient data"):
            tracker.forecast_completion()
    
    def test_forecast_with_linear_trend(self, tracker):
        """Test linear forecasting."""
        # Add 20 patients over 40 days (~0.5 patients/day = 15/month)
        # Target is 100, so need 80 more → ~160 more days
        start = date(2024, 2, 1)
        for i in range(20):
            tracker.add_event(f'P{i+1:03d}', start + timedelta(days=i*2))
        
        forecast = tracker.forecast_completion()
        
        assert 'predicted_completion_date' in forecast
        assert 'confidence_interval_days' in forecast
        assert 'current_velocity' in forecast
        assert forecast['patients_remaining'] == 80
        assert forecast['status'] == 'active'
    
    def test_forecast_already_completed(self, valid_project):
        """Test forecast when target already reached."""
        # Create tracker with low target
        valid_project.target_sample_size = 5
        tracker = RecruitmentTracker(valid_project)
        
        # Enroll more than target
        start = date(2024, 2, 1)
        for i in range(10):
            tracker.add_event(f'P{i+1:03d}', start + timedelta(days=i))
        
        forecast = tracker.forecast_completion()
        
        assert forecast['status'] == 'completed'
        assert forecast['patients_remaining'] == 0
        assert forecast['days_remaining'] == 0


# ============================================================================
# Test On-Track Status
# ============================================================================

class TestOnTrackStatus:
    """Test enrollment timeline adherence."""
    
    def test_is_on_track_with_no_events(self, tracker):
        """Test on-track with no data."""
        assert tracker.is_on_track() is True
    
    def test_is_on_track_within_tolerance(self, valid_project):
        """Test on-track when enrollment is on schedule."""
        # Project: Jan 1 - Jan 1 next year, 100 patients
        tracker = RecruitmentTracker(valid_project)
        
        # After 6 months (182 days), expect ~50 patients
        # Add 48 patients (within 10% tolerance)
        start = valid_project.first_patient_date
        for i in range(48):
            tracker.add_event(f'P{i+1:03d}', start + timedelta(days=i*4))
        
        assert tracker.is_on_track(tolerance=0.10) is True
    
    def test_is_on_track_outside_tolerance(self, valid_project):
        """Test on-track when enrollment is behind schedule."""
        tracker = RecruitmentTracker(valid_project)
        
        # After 182 days, should have ~50 patients
        # Add only 20 (40% below expected)
        start = valid_project.first_patient_date
        for i in range(20):
            tracker.add_event(f'P{i+1:03d}', start + timedelta(days=i*9))
        
        assert tracker.is_on_track(tolerance=0.10) is False


# ============================================================================
# Test Persistence (Save/Load)
# ============================================================================

class TestPersistence:
    """Test saving and loading recruitment logs."""
    
    def test_save_creates_json_file(self, tracker, temp_project_dir):
        """Test save creates recruitment_log.json."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))
        
        tracker.save(temp_project_dir)
        
        log_file = temp_project_dir / "recruitment_log.json"
        assert log_file.exists()
    
    def test_save_includes_all_events(self, tracker, temp_project_dir):
        """Test saved file contains all events."""
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))
        tracker.add_event("P003", date(2024, 2, 10))
        
        tracker.save(temp_project_dir)
        
        log_file = temp_project_dir / "recruitment_log.json"
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        assert len(data['events']) == 3
        assert data['events'][0]['patient_id'] == 'P001'
        assert data['summary']['total_enrolled'] == 3
    
    def test_load_restores_events(self, tracker, temp_project_dir, valid_project):
        """Test load restores all events."""
        # Add and save events
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))
        tracker.save(temp_project_dir)
        
        # Create new tracker and load
        new_tracker = RecruitmentTracker(valid_project)
        count = new_tracker.load(temp_project_dir)
        
        assert count == 2
        assert len(new_tracker.events) == 2
        assert new_tracker.events[0].patient_id == "P001"
        assert new_tracker.events[1].patient_id == "P002"
    
    def test_load_nonexistent_file_raises_error(self, tracker, temp_project_dir):
        """Test load from nonexistent file."""
        with pytest.raises(DataLoadError, match="not found"):
            tracker.load(temp_project_dir)
    
    def test_save_load_roundtrip(self, tracker, temp_project_dir, valid_project):
        """Test save/load preserves all data."""
        # Add events
        tracker.add_event("P001", date(2024, 2, 1))
        tracker.add_event("P002", date(2024, 2, 5))
        tracker.add_event("P003", date(2024, 2, 10))
        
        # Get original timeline
        original_timeline = tracker.get_timeline()
        
        # Save and load
        tracker.save(temp_project_dir)
        new_tracker = RecruitmentTracker(valid_project)
        new_tracker.load(temp_project_dir)
        
        # Compare
        assert len(new_tracker.events) == len(tracker.events)
        
        restored_timeline = new_tracker.get_timeline()
        assert len(restored_timeline) == len(original_timeline)
        assert restored_timeline['cumulative_enrolled'].iloc[-1] == 3


# ============================================================================
# Test Integration Scenarios
# ============================================================================

class TestIntegration:
    """Test complete workflows."""
    
    def test_complete_workflow(self, tracker, sample_enrollment_data, temp_project_dir):
        """Test end-to-end recruitment tracking workflow."""
        # 1. Process dataset
        count = tracker.process_dataset(
            sample_enrollment_data,
            date_column='enrollment_date',
            id_column='patient_id'
        )
        assert count == 50
        
        # 2. Get timeline
        timeline = tracker.get_timeline()
        assert len(timeline) > 0
        assert timeline['cumulative_enrolled'].iloc[-1] == 50
        
        # 3. Calculate velocity
        velocity = tracker.calculate_velocity()
        assert velocity > 0
        
        # 4. Get summary
        summary = tracker.get_summary()
        assert summary['total_enrolled'] == 50
        assert summary['percent_complete'] == 50.0
        
        # 5. Forecast completion
        forecast = tracker.forecast_completion()
        assert forecast['patients_remaining'] == 50
        assert forecast['status'] == 'active'
        
        # 6. Save
        tracker.save(temp_project_dir)
        
        # 7. Load in new tracker
        from hamelin.core.project import create_sample_project
        new_project = create_sample_project()
        new_project.target_sample_size = 100
        new_tracker = RecruitmentTracker(new_project)
        new_tracker.load(temp_project_dir)
        
        assert len(new_tracker.events) == 50
    
    def test_realistic_enrollment_scenario(self, valid_project):
        """Test realistic enrollment pattern."""
        tracker = RecruitmentTracker(valid_project)
        
        # Simulate realistic enrollment:
        # - Slow start (1-2 per week)
        # - Ramp up (3-5 per week)
        # - Steady state (5-7 per week)
        
        start = date(2024, 1, 15)
        current_date = start
        
        # Phase 1: Slow (4 weeks, 6 patients)
        for i in range(6):
            tracker.add_event(f'P{i+1:03d}', current_date)
            current_date += timedelta(days=4)
        
        # Phase 2: Ramp up (8 weeks, 30 patients)
        for i in range(30):
            tracker.add_event(f'P{i+7:03d}', current_date)
            current_date += timedelta(days=2)
        
        # Phase 3: Steady (12 weeks, 64 patients)
        for i in range(64):
            tracker.add_event(f'P{i+37:03d}', current_date)
            current_date += timedelta(days=1)
        
        # Total: 100 patients enrolled
        assert len(tracker.events) == 100
        
        # Should be at target
        forecast = tracker.forecast_completion()
        assert forecast['status'] == 'completed'
