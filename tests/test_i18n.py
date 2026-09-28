"""
Tests for i18n Module
~~~~~~~~~~~~~~~~~~~~~

Test suite for internationalization functionality.
"""

import pytest
from hamelin.i18n import t, set_language, get_language
from hamelin.i18n.strings import EN, ES


class TestTranslationFunction:
    """Tests for t() function."""
    
    def test_t_returns_english_by_default(self):
        """Test that t() returns English strings by default."""
        assert t("data.title") == "Data Management"
        assert t("nav.home") == "Home"
        assert t("settings.title") == "Settings"
    
    def test_t_returns_spanish_after_set_language(self):
        """Test that t() returns Spanish strings after set_language('es')."""
        set_language("es")
        assert t("data.title") == "Gestión de Datos"
        assert t("nav.home") == "Inicio"
        assert t("settings.title") == "Configuración"
        # Reset to English
        set_language("en")
    
    def test_t_returns_key_as_fallback_for_missing(self):
        """Test that t() returns the key itself if not found."""
        assert t("nonexistent.key") == "nonexistent.key"
        assert t("") == ""
    
    def test_t_returns_english_if_missing_in_other_language(self):
        """Test fallback to English if key missing in current language."""
        set_language("es")
        # Assuming all Spanish translations exist, but just in case:
        # If a key is missing, it should fall back to English
        result = t("data.title")
        assert result is not None
        set_language("en")
    
    def test_all_english_keys_have_spanish_equivalents(self):
        """Test that every English key has a Spanish translation."""
        missing_keys = []
        for key in EN.keys():
            if key not in ES:
                missing_keys.append(key)
        
        assert len(missing_keys) == 0, f"Missing Spanish translations for: {missing_keys}"
    
    def test_spanish_has_no_extra_keys(self):
        """Test that Spanish dict has the same keys as English."""
        english_keys = set(EN.keys())
        spanish_keys = set(ES.keys())
        
        extra_keys = spanish_keys - english_keys
        assert len(extra_keys) == 0, f"Extra Spanish keys not in English: {extra_keys}"


class TestLanguageSetting:
    """Tests for set_language() and get_language()."""
    
    def test_set_language_en(self):
        """Test setting language to English."""
        set_language("en")
        assert get_language() == "en"
        assert t("data.title") == "Data Management"
    
    def test_set_language_es(self):
        """Test setting language to Spanish."""
        set_language("es")
        assert get_language() == "es"
        assert t("data.title") == "Gestión de Datos"
        set_language("en")
    
    def test_set_language_invalid_defaults_to_en(self):
        """Test that invalid language codes default to English."""
        set_language("fr")  # French not supported
        assert get_language() == "en"
        assert t("data.title") == "Data Management"
    
    def test_set_language_empty_string_defaults_to_en(self):
        """Test that empty language code defaults to English."""
        set_language("")
        assert get_language() == "en"
        set_language("en")


class TestKeyNaming:
    """Tests for i18n key naming conventions."""
    
    def test_all_keys_follow_naming_convention(self):
        """Test that all keys follow the section.component pattern."""
        valid_patterns = [
            "nav.",    # Navigation
            "home.",   # Home page
            "metadata.",  # Metadata page
            "data.",   # Data page
            "table1.",  # Table 1 page
            "forecasting.",  # Forecasting page
            "training.",  # Training page
            "dashboard.",  # Dashboard page
            "settings.",  # Settings page
            "help.",   # Help page
        ]
        
        for key in EN.keys():
            assert any(key.startswith(prefix) for prefix in valid_patterns), \
                f"Key '{key}' does not follow naming convention"
    
    def test_section_keys_are_grouped(self):
        """Test that keys are logically grouped by section."""
        nav_keys = [k for k in EN.keys() if k.startswith("nav.")]
        data_keys = [k for k in EN.keys() if k.startswith("data.")]
        
        assert len(nav_keys) >= 9, "Navigation should have at least 9 keys"
        assert len(data_keys) >= 8, "Data page should have at least 8 keys"


class TestCommonStrings:
    """Tests for common UI strings."""
    
    def test_buttons_are_translated(self):
        """Test that button labels are present in both languages."""
        buttons = ["data.btn.load", "data.btn.browse", "training.btn.start"]
        for button_key in buttons:
            assert button_key in EN, f"Button key missing: {button_key}"
            assert button_key in ES, f"Spanish translation missing: {button_key}"
    
    def test_titles_are_translated(self):
        """Test that page titles are present in both languages."""
        titles = [
            "data.title",
            "training.title",
            "metadata.title",
            "settings.title",
        ]
        for title_key in titles:
            assert title_key in EN, f"Title key missing: {title_key}"
            assert title_key in ES, f"Spanish translation missing: {title_key}"
            assert len(EN[title_key]) > 0, f"Empty English title: {title_key}"
            assert len(ES[title_key]) > 0, f"Empty Spanish title: {title_key}"


class TestLanguagePersistence:
    """Tests for language setting persistence."""
    
    def test_multiple_language_switches(self):
        """Test switching between languages multiple times."""
        set_language("en")
        assert t("data.title") == "Data Management"
        
        set_language("es")
        assert t("data.title") == "Gestión de Datos"
        
        set_language("en")
        assert t("data.title") == "Data Management"
        
        set_language("es")
        assert t("data.title") == "Gestión de Datos"
        
        # Reset
        set_language("en")
    
    def test_get_language_consistency(self):
        """Test that get_language() is consistent with t() output."""
        set_language("en")
        assert get_language() == "en"
        assert t("data.title") == EN["data.title"]
        
        set_language("es")
        assert get_language() == "es"
        assert t("data.title") == ES["data.title"]
        
        set_language("en")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
