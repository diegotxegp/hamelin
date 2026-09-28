"""
Custom Exception Classes
~~~~~~~~~~~~~~~~~~~~~~~~

Domain-specific exceptions for HAMELIN

Exception Hierarchy:
    HamelinError (base)
    ├── DataError
    │   ├── DataLoadError
    │   ├── DataValidationError
    │   └── DataExportError
    ├── ModelError
    │   ├── ModelTrainingError
    │   ├── ModelPredictionError
    │   └── ModelSaveError
    ├── UIError
    │   ├── UIRenderError
    │   └── UIInteractionError
    └── ConfigError

All exceptions include:
- User-friendly English messages
- Technical details for logging
- Optional suggestion for resolution
"""

from typing import Optional


class HamelinError(Exception):
    """
    Base exception for all HAMELIN errors.
    
    Attributes:
        message: User-friendly error message (English)
        technical_detail: Technical information for logging
        suggestion: Optional suggestion for resolution
    """
    
    def __init__(
        self,
        message: str,
        technical_detail: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        """
        Initialize HAMELIN exception.
        
        Args:
            message: User-friendly error description
            technical_detail: Technical information (optional)
            suggestion: Suggestion for fixing the error (optional)
        """
        self.message = message
        self.technical_detail = technical_detail or ""
        self.suggestion = suggestion or ""
        
        # Build full message
        full_message = message
        if suggestion:
            full_message += f"\n\nSuggestion: {suggestion}"
        
        super().__init__(full_message)
    
    def get_user_message(self) -> str:
        """Get user-friendly message."""
        return self.message
    
    def get_technical_detail(self) -> str:
        """Get technical detail for logging."""
        return self.technical_detail
    
    def get_suggestion(self) -> str:
        """Get resolution suggestion."""
        return self.suggestion


# ============================================================================
# Data-related Exceptions
# ============================================================================

class DataError(HamelinError):
    """Base class for data-related errors."""
    pass


class DataLoadError(DataError):
    """Error loading data from file."""
    
    def __init__(
        self,
        filename: str,
        reason: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = f"Failed to load data from '{filename}'"
        if reason:
            message += f": {reason}"
        
        suggestion = (
            "Please check that:\n"
            "• The file exists and is accessible\n"
            "• The file format is supported (CSV, Excel)\n"
            "• The file is not corrupted or open in another program"
        )
        
        super().__init__(message, technical_detail, suggestion)
        self.filename = filename


class DataValidationError(DataError):
    """Error validating data integrity."""
    
    def __init__(
        self,
        validation_issue: str,
        column: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = f"Data validation failed: {validation_issue}"
        if column:
            message += f" (Column: '{column}')"
        
        suggestion = (
            "Please check your data for:\n"
            "• Missing or invalid values\n"
            "• Incorrect data types\n"
            "• Out-of-range values"
        )
        
        super().__init__(message, technical_detail, suggestion)
        self.column = column


class DataExportError(DataError):
    """Error exporting data or results."""
    
    def __init__(
        self,
        export_format: str,
        reason: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = f"Failed to export data as {export_format}"
        if reason:
            message += f": {reason}"
        
        suggestion = (
            "Possible solutions:\n"
            "• Ensure you have write permissions\n"
            "• Check available disk space\n"
            "• Close the file if it's already open"
        )
        
        super().__init__(message, technical_detail, suggestion)
        self.export_format = export_format


class DataSaveError(DataError):
    """Error saving data or metadata to file."""
    
    def __init__(
        self,
        reason: str,
        filename: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = f"Failed to save data: {reason}"
        if filename:
            message = f"Failed to save data to '{filename}': {reason}"
        
        suggestion = (
            "Possible solutions:\n"
            "• Ensure you have write permissions\n"
            "• Check available disk space\n"
            "• Ensure the directory exists\n"
            "• Close the file if it's already open"
        )
        
        super().__init__(message, technical_detail, suggestion)
        self.filename = filename


class ValidationError(DataError):
    """Error validating metadata or configuration."""
    
    def __init__(
        self,
        reason: str,
        technical_detail: Optional[str] = None
    ):
        message = f"Validation failed: {reason}"
        
        suggestion = (
            "Please review:\n"
            "• All required fields are filled\n"
            "• Data formats are correct\n"
            "• Values are within acceptable ranges"
        )
        
        super().__init__(message, technical_detail, suggestion)


# ============================================================================
# Model-related Exceptions
# ============================================================================

class ModelError(HamelinError):
    """Base class for model-related errors."""
    pass


class ModelTrainingError(ModelError):
    """Error during model training."""
    
    def __init__(
        self,
        model_type: Optional[str] = None,
        reason: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = "Model training failed"
        if model_type:
            message += f" ({model_type})"
        if reason:
            message += f": {reason}"
        
        suggestion = (
            "Common causes:\n"
            "• Insufficient data\n"
            "• Invalid hyperparameters\n"
            "• Data type mismatches\n"
            "• Insufficient memory or timeout"
        )
        
        super().__init__(message, technical_detail, suggestion)
        self.model_type = model_type


class ModelPredictionError(ModelError):
    """Error during model prediction."""
    
    def __init__(
        self,
        reason: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = "Model prediction failed"
        if reason:
            message += f": {reason}"
        
        suggestion = (
            "Please verify:\n"
            "• Model is trained and loaded\n"
            "• Input data matches training format\n"
            "• All required features are present"
        )
        
        super().__init__(message, technical_detail, suggestion)


class ModelSaveError(ModelError):
    """Error saving model."""
    
    def __init__(
        self,
        filepath: str,
        reason: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = f"Failed to save model to '{filepath}'"
        if reason:
            message += f": {reason}"
        
        suggestion = (
            "Check:\n"
            "• Write permissions for the target directory\n"
            "• Available disk space\n"
            "• Path validity"
        )
        
        super().__init__(message, technical_detail, suggestion)
        self.filepath = filepath


# ============================================================================
# UI-related Exceptions
# ============================================================================

class UIError(HamelinError):
    """Base class for UI-related errors."""
    pass


class UIRenderError(UIError):
    """Error rendering UI component."""
    
    def __init__(
        self,
        component: str,
        reason: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = f"Failed to render UI component: {component}"
        if reason:
            message += f" - {reason}"
        
        suggestion = "Please try restarting the application."
        
        super().__init__(message, technical_detail, suggestion)
        self.component = component


class UIInteractionError(UIError):
    """Error during UI interaction."""
    
    def __init__(
        self,
        action: str,
        reason: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = f"UI interaction failed: {action}"
        if reason:
            message += f" - {reason}"
        
        suggestion = "Please try the operation again."
        
        super().__init__(message, technical_detail, suggestion)
        self.action = action


# ============================================================================
# Configuration Exceptions
# ============================================================================

class ConfigError(HamelinError):
    """Configuration error."""
    
    def __init__(
        self,
        config_key: Optional[str] = None,
        reason: Optional[str] = None,
        technical_detail: Optional[str] = None
    ):
        message = "Configuration error"
        if config_key:
            message += f" for '{config_key}'"
        if reason:
            message += f": {reason}"
        
        suggestion = (
            "Try:\n"
            "• Resetting configuration to defaults\n"
            "• Checking config file syntax\n"
            "• Reinstalling the application"
        )
        
        super().__init__(message, technical_detail, suggestion)
        self.config_key = config_key


# ============================================================================
# Validation Exceptions
# ============================================================================

class FieldValidationError(HamelinError):
    """Validation error for a specific field."""
    
    def __init__(
        self,
        field: str,
        reason: str,
        technical_detail: Optional[str] = None
    ):
        message = f"Validation failed for '{field}': {reason}"
        suggestion = "Please correct the input and try again."
        
        super().__init__(message, technical_detail, suggestion)
        self.field = field


if __name__ == "__main__":
    # Test exceptions
    print("Testing HAMELIN exceptions...\n")
    
    # Test DataLoadError
    try:
        raise DataLoadError(
            "test_data.csv",
            reason="File not found",
            technical_detail="FileNotFoundError at path/to/test_data.csv"
        )
    except DataLoadError as e:
        print(f"DataLoadError caught:")
        print(f"  User message: {e.get_user_message()}")
        print(f"  Suggestion: {e.get_suggestion()}")
        print(f"  Technical: {e.get_technical_detail()}\n")
    
    # Test ModelTrainingError
    try:
        raise ModelTrainingError(
            model_type="Random Forest",
            reason="Timeout after 1 hour",
            technical_detail="Ray timeout exception"
        )
    except ModelTrainingError as e:
        print(f"ModelTrainingError caught:")
        print(f"  Message: {e.get_user_message()}\n")
    
    # Test ConfigError
    try:
        raise ConfigError(
            config_key="ui.theme",
            reason="Invalid value 'invalid_theme'"
        )
    except ConfigError as e:
        print(f"ConfigError caught:")
        print(f"  Message: {e.get_user_message()}\n")
    
    print("✓ Exception system test complete")
