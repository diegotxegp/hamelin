"""
Analytics Module
~~~~~~~~~~~~~~~~

Statistical analysis and data processing tools for clinical research.

Modules:
    - table1_generator: Automated baseline characteristics tables
    - recruitment_tracker: Patient enrollment tracking and forecasting
"""

from .table1_generator import Table1Generator
from .recruitment_tracker import RecruitmentEvent, RecruitmentTracker

__all__ = [
    'Table1Generator',
    'RecruitmentEvent',
    'RecruitmentTracker',
]
