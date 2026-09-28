"""
Configuration Management System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Centralized configuration management for HAMELIN

Features:
- YAML-based configuration
- Type validation
- Default values
- Environment-specific settings
- Hot reload capability

Usage:
    from utils.config_manager import config
    
    dataset_path = config.get('paths.data')
    window_width = config.get('ui.window.width', default=1200)
    config.set('ui.theme', 'dark')
    config.save()
"""

import yaml
from pathlib import Path
from typing import Any, Optional, Dict
from copy import deepcopy


class ConfigManager:
    """
    Manages application configuration with YAML persistence.
    
    Provides:
    - Hierarchical configuration access (dot notation)
    - Type validation
    - Default values
    - Auto-save capability
    """
    
    _instance: Optional['ConfigManager'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager."""
        if not ConfigManager._initialized:
            self.config_dir = Path(__file__).parent.parent.parent.parent / "workspace" / "config"
            self.config_file = self.config_dir / "app_config.yaml"
            self._config: Dict[str, Any] = {}
            self._defaults: Dict[str, Any] = self._get_defaults()
            self.load()
            ConfigManager._initialized = True
    
    def _get_defaults(self) -> Dict[str, Any]:
        """
        Define default configuration values.
        
        Returns:
            Dictionary with default configuration
        """
        return {
            'app': {
                'name': 'HAMELIN',
                'version': '0.1.0',
                'language': 'en',  # English UI
                'debug': False
            },
            'paths': {
                'data': 'workspace/data/',
                'models': 'workspace/models/',
                'exports': 'workspace/exports/',
                'logs': 'workspace/logs/'
            },
            'ui': {
                'theme': 'light',  # light or dark
                'window': {
                    'width': 1400,
                    'height': 900,
                    'maximized': False
                },
                'font': {
                    'family': 'Segoe UI',
                    'size': 10
                }
            },
            'data': {
                'auto_detect_types': True,
                'missing_value_indicators': ['', 'NA', 'N/A', 'null', 'None'],
                'max_categorical_unique': 20,
                'date_formats': ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
            },
            'model': {
                'default_time_limit': 3600,  # 1 hour
                'validation_split': 0.2,
                'random_state': 42,
                'n_jobs': -1  # Use all cores
            },
            'table1': {
                'decimal_places': 2,
                'show_ci': True,
                'ci_level': 0.95,
                'export_format': 'html'  # html, docx, xlsx
            },
            'forecasting': {
                'methods': ['linear', 'polynomial', 'exponential'],
                'confidence_interval': 0.95,
                'min_data_points': 5
            },
            'logging': {
                'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
                'max_file_size_mb': 10,
                'backup_count': 5
            }
        }
    
    def load(self) -> None:
        """Load configuration from file, or create with defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f) or {}
                
                # Merge with defaults (loaded config takes precedence)
                self._config = self._merge_configs(self._defaults, loaded_config)
                
                # Import logger here to avoid circular import
                try:
                    from hamelin.utils.logger import log
                    log.info(f"Configuration loaded from {self.config_file}")
                except ImportError:
                    pass
                    
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration")
                self._config = deepcopy(self._defaults)
        else:
            # No config file, use defaults and create it
            self._config = deepcopy(self._defaults)
            self.save()
    
    def _merge_configs(self, defaults: Dict, loaded: Dict) -> Dict:
        """
        Recursively merge loaded config with defaults.
        
        Args:
            defaults: Default configuration
            loaded: Loaded configuration
            
        Returns:
            Merged configuration
        """
        result = deepcopy(defaults)
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            path: Dot-separated path (e.g., 'ui.window.width')
            default: Default value if path not found
            
        Returns:
            Configuration value or default
            
        Example:
            width = config.get('ui.window.width')
            theme = config.get('ui.theme', default='light')
        """
        keys = path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            path: Dot-separated path (e.g., 'ui.theme')
            value: Value to set
            
        Example:
            config.set('ui.theme', 'dark')
            config.set('ui.window.width', 1600)
        """
        keys = path.split('.')
        target = self._config
        
        # Navigate to the parent of the final key
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # Set the final value
        target[keys[-1]] = value
        
        try:
            from hamelin.utils.logger import log
            log.debug(f"Config updated: {path} = {value}")
        except ImportError:
            pass
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
            
            try:
                from hamelin.utils.logger import log
                log.info(f"Configuration saved to {self.config_file}")
            except ImportError:
                pass
                
        except Exception as e:
            try:
                from hamelin.utils.logger import log
                log.error(f"Failed to save configuration: {e}", exc_info=True)
            except ImportError:
                print(f"Error saving configuration: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = deepcopy(self._defaults)
        self.save()
        
        try:
            from hamelin.utils.logger import log
            log.warning("Configuration reset to defaults")
        except ImportError:
            pass
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get entire configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return deepcopy(self._config)
    
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if valid, False otherwise
        """
        # Add validation rules as needed
        validations = [
            (self.get('ui.window.width', 0) > 0, "Window width must be positive"),
            (self.get('ui.window.height', 0) > 0, "Window height must be positive"),
            (self.get('model.validation_split', 0) > 0, "Validation split must be positive"),
            (self.get('model.validation_split', 1) < 1, "Validation split must be < 1"),
        ]
        
        is_valid = True
        for condition, message in validations:
            if not condition:
                try:
                    from hamelin.utils.logger import log
                    log.error(f"Config validation failed: {message}")
                except ImportError:
                    print(f"Config validation failed: {message}")
                is_valid = False
        
        return is_valid


# Singleton instance for easy import
config = ConfigManager()


if __name__ == "__main__":
    # Test the configuration manager
    print("Testing ConfigManager...")
    
    # Get values
    print(f"App name: {config.get('app.name')}")
    print(f"Window width: {config.get('ui.window.width')}")
    print(f"Theme: {config.get('ui.theme')}")
    
    # Set values
    config.set('ui.theme', 'dark')
    print(f"Theme changed to: {config.get('ui.theme')}")
    
    # Test default value
    print(f"Non-existent key: {config.get('does.not.exist', default='DEFAULT')}")
    
    # Validate
    is_valid = config.validate()
    print(f"Config valid: {is_valid}")
    
    # Save
    config.save()
    
    print("\n✓ ConfigManager test complete. Check config/app_config.yaml")
