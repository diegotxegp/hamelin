"""
Custom Widgets Package
~~~~~~~~~~~~~~~~~~~~~~

Reusable custom widgets for HAMELIN UI.
"""

from .help_button import HelpButton, SectionHeader
from .kpi_card_widget import KPICardWidget
from .model_history_widget import ModelHistoryWidget
from .model_results_widget import ModelResultsWidget
from .page_help import PageHelpButton, attach_help_popup, attach_help_popup_hover
from .arrow_cursor_filter import ArrowCursorFilter
from .wheel_guard import WheelGuard
from .recruitment_chart_widget import RecruitmentChartWidget
from .table_theme import style_table_widget
from .theme_colors import apply_scroll_area_theme, bind_style, colors, list_item_qss, on_theme_changed
from .training_timeline_widget import TrainingTimelineWidget

__all__ = [
    'HelpButton', 'SectionHeader',
    'KPICardWidget',
    'ModelHistoryWidget', 'ModelResultsWidget',
    'PageHelpButton', 'attach_help_popup', 'attach_help_popup_hover',
    'ArrowCursorFilter', 'WheelGuard',
    'RecruitmentChartWidget', 'style_table_widget',
    'apply_scroll_area_theme', 'bind_style', 'colors', 'list_item_qss', 'on_theme_changed',
    'TrainingTimelineWidget',
]
