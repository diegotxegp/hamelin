"""
Main Window
~~~~~~~~~~~

Main application window with navigation and page management.
"""

import threading

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QScrollArea
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon
from qfluentwidgets import (
    FluentWindow, NavigationInterface, NavigationItemPosition,
    FluentIcon, MSFluentWindow, SplashScreen, InfoBar, InfoBarPosition,
    isDarkTheme, qconfig
)

from hamelin.view.pages import (
    HomePage, MetadataPage, DataPage,
    ForecastingPage, TrainingPage, EvaluationPage, PredictionPage,
    DashboardPage, SettingsPage
)
from hamelin.view.pages.help_page import HelpPage
from hamelin.core.project import ProjectRepository
from hamelin.core.project_layout import tidy_project
from hamelin.analytics.variable_analyzer import prewarm_ludwig_type_inference
from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log, PAGE_DISPLAY_NAMES
from hamelin.utils.config_manager import config
from hamelin.utils.theme_colors import apply_tooltip_theme, on_theme_changed
from hamelin.i18n import t


# Pages that are visible but not yet available to end users (Prediction, Forecasting).
LOCKED_PAGES = True


class MainWindow(MSFluentWindow):
    """
    Main application window.

    Features:
    - Navigation sidebar with progressive enablement
    - 9 pages: Home, Project, Data (includes Table 1), Training, Evaluation,
      Prediction, Forecasting, Help, Settings. Dashboard is temporarily out of the nav
      (see _init_navigation) - the page and its state still exist, just
      not reachable from the sidebar.
    - Guided workflow: Project → Data → Analysis (tabs unlock as prerequisites are met)
    - Modern Fluent Design
    """
    
    def __init__(self):
        super().__init__()
        log.info("Initializing Main Window")

        # Ludwig's automl module costs seconds to import (see
        # prewarm_ludwig_type_inference()).  Doing that at launch made the
        # whole UI sluggish (the import thread competes for the GIL), so it
        # is started only when the user opens the Data or Training page -
        # i.e. shortly before a dataset is loaded - see _log_page_navigation.
        self._ludwig_prewarmed = False

        # Window properties
        self.setWindowTitle(t("home.title"))

        # QToolTip is native/unstyled everywhere in this app otherwise -
        # see tooltip_qss()'s docstring. Applied once, app-wide, and kept
        # in sync with Settings > Theme for the rest of this window's life.
        on_theme_changed(apply_tooltip_theme)


        # Get window size from config
        width = config.get('ui.window.width', 1400)
        height = config.get('ui.window.height', 900)
        # Comfortably inside the usable screen, not flush with it: the OS
        # adds its own title bar and borders around the window (and a
        # remote/WSL desktop adds more), so a window exactly as big as the
        # screen still hangs off its bottom and right edges. On a 1366x768
        # laptop this gives about 1284x691 instead of 1400x900; the user can
        # maximize, and that is remembered (see closeEvent).
        screen = QApplication.primaryScreen()
        if screen is not None:
            avail = screen.availableGeometry()
            width = min(width, int(avail.width() * 0.94))
            height = min(height, int(avail.height() * 0.90))
        self.resize(width, height)
        # Reopen maximized if that is how it was closed (see closeEvent).
        self._start_maximized = bool(config.get('ui.window.maximized', False))
        
        # Application state for progressive enablement
        # TODO: uncomment for production to activate guided workflow
        # self.project_configured = False
        # self.data_loaded = False
        # self.primary_variable_selected = False
        # self.recruitment_metadata_set = False

        # Initialize UI
        self._init_pages()
        self._init_navigation()
        # self._update_navigation_state()  # TODO: enable for production

        # Central usage-log hook: fires for every page switch regardless of
        # which nav button/method triggered it, so individual pages don't
        # each need their own "I was opened" logging.
        self.stackedWidget.currentChanged.connect(self._log_page_navigation)

        # Show splash screen
        self._show_splash()

        # Auto-load the project if there is exactly one saved
        self._auto_load_project()

        log.info("Main Window initialized successfully")
    
    def _init_pages(self):
        """Initialize all pages"""
        log.debug("Initializing pages")
        
        # Create pages
        self.home_page = HomePage(self)
        self.dashboard_page = DashboardPage(self)
        # Not in the nav, so nothing lays it out: left visible it sits at
        # (0, 0) with the default 100x30 size, on top of the title bar.
        self.dashboard_page.hide()
        self.data_page = DataPage(self)
        self.forecasting_page = ForecastingPage(self)
        self.training_page = TrainingPage(self)
        self.evaluation_page = EvaluationPage(self)
        self.prediction_page = PredictionPage(self)
        self.metadata_page = MetadataPage(self)
        self.settings_page = SettingsPage(self)
        self.help_page = HelpPage(self)
        
        # Connect DataModel sharing between pages
        self.data_page.data_loaded.connect(self._on_data_loaded)
        # Share project metadata with ForecastingPage and DashboardPage when saved or opened
        self.metadata_page.metadata_saved.connect(self._on_metadata_saved)
        self.metadata_page.project_loaded.connect(self._on_project_loaded)
        self.metadata_page.all_projects_deleted.connect(self.home_page.update_stats)
        # Forecasting → Dashboard live wiring: tracker_ready carries the live
        # RecruitmentTracker after each forecast run.
        self.forecasting_page.tracker_ready.connect(self.dashboard_page.set_tracker)
        # Dashboard quick-action navigation
        self.dashboard_page.navigate_to_data.connect(
            lambda: self.switchTo(self.data_page)
        )
        self.dashboard_page.navigate_to_training.connect(
            lambda: self.switchTo(self.training_page)
        )
        self.dashboard_page.navigate_to_interface.connect(
            lambda: self.switchTo(self.evaluation_page)
        )
        # "Duplicate & Retrain" on the Evaluation page → pre-filled Training page
        self.evaluation_page.duplicate_requested.connect(
            self._prefill_training_from_duplicate
        )
        # When training finishes, refresh history widgets and dashboard
        self.training_page.training_finished.connect(self._on_training_finished)

        log.debug("Pages created successfully")
    
    def _init_navigation(self):
        """Initialize navigation interface"""
        log.debug("Initializing navigation")
        
        # Add pages to navigation (8 pages)
        self.addSubInterface(
            self.home_page,
            FluentIcon.HOME,
            t("nav.home")
        )

        self.addSubInterface(
            self.metadata_page,
            FluentIcon.FOLDER,
            t("nav.project")
        )

        self.addSubInterface(
            self.data_page,
            FluentIcon.FOLDER_ADD,
            t("nav.data")
        )

        # Table 1 (nav.table1) is now a section inside DataPage rather than
        # its own nav entry - it's just another view over the same dataset.
        self.addSubInterface(
            self.training_page,
            FluentIcon.ROBOT,
            t("nav.training")
        )

        # Evaluation (inspect/compare/duplicate trained models) and Prediction
        # (run a trained model on new, unlabeled data) follow Training.
        self.addSubInterface(
            self.evaluation_page,
            FluentIcon.VIEW,
            t("nav.evaluation")
        )

        self._lock_nav_item(self.addSubInterface(
            self.prediction_page,
            FluentIcon.PLAY,
            t("nav.prediction")
        ))

        # Dashboard: removed from the nav for now (its useful bits -
        # timestamps, provenance, notes - are moving into the Evaluation page
        # instead; see hamelin_integration_notes.md). dashboard_page itself
        # still exists and is kept up to date via set_data_model() etc.
        # below, just not reachable from the sidebar.

        self._lock_nav_item(self.addSubInterface(
            self.forecasting_page,
            FluentIcon.HISTORY,
            t("nav.forecasting")
        ))

        # Help and settings at bottom.
        self.addSubInterface(
            self.help_page,
            FluentIcon.HELP,
            t("nav.help"),
            position=NavigationItemPosition.BOTTOM
        )

        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            t("nav.settings"),
            position=NavigationItemPosition.BOTTOM
        )

        log.debug("Navigation initialized with 9 pages")

    def _lock_nav_item(self, item) -> None:
        """Grey out a navigation entry whose page is not available yet.

        The pages stay in the code base (and are fully tested); flipping
        ``LOCKED_PAGES`` off re-enables them.
        """
        if not LOCKED_PAGES or item is None:
            return
        item.setEnabled(False)
        item.setToolTip(t("nav.locked"))

    def _prefill_training_from_duplicate(self, payload: dict) -> None:
        """Bridge the Evaluation page's "Duplicate & Retrain" to the Training
        page: pre-fill it from the handed-over Ludwig config and bring it to
        the front. Nothing is saved until the user trains."""
        self.training_page.prefill_from_config(payload)
        self.switchTo(self.training_page)

    # ======================================================================
    # PROGRESSIVE ENABLEMENT
    # ======================================================================

    def _update_navigation_state(self):
        """
        Enable / disable nav items to guide the user through the workflow:

            Project (always) → Data (includes Table 1) / Training → Forecasting

        Uses a best-effort approach: if the qfluentwidgets internal API
        doesn't return the expected item object the call is silently skipped
        and all items remain enabled (fail-open, not fail-closed).
        """
        self._set_nav_enabled(self.data_page, self.project_configured)
        self._set_nav_enabled(self.training_page, self.data_loaded)
        self._set_nav_enabled(self.forecasting_page, self.recruitment_metadata_set)
        log.debug(
            f"Nav state — project={self.project_configured}, "
            f"data={self.data_loaded}, recruitment={self.recruitment_metadata_set}"
        )

    def _set_nav_enabled(self, page_widget: QWidget, enabled: bool) -> None:
        """Silently enable/disable a navigation item by its page widget."""
        try:
            item = self.navigationInterface.widget(page_widget.objectName())
            if item is not None:
                item.setEnabled(enabled)
        except Exception:  # noqa: BLE001
            pass  # fail-open: item stays enabled if API is unavailable

    def enable_data_page(self) -> None:
        """Unlock the Data tab — called once a project has been configured."""
        self.project_configured = True
        self._update_navigation_state()
        log.info("Data page enabled — project configured")

    def enable_analysis_pages(self) -> None:
        """Unlock Table 1 and Training tabs — called once a dataset is loaded."""
        self.data_loaded = True
        self._update_navigation_state()
        log.info("Analysis pages enabled — data loaded")

    def enable_forecasting_page(self) -> None:
        """Unlock Forecasting tab — called once recruitment metadata is set."""
        self.recruitment_metadata_set = True
        self._update_navigation_state()
        log.info("Forecasting page enabled — recruitment metadata set")

    # ======================================================================
    # END PROGRESSIVE ENABLEMENT
    # ======================================================================

    def _on_data_loaded(self):
        """
        Called when DataPage successfully loads a dataset.
        Passes the shared DataModel to every page that needs it so the
        user does not have to load the same file twice.
        """
        import os
        dm = self.data_page.get_data_model()
        if dm is None:
            return
        filepath = self.data_page.file_path_edit.text()
        label = os.path.basename(filepath) if filepath else "loaded dataset"
        # Table 1 is embedded inside DataPage itself, which keeps it in
        # sync directly - no forwarding needed here.
        self.forecasting_page.set_data_model(dm)
        self.dashboard_page.set_data_model(dm)
        self.training_page.set_data_model(dm)
        # self.enable_analysis_pages()  # TODO: enable for production
        log.info(f"DataModel shared with ForecastingPage, DashboardPage, TrainingPage: {label}")

    def _on_metadata_saved(self):
        """
        Called when MetadataPage saves a project.
        Forwards the current metadata to ForecastingPage and DashboardPage.
        """
        metadata = self.metadata_page.get_current_metadata()
        if metadata is None:
            return
        # ProjectMetadata has no "project_dir" attribute (never has - it
        # only tracks short_name), so this used to silently fall through
        # to the bare short_name string ("A") instead of the real
        # Projects/A folder. Path("A") then resolves relative to wherever
        # the process happened to be launched from, so every training run,
        # ModelHistory entry, and Ludwig output ended up scattered in a
        # throwaway "./A/" directory that nothing else in the app ever
        # reads from - training would succeed but never show up anywhere
        # (project card model counts, dashboard, etc.).
        project_dir = ProjectRepository().get_project_path(metadata.short_name)
        for name, call in [
            ("forecasting_page", lambda: self.forecasting_page.set_project_metadata(metadata)),
            ("dashboard_page",   lambda: self.dashboard_page.set_project_metadata(metadata)),
            ("table1_metadata",  lambda: self.data_page.table1_section.set_project_metadata(metadata)),
            ("home_page",        lambda: self.home_page.update_stats()),
            ("dashboard_load",   lambda: self.dashboard_page.load_project(str(project_dir)) if project_dir else None),
            ("training_page",    lambda: self.training_page.set_project_dir(project_dir) if project_dir else None),
            ("evaluation_page",  lambda: self.evaluation_page.set_project_dir(project_dir) if project_dir else None),
            ("forecasting_dir",  lambda: self.forecasting_page.set_project_dir(project_dir) if project_dir else None),
            ("prediction_page",     lambda: self.prediction_page.set_project_dir(project_dir) if project_dir else None),
            ("data_page",        lambda: self.data_page.set_project_dir(project_dir, auto_load_last=False) if project_dir else None),
        ]:
            try:
                call()
            except Exception as exc:
                log.warning(f"_on_metadata_saved: {name} failed (non-critical) — {exc}")
        # self.enable_data_page()  # TODO: enable for production
        # try:
        #     if metadata is not None and getattr(metadata, "expected_patients", None):
        #         self.enable_forecasting_page()
        # except Exception:
        #     pass
        log.info(f"Metadata shared: {metadata.short_name}")

    def _on_project_loaded(self, metadata):
        """
        Called when MetadataPage opens an existing project from the selector.
        Forwards the metadata to ForecastingPage and DashboardPage.
        """
        # See the matching comment in _on_metadata_saved - resolve the
        # real project folder instead of falling back to the bare
        # short_name string.
        project_dir = ProjectRepository().get_project_path(metadata.short_name)
        self._tidy(project_dir)
        for name, call in [
            ("forecasting_page", lambda: self.forecasting_page.set_project_metadata(metadata)),
            ("dashboard_page",   lambda: self.dashboard_page.set_project_metadata(metadata)),
            ("table1_metadata",  lambda: self.data_page.table1_section.set_project_metadata(metadata)),
            ("dashboard_load",   lambda: self.dashboard_page.load_project(str(project_dir)) if project_dir else None),
            ("training_page",    lambda: self.training_page.set_project_dir(project_dir) if project_dir else None),
            ("evaluation_page",  lambda: self.evaluation_page.set_project_dir(project_dir) if project_dir else None),
            ("forecasting_dir",  lambda: self.forecasting_page.set_project_dir(project_dir) if project_dir else None),
            ("prediction_page",     lambda: self.prediction_page.set_project_dir(project_dir) if project_dir else None),
            ("data_page",        lambda: self.data_page.set_project_dir(project_dir, auto_load_last=False) if project_dir else None),
        ]:
            try:
                call()
            except Exception as exc:
                log.warning(f"_on_project_loaded: {name} failed (non-critical) — {exc}")
        # self.enable_data_page()  # TODO: enable for production
        # try:
        #     if metadata is not None and getattr(metadata, "expected_patients", None):
        #         self.enable_forecasting_page()
        # except Exception:
        #     pass
        log.info(f"Opened project forwarded to all pages: {metadata.short_name}")

    def _auto_load_project(self):
        """
        If exactly one project exists on disk, load it automatically.
        This removes the need for the clinician to manually open it every session.
        Multiple projects → leave the selector visible so the user can choose.
        """
        try:
            from hamelin.core.project import ProjectRepository
            repo = ProjectRepository()
            projects = repo.list_projects()
            if len(projects) == 1:
                # Reuse the metadata MetadataPage already loaded while
                # building its selector cards, instead of re-reading the
                # same metadata.json from disk.
                meta = self.metadata_page._selector_meta_cache.get(projects[0])
                if meta is None:
                    meta = repo.load(projects[0])
                self.metadata_page.set_active_project(meta)
                self.forecasting_page.set_project_metadata(meta)
                self.dashboard_page.set_project_metadata(meta)
                self.data_page.table1_section.set_project_metadata(meta)
                # See the comment in _on_metadata_saved - resolve the real
                # project folder, not the bare short_name string.
                project_dir = repo.get_project_path(meta.short_name)
                self._tidy(project_dir)
                if project_dir:
                    self.dashboard_page.load_project(str(project_dir))
                    self.training_page.set_project_dir(project_dir)
                    self.evaluation_page.set_project_dir(project_dir)
                    self.forecasting_page.set_project_dir(project_dir)
                    self.prediction_page.set_project_dir(project_dir)
                    self.data_page.set_project_dir(project_dir)
                # self.enable_data_page()  # TODO: enable for production
                # try:
                #     if getattr(meta, "expected_patients", None):
                #         self.enable_forecasting_page()
                # except Exception:
                #     pass
                log.info(f"Auto-loaded single project: {meta.short_name}")
        except Exception as exc:
            log.warning(f"Auto-load project failed (non-critical): {exc}")

    def _tidy(self, project_dir) -> None:
        """Bring a just-opened project to the current folder layout and drop
        stale Ludwig trial dumps (unless a training is running right now)."""
        worker = getattr(self.training_page, "_trainer_worker", None)
        running = worker is not None and worker.isRunning()
        tidy_project(project_dir, trial_dumps=not running)

    def _log_page_navigation(self, index: int) -> None:
        """Record every page switch in the usability CSV log, whatever
        triggered it (nav bar click, back link, auto-load, ...)."""
        widget = self.stackedWidget.widget(index)
        if widget is None:
            return
        page_name = PAGE_DISPLAY_NAMES.get(widget.objectName(), widget.objectName())
        usage_log.event(page_name, "navigate", "page opened")
        if not self._ludwig_prewarmed and widget in (self.data_page, self.training_page):
            self._ludwig_prewarmed = True
            threading.Thread(target=prewarm_ludwig_type_inference, daemon=True).start()

    def _on_training_finished(self, result) -> None:
        """
        Called when TrainingPage finishes a training run.
        Refreshes the history widgets and the Dashboard.
        """
        project_dir = self.training_page._project_dir
        if project_dir:
            self.training_page.refresh_history(project_dir)
            self.evaluation_page.refresh()
            self.prediction_page.set_project_dir(project_dir)
        self.dashboard_page.refresh()
        log.info(f"MainWindow: training_finished received — {result.model_type}")

    def _show_splash(self):
        """Show splash screen on startup"""
        try:
            # Create splash screen — must call self.show() here so qfluentwidgets
            # SplashScreen can overlay the window correctly.  finish() removes the
            # overlay; without show() first the window stays hidden indefinitely.
            self._splash = SplashScreen(self.windowIcon(), self)
            self._splash.setIconSize(QSize(128, 128))
            # Show and ensure the main window is visible and centered
            self.show()
            if self._start_maximized:
                self.showMaximized()
            self.raise_()
            self.activateWindow()

            # Center on primary screen to avoid off-screen placement
            try:
                from PySide6.QtGui import QGuiApplication
                geom = self.geometry()
                screen = QGuiApplication.primaryScreen()
                if screen is not None and geom is not None:
                    sgeom = screen.availableGeometry()
                    cx = sgeom.x() + max(0, (sgeom.width() - geom.width()) // 2)
                    cy = sgeom.y() + max(0, (sgeom.height() - geom.height()) // 2)
                    self.move(cx, cy)
            except Exception:
                pass

            # Close splash after short delay
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1500, self._splash.finish)

            log.debug("Splash screen displayed")
        except Exception as e:
            log.warning(f"Could not show splash screen: {e}")
            # Best-effort fallback: ensure the window is visible
            try:
                self.show()
                self.raise_()
                self.activateWindow()
            except Exception:
                pass
    
    def closeEvent(self, event):
        """Handle window close event"""
        log.info("Main Window closing")
        
        # Remember the size (and whether it was maximized) for next launch.
        # While maximized the normal size is kept, so un-maximizing later
        # still gives back the previous window. Persisted to disk here:
        # config.set() alone only changes memory, so the size used to be
        # forgotten every time and each launch fell back to 1400x900.
        maximized = self.isMaximized()
        size = self.normalGeometry().size() if maximized else self.size()
        if size.width() > 100 and size.height() > 100:
            config.set('ui.window.width', size.width())
            config.set('ui.window.height', size.height())
        config.set('ui.window.maximized', maximized)
        try:
            config.save()
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Could not save window size: {exc}")
        
        # Leave the open project tidy: no Ludwig trial dumps, no empty folders.
        try:
            self._tidy(self.training_page._project_dir)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Could not tidy project on exit: {exc}")

        # Accept close event
        event.accept()
        log.info("Main Window closed successfully")
