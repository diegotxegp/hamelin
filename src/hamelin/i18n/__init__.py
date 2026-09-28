"""
i18n Module
~~~~~~~~~~~

Internationalization singleton for HAMELIN.

Usage:
    from hamelin.i18n import t, set_language
    
    # In any page/widget
    label = TitleLabel(t("data.title"))  # → "Data Management" (EN) or "Gestión de Datos" (ES)
    
    # When language changes in Settings
    set_language("es")
    
Design:
- Singleton pattern: module-level _current_lang
- Fallback: missing keys return the key itself (safe)
- No live reload: restart required (simpler, more robust)
"""

from hamelin.i18n.strings import EN, ES
from hamelin.utils.logger import log

_DICTS = {"en": EN, "es": ES}
_current_lang: str = "en"


def t(key: str) -> str:
    """
    Get translated string for the current language.
    
    Args:
        key: Translation key (e.g., "data.title", "nav.home")
    
    Returns:
        Translated string, or the key itself if not found (safe fallback).
    
    Example:
        >>> t("data.title")  # EN → "Data Management"
        >>> t("missing.key")  # → "missing.key"
    """
    if _current_lang not in _DICTS:
        return EN.get(key, key)
    return _DICTS[_current_lang].get(key) or EN.get(key, key)


def set_language(lang: str) -> None:
    """
    Set the active language globally.
    
    Args:
        lang: Language code ("en" or "es"). Invalid codes default to "en".
    
    Example:
        >>> set_language("es")
        >>> t("data.title")  # → "Gestión de Datos"
    """
    global _current_lang
    if lang in _DICTS:
        _current_lang = lang
        log.debug(f"Language set to {lang}")
    else:
        _current_lang = "en"
        log.warning(f"Invalid language '{lang}', defaulting to 'en'")


def get_language() -> str:
    """Get the current active language code."""
    return _current_lang
