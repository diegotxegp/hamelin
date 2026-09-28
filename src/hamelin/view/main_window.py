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
    ForecastingPage, TrainingPage, DashboardPage, SettingsPage
)
from hamelin.view.pages.help_page import HelpPage
from hamelin.core.project import ProjectRepository
from hamelin.analytics.variable_analyzer import prewarm_ludwig_type_inference
from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log, PAGE_DISPLAY_NAMES
from hamelin.utils.config_manager import config
from hamelin.utils.theme_colors import on_theme_changed, tooltip_qss
from hamelin.i18n import t


class _LazyPage(QWidget):
    """Placeholder added to the nav bar in its real, final slot right away
    (via addSubInterface, same as every other page) so the "Models" item
    never has to be removed and re-added later - re-adding it would append
    it to the end of the nav bar instead of leaving it where it started,
    which is what made it visibly jump down the sidebar on first click.

    *on_show* is called every time this page becomes visible (not just the
    first time - see _open_interface_page's own docstring for why the
    heavy one-time setup and the cheap per-visit refresh live in the same
    method there) and does the actual lazy loading of content into this
    widget.
    """

    def __init__(self, on_show, parent=None):
        super().__init__(parent)
        self._on_show = on_show

    def showEvent(self, event):
        super().showEvent(event)
        self._on_show()


class MainWindow(MSFluentWindow):
    """
    Main application window.

    Features:
    - Navigation sidebar with progressive enablement
    - 7 pages: Home, Project, Data (includes Table 1), Training, Models,
      Forecasting, Help, Settings. Dashboard is temporarily out of the nav
      (see _init_navigation) - the page and its state still exist, just
      not reachable from the sidebar.
    - Guided workflow: Project → Data → Analysis (tabs unlock as prerequisites are met)
    - Modern Fluent Design
    """
    
    def __init__(self):
        super().__init__()
        log.info("Initializing Main Window")

        # Pays Ludwig's automl-module import cost (tens of seconds - it
        # pulls in most of Ludwig's schema/encoder/decoder registry, see
        # prewarm_ludwig_type_inference()'s docstring) in the background
        # instead of on the user's first dataset load in the Data page.
        # Deferred via QTimer.singleShot(0, ...) rather than started here
        # directly: a plain Python thread still contends for the GIL with
        # this constructor's own synchronous page-building work (and
        # _auto_load_project()'s disk I/O right after it), which was
        # slowing down Home's very first paint. singleShot(0) only fires
        # once Qt's event loop is actually running (after __init__ returns
        # and the window is already shown), not synchronously here.
        QTimer.singleShot(
            0, lambda: threading.Thread(target=prewarm_ludwig_type_inference, daemon=True).start()
        )

        # Window properties
        self.setWindowTitle(t("home.title"))

        # QToolTip is native/unstyled everywhere in this app otherwise -
        # see tooltip_qss()'s docstring. Applied once, app-wide, and kept
        # in sync with Settings > Theme for the rest of this window's life.
        on_theme_changed(lambda: QApplication.instance().setStyleSheet(tooltip_qss()))


        # Get window size from config
        width = config.get('ui.window.width', 1400)
        height = config.get('ui.window.height', 900)
        self.resize(width, height)
        
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
        self.metadata_page = MetadataPage(self)
        self.settings_page = SettingsPage(self)
        self.help_page = HelpPage(self)
        
        # Connect DataModel sharing between pages
        self.data_page.data_loaded.connect(self._on_data_loaded)
        # Share project metadata with ForecastingPage and DashboardPage when saved or opened
        self.metadata_page.metadata_saved.connect(self._on_metadata_saved)
        self.metadata_page.project_loaded.connect(self._on_project_loaded)
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
            self._open_interface_page
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

        # "Models" opens the standalone "interface" model comparison/
        # visualisation tool. Its content is heavy to build (imports the
        # interface codebase, needs a project open) so it's loaded lazily
        # on first visit - see _open_interface_page - but the nav item
        # itself is a real addSubInterface() page from the start, added
        # once in this exact slot, so it never moves in the sidebar.
        self.models_page = _LazyPage(self._open_interface_page)
        self.models_page.setObjectName("modelsPage")
        self.addSubInterface(
            self.models_page,
            FluentIcon.VIEW,
            t("nav.models")
        )

        # Dashboard: removed from the nav for now (its useful bits -
        # timestamps, provenance, notes - are moving into the Models page
        # instead; see hamelin_integration_notes.md). dashboard_page itself
        # still exists and is kept up to date via set_data_model() etc.
        # below, just not reachable from the sidebar.

        self.addSubInterface(
            self.forecasting_page,
            FluentIcon.HISTORY,
            t("nav.forecasting")
        )

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

        log.debug("Navigation initialized with 7 pages")

    # ======================================================================
    # EMBEDDED "INTERFACE" DASHBOARD (model comparison / visualisation tool)
    # ======================================================================

    def _open_interface_page(self) -> None:
        """
        Lazily load and show the embedded "interface" dashboard
        (hamelin.interface, see hamelin/interface/app.py) as a
        normal embedded page - same as every other page, Hamelin's own
        side nav stays visible and "Models" stays highlighted while it's
        showing.

        interface's own pages were built assuming they own the full
        window: its popups/cards position themselves from ITS OWN widget's
        current width/height (not the screen's), so squeezed into a
        narrower space that math still places everything correctly inside
        it - but several of its rows are laid out with fixed pixel-width
        buttons/cards that don't shrink, so the row's own natural width can
        end up wider than what's actually available next to Hamelin's nav.
        Wrapped in a QScrollArea (below) so that specific case degrades to
        a horizontal scrollbar instead of clipping or overlapping content,
        without having to rework interface's own widgets to be responsive.
        No in-page "Back to Hamelin" button - now that this is a normal
        nav page, leaving it is just clicking any other nav item.

        Loaded on first use rather than at startup so a problem in that
        codebase can't prevent Hamelin itself from launching.

        interface's own model scan is pointed at THIS project's
        model_checkpoints/ folder (see TrainingPage._on_training_finished,
        which saves one named subfolder per completed run there - NOT
        ludwig_runs/, which is just Ludwig's own internal hyperopt trial
        dump, not meant for browsing) every time this is called, not just
        on first load - otherwise switching to a different Hamelin project
        and reopening Models would keep showing whichever project (or
        interface's own unrelated "./results" dev fixtures, if no project
        had been opened yet the first time) was current the very first
        time Models was ever opened this session.
        """
        from pathlib import Path

        project_dir = self.training_page._project_dir
        if project_dir is None:
            InfoBar.warning(
                title="No project", content="Open a project first.",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            return
        results_dir = str(Path(project_dir) / "model_checkpoints")

        first_load = getattr(self, "interface_page", None) is None
        if first_load:
            try:
                from hamelin.interface.app import MainWindow as InterfaceMainWindow
                import hamelin.interface.utils.get_model_paths as interface_gmp
                from hamelin.interface.utils.theme_state import theme_state as interface_theme
            except Exception as exc:
                log.error(f"Failed to load the interface dashboard: {exc}", exc_info=True)
                return

            self._interface_gmp = interface_gmp
            self._interface_theme = interface_theme
            interface_theme.set_dark(isDarkTheme())
            qconfig.themeChanged.connect(
                lambda *_: interface_theme.set_dark(isDarkTheme())
            )
            # Before constructing InterfaceMainWindow - LandingPage reads
            # this during its own __init__ (for the "N models available"
            # badge), so it has to already be correct by the time that runs.
            self._interface_gmp.RESULTS_DIR = results_dir
            self.interface_page = InterfaceMainWindow()

            # "Duplicate a model" hands over a tweaked Ludwig config; bring
            # our own Training page forward, pre-filled from it. Nothing is
            # saved until the user actually trains.
            self.interface_page.duplicate_model.open_training_requested.connect(
                self._prefill_training_from_duplicate
            )

            # Scroll container - see the docstring above for why. Not
            # setWidgetResizable(False): that would leave interface_page
            # pinned to its natural size permanently (always scrolling,
            # even with room to spare); True makes it fill the available
            # space and only fall back to scrollbars once its content
            # can't shrink any further.
            self.interface_scroll = QScrollArea()
            self.interface_scroll.setWidget(self.interface_page)
            self.interface_scroll.setWidgetResizable(True)
            self.interface_scroll.setFrameShape(QScrollArea.Shape.NoFrame)

            # A bare margin, not just cosmetic: MSFluentWindow is a
            # frameless window, and on Linux its own resize-grip hit-test
            # zone is the outer 5px of the whole window (see
            # qframelesswindow.linux.LinuxFramelessWindowBase.BORDER_WIDTH)
            # - without this margin, interface_scroll's own vertical
            # scrollbar sits flush against that edge, so trying to grab it
            # shows a resize cursor and drags the window instead of
            # scrolling. Every other Hamelin page already clears this
            # zone via its own ~30px content margins; interface_scroll had
            # none of its own.
            #
            # Content goes straight into models_page (the real nav page
            # added once in _init_navigation) instead of a separate
            # container swapped in via addSubInterface - that swap used to
            # remove the "models" nav item and re-add it, which appended it
            # to the end of the sidebar instead of leaving it where it was.
            container_layout = QVBoxLayout(self.models_page)
            container_layout.setContentsMargins(0, 0, 8, 8)
            container_layout.addWidget(self.interface_scroll)
            log.info("Interface dashboard loaded")

        # Every call, not just first_load - see the docstring above.
        self._interface_gmp.RESULTS_DIR = results_dir
        # interface_page itself is only ever built once (first_load), so
        # its landing page's "N models available" badge (set once in its
        # own __init__) needs an explicit nudge to reflect a project
        # switched to *after* that - everything else keyed off
        # gmp.get_model_names() re-reads it live when shown instead.
        if not first_load:
            self.interface_page.landing._refresh_model_badge()

        # interface's own pages are laid out assuming plenty of room (its
        # own standalone launch always opens showMaximized() - see
        # interface/app.py's __main__ block) - giving Hamelin's window the
        # same real estate here is what makes the embedded page look the
        # same as that, instead of needing the QScrollArea's fallback
        # scrollbars for room a maximized window would have had anyway.
        if not self.isMaximized():
            self.showMaximized()

    def _prefill_training_from_duplicate(self, payload: dict) -> None:
        """Bridge the embedded dashboard's "duplicate a model" flow to the
        Training page: pre-fill it from the handed-over Ludwig config and
        bring it to the front. Nothing is saved until the user trains."""
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
        for name, call in [
            ("forecasting_page", lambda: self.forecasting_page.set_project_metadata(metadata)),
            ("dashboard_page",   lambda: self.dashboard_page.set_project_metadata(metadata)),
            ("table1_metadata",  lambda: self.data_page.table1_section.set_project_metadata(metadata)),
            ("dashboard_load",   lambda: self.dashboard_page.load_project(str(project_dir)) if project_dir else None),
            ("training_page",    lambda: self.training_page.set_project_dir(project_dir) if project_dir else None),
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
                if project_dir:
                    self.dashboard_page.load_project(str(project_dir))
                    self.training_page.set_project_dir(project_dir)
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

    def _log_page_navigation(self, index: int) -> None:
        """Record every page switch in the usability CSV log, whatever
        triggered it (nav bar click, back link, auto-load, ...)."""
        widget = self.stackedWidget.widget(index)
        if widget is None:
            return
        page_name = PAGE_DISPLAY_NAMES.get(widget.objectName(), widget.objectName())
        usage_log.event(page_name, "navigate", "page opened")

    def _on_training_finished(self, result) -> None:
        """
        Called when TrainingPage finishes a training run.
        Refreshes the history widgets and the Dashboard.
        """
        project_dir = self.training_page._project_dir
        if project_dir:
            self.training_page.refresh_history(project_dir)
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
        
        # Save window size to config
        config.set('ui.window.width', self.width())
        config.set('ui.window.height', self.height())
        
        # Accept close event
        event.accept()
        log.info("Main Window closed successfully")
