"""
Settings Page
~~~~~~~~~~~~~

Application configuration and preferences.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QScrollArea, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel, CardWidget,
    PushButton, PrimaryPushButton, ComboBox, SpinBox, SwitchButton,
    Slider, FluentIcon, OptionsSettingCard, SettingCardGroup,
    ScrollArea, setTheme, Theme, InfoBar, InfoBarPosition, MessageBox
)

from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.utils.config_manager import config
from hamelin.view.widgets import HelpButton, PageHelpButton
from hamelin.view.widgets.theme_colors import apply_scroll_area_theme, bind_style
from hamelin.i18n import t, set_language


class SettingsPage(QWidget):
    """
    Settings and configuration page.
    
    Allows users to:
    - Change theme (light/dark)
    - Adjust font size
    - Set language preferences
    - Configure export options
    - Adjust advanced settings
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage")
        log.debug("Initializing Settings Page")
        self._init_ui()
    
    def _init_ui(self):
        """Initialize user interface"""
        # Outer scroll so all settings are reachable at any window height
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)
        # Make the scroll area transparent so the app's real (theme-aware)
        # background shows through instead of QScrollArea's own opaque,
        # theme-blind palette background.
        apply_scroll_area_theme(scroll)
        container.setStyleSheet("background: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        page_title_row = QHBoxLayout()
        title = TitleLabel(t("nav.settings"))
        title.setAlignment(Qt.AlignLeft)
        page_title_row.addWidget(title)
        page_title_row.addWidget(PageHelpButton(t("settings.help"), self))
        page_title_row.addStretch()
        layout.addLayout(page_title_row)
        
        # Subtitle
        subtitle = StrongBodyLabel(t("settings.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Appearance Settings
        appearance_card = CardWidget()
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setContentsMargins(20, 20, 20, 20)
        appearance_layout.setSpacing(15)
        
        # Section header with help
        title_row = QHBoxLayout()
        appearance_title = StrongBodyLabel(t("settings.section.appearance"))
        title_row.addWidget(appearance_title)
        help_btn = HelpButton(t("help.settings.appearance"))
        title_row.addWidget(help_btn)
        title_row.addStretch()
        appearance_layout.addLayout(title_row)
        
        appearance_form = QFormLayout()
        appearance_form.setSpacing(10)
        
        # Theme selector
        self._theme_combo = ComboBox()
        self._theme_combo.addItems([t("settings.theme.light"), t("settings.theme.dark"), t("settings.theme.auto")])
        self._theme_combo.setCurrentText(config.get('ui.theme', 'light').capitalize())
        self._theme_combo.currentTextChanged.connect(self._on_theme_changed)
        appearance_form.addRow(t("settings.label.theme.label"), self._theme_combo)
        
        # Font size
        self._font_size_spin = SpinBox()
        self._font_size_spin.setRange(8, 16)
        self._font_size_spin.setValue(config.get('ui.font.size', 10))
        self._font_size_spin.valueChanged.connect(self._on_font_size_changed)
        appearance_form.addRow(t("settings.label.font.size"), self._font_size_spin)
        
        appearance_layout.addLayout(appearance_form)
        layout.addWidget(appearance_card)
        
        # Language Settings
        language_card = CardWidget()
        language_layout = QVBoxLayout(language_card)
        language_layout.setContentsMargins(20, 20, 20, 20)
        language_layout.setSpacing(15)
        
        language_title = StrongBodyLabel(t("settings.section.language"))
        language_layout.addWidget(language_title)
        
        lang_form = QFormLayout()
        lang_form.setSpacing(10)
        
        self._lang_combo = ComboBox()
        self._lang_combo.addItems(["English", "Español"])
        # Initialize to current language from config
        current_lang = config.get("app.language", "en")
        current_lang_display = "Español" if current_lang == "es" else "English"
        self._lang_combo.setCurrentText(current_lang_display)
        self._lang_combo.currentTextChanged.connect(self._on_language_changed)
        lang_form.addRow(t("settings.label.ui.language"), self._lang_combo)
        
        language_layout.addLayout(lang_form)
        layout.addWidget(language_card)
        
        # Export Preferences
        export_card = CardWidget()
        export_layout = QVBoxLayout(export_card)
        export_layout.setContentsMargins(20, 20, 20, 20)
        export_layout.setSpacing(15)
        
        # Section header with help
        title_row = QHBoxLayout()
        export_title = StrongBodyLabel(t("settings.section.export"))
        title_row.addWidget(export_title)
        help_btn = HelpButton(t("help.settings.export"))
        title_row.addWidget(help_btn)
        title_row.addStretch()
        export_layout.addLayout(title_row)
        
        export_form = QFormLayout()
        export_form.setSpacing(10)

        # Default format setting removed - it never did anything (no
        # handler wired it to any actual export). The format is now
        # chosen directly at the point of export instead (Data page,
        # next to the Export button), where it actually applies.

        # Decimal places
        self._decimals_spin = SpinBox()
        self._decimals_spin.setRange(0, 6)
        self._decimals_spin.setValue(2)
        export_form.addRow(t("settings.label.decimals"), self._decimals_spin)
        
        export_layout.addLayout(export_form)
        layout.addWidget(export_card)
        
        # Advanced Options
        advanced_card = CardWidget()
        advanced_layout = QVBoxLayout(advanced_card)
        advanced_layout.setContentsMargins(20, 20, 20, 20)
        advanced_layout.setSpacing(15)
        
        advanced_title = StrongBodyLabel(t("settings.section.advanced"))
        advanced_layout.addWidget(advanced_title)
        
        advanced_form = QFormLayout()
        advanced_form.setSpacing(10)
        
        # Log level
        self._log_level_combo = ComboBox()
        self._log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self._log_level_combo.setCurrentIndex(1)  # INFO
        advanced_form.addRow(t("settings.label.log.level"), self._log_level_combo)
        
        advanced_layout.addLayout(advanced_form)
        
        # Debug mode info
        debug_info = BodyLabel(
            t("settings.btn.debug")
        )
        bind_style(debug_info, lambda c: f"color: {c.text_secondary}; font-size: 11px;")
        debug_info.setWordWrap(True)
        advanced_layout.addWidget(debug_info)
        
        layout.addWidget(advanced_card)
        
        # About Section
        about_card = CardWidget()
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(20, 20, 20, 20)
        about_layout.setSpacing(10)
        
        about_title = StrongBodyLabel(t("settings.section.about"))
        about_layout.addWidget(about_title)

        version_label = BodyLabel(f"{t('settings.label.version.label')} {config.get('app.version', '0.1.0')}")
        about_layout.addWidget(version_label)

        desc_label = BodyLabel(t("settings.about.description"))
        desc_label.setWordWrap(True)
        about_layout.addWidget(desc_label)

        # Separator line
        about_layout.addSpacing(6)
        authors_title = StrongBodyLabel(t("settings.section.authors"))
        about_layout.addWidget(authors_title)

        authors_label = BodyLabel(
            "Diego García-Prieto  (diego.garciaprieto@unican.es)\n"
            "Camilo Palazuelos  (camilo.palazuelos@unican.es)\n"
            "Rafael Duque  (rafael.duque@unican.es)\n\n"
            f"{t('settings.about.university')}"
        )
        about_layout.addWidget(authors_label)

        about_layout.addSpacing(6)
        contact_label = BodyLabel(t("settings.about.repository"))
        bind_style(contact_label, lambda c: f"color: {c.text_secondary}; font-size: 11px;")
        about_layout.addWidget(contact_label)
        
        # License button
        license_btn = PushButton(t("settings.btn.license"), self)
        license_btn.setIcon(FluentIcon.DOCUMENT)
        license_btn.clicked.connect(self._show_license)
        about_layout.addWidget(license_btn)
        
        layout.addWidget(about_card)
        
        # Action Buttons
        button_row = QHBoxLayout()
        button_row.addStretch()
        
        reset_button = PushButton(t("settings.btn.reset"), self)
        reset_button.setIcon(FluentIcon.CANCEL)
        reset_button.clicked.connect(self._reset_settings)
        
        save_button = PrimaryPushButton(t("settings.btn.apply"), self)
        save_button.setIcon(FluentIcon.SAVE)
        save_button.clicked.connect(self._save_settings)
        
        button_row.addWidget(reset_button)
        button_row.addWidget(save_button)
        
        layout.addLayout(button_row)
        
        # Stretch
        layout.addStretch()
        
        log.debug("Settings Page initialized successfully")
    
    def _on_theme_changed(self, theme: str):
        """Apply theme change immediately via qfluentwidgets."""
        mapping = {
            t("settings.theme.light"): Theme.LIGHT,
            t("settings.theme.dark"): Theme.DARK,
            t("settings.theme.auto"): Theme.AUTO,
        }
        chosen = mapping.get(theme, Theme.LIGHT)
        setTheme(chosen)
        config.set('ui.theme', theme.lower())
        log.info(f"Theme changed to: {theme}")
        usage_log.event("Settings", "select", "Theme", theme)
    
    def _on_font_size_changed(self, size: int):
        """Handle font size change"""
        log.debug(f"Font size changed to: {size}")
        config.set('ui.font.size', size)
        family = config.get('ui.font.family', 'Segoe UI')
        app = QApplication.instance()
        if app:
            app.setFont(QFont(family, size))
    
    def _on_language_changed(self, lang: str):
        """Handle language change"""
        log.info(f"Language changed to: {lang}")
        lang_code = {"English": "en", "Español": "es"}.get(lang, "en")
        config.set('app.language', lang_code)
        set_language(lang_code)
        usage_log.event("Settings", "select", "UI Language", lang)
        InfoBar.information(
            title=t("settings.msg.language.changed"),
            content=t("settings.msg.language.restart"),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=5000, parent=self,
        )
    
    def _show_license(self):
        """Show license information"""
        usage_log.event("Settings", "click", "License button")
        log.info("Show license clicked")
        from pathlib import Path
        license_path = Path(__file__).parent.parent.parent.parent.parent / "LICENSE"
        if license_path.exists():
            license_text = license_path.read_text(encoding="utf-8")
        else:
            license_text = (
                "MIT License\n\n"
                "Copyright (c) 2025 Diego García-Prieto, Camilo Palazuelos, "
                "Rafael Duque — University of Cantabria\n\n"
                "Permission is hereby granted, free of charge, to any person obtaining a copy "
                "of this software and associated documentation files (the 'Software'), to deal "
                "in the Software without restriction, including without limitation the rights "
                "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
                "copies of the Software, and to permit persons to whom the Software is "
                "furnished to do so, subject to the following conditions:\n\n"
                "The above copyright notice and this permission notice shall be included in all "
                "copies or substantial portions of the Software.\n\n"
                "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
                "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
                "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
                "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
                "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
                "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
            )
        dlg = MessageBox("License — MIT", license_text, self)
        dlg.exec()
    
    def _reset_settings(self):
        """Reset all settings to defaults"""
        usage_log.event("Settings", "click", "Reset button")
        log.info("Reset settings clicked")
        dlg = MessageBox(
            t("settings.msg.reset.title"),
            t("settings.msg.reset.confirm"),
            self,
        )
        if dlg.exec():
            config.reset_to_defaults()
            self._reload_ui_values()
            InfoBar.success(
                title=t("settings.msg.reset.title"),
                content=t("settings.msg.reset.success"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            log.info("Settings reset to defaults")
    
    def _log_filled_fields(self) -> None:
        """One usage-log row per current setting, logged at Apply time,
        mirroring MetadataPage._log_filled_fields()."""
        fields = {
            "Theme": self._theme_combo.currentText(),
            "Font Size": self._font_size_spin.value(),
            "UI Language": self._lang_combo.currentText(),
            "Decimal Places": self._decimals_spin.value(),
            "Log Level": self._log_level_combo.currentText(),
        }
        for element, value in fields.items():
            if value:
                usage_log.event("Settings", "field_filled", element, str(value))

    def _save_settings(self):
        """Save current settings"""
        usage_log.event("Settings", "click", "Apply button")
        log.info("Apply settings clicked")
        config.save()
        self._log_filled_fields()
        InfoBar.success(
            title=t("settings.msg.reset.title"),
            content=t("settings.msg.saved.success"),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=3000, parent=self,
        )

    def _reload_ui_values(self):
        """Reload widget values from current config (used after reset)."""
        theme = config.get('ui.theme', 'light').capitalize()
        mapping = {
            "light": t("settings.theme.light"),
            "dark": t("settings.theme.dark"),
            "auto (system)": t("settings.theme.auto")
        }
        self._theme_combo.setCurrentText(mapping.get(theme.lower(), t("settings.theme.light")))
        self._font_size_spin.setValue(config.get('ui.font.size', 10))
        lang_code = config.get('app.language', 'en')
        lang_map = {"en": "English", "es": "Español"}
        self._lang_combo.setCurrentText(lang_map.get(lang_code, "English"))
        log.debug("Settings UI reloaded from config")
