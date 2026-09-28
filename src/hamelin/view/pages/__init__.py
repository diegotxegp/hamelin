"""
UI Pages Package
~~~~~~~~~~~~~~~~

Contains all application pages/views.
"""

from .home_page import HomePage
from .table1_page import Table1Page
from .metadata_page import MetadataPage
from .data_page import DataPage
from .forecasting_page import ForecastingPage
from .training_page import TrainingPage
from .dashboard_page import DashboardPage
from .settings_page import SettingsPage

__all__ = [
    'HomePage',
    'Table1Page',
    'MetadataPage',
    'DataPage',
    'ForecastingPage',
    'TrainingPage',
    'DashboardPage',
    'SettingsPage'
]
