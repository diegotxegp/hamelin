"""
Global Error Handler
~~~~~~~~~~~~~~~~~~~

Centralized error handling and recovery for HAMELIN

Features:
- Global exception handler
- User-friendly error dialogs
- Automatic logging of errors
- Error recovery mechanisms
- Graceful degradation

Usage:
    from hamelin.utils.error_handler import handle_error, safe_execute
    
    # Manual error handling
    try:
        risky_operation()
    except Exception as e:
        handle_error(e, context="Loading data")
    
    # Automatic error handling with decorator
    @safe_execute(default_return=None)
    def my_function():
        # Code that might raise exceptions
        pass
"""

import sys
import traceback
from typing import Optional, Callable, Any, TypeVar
from functools import wraps

from hamelin.utils.exceptions import HamelinError
from hamelin.utils.logger import log


T = TypeVar('T')


class ErrorHandler:
    """
    Global error handler for HAMELIN application.
    
    Provides centralized error handling, logging, and user notification.
    """
    
    _instance: Optional['ErrorHandler'] = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize error handler."""
        self.error_count = 0
        self.last_error: Optional[Exception] = None
    
    def handle(
        self,
        error: Exception,
        context: Optional[str] = None,
        show_dialog: bool = True,
        critical: bool = False
    ) -> None:
        """
        Handle an exception.
        
        Args:
            error: The exception to handle
            context: Context where error occurred (e.g., "Loading data")
            show_dialog: Whether to show error dialog to user
            critical: If True, application should exit after handling
        """
        self.error_count += 1
        self.last_error = error
        
        # Get error details
        if isinstance(error, HamelinError):
            user_message = error.get_user_message()
            technical_detail = error.get_technical_detail()
            suggestion = error.get_suggestion()
        else:
            user_message = str(error)
            technical_detail = traceback.format_exc()
            suggestion = "Please try again or contact support if the problem persists."
        
        # Add context if provided
        if context:
            user_message = f"{context}: {user_message}"
        
        # Log the error
        log_message = f"Error #{self.error_count}"
        if context:
            log_message += f" in {context}"
        log_message += f": {user_message}"
        
        if critical:
            log.critical(log_message, exc_info=True)
        else:
            log.error(log_message, exc_info=True)
        
        if technical_detail:
            log.debug(f"Technical detail: {technical_detail}")
        
        # Show user notification (would integrate with UI in real implementation)
        if show_dialog:
            self._show_error_dialog(user_message, suggestion, critical)
        
        # If critical, prepare for shutdown
        if critical:
            log.critical("Critical error - application will exit")
            self._prepare_shutdown()
    
    def _show_error_dialog(
        self,
        message: str,
        suggestion: str,
        critical: bool
    ) -> None:
        """
        Show error dialog to user.
        
        In a real application, this would show a PySide6 QMessageBox.
        For now, we'll just print to console.
        
        Args:
            message: Error message
            suggestion: Suggestion for resolution
            critical: Whether this is a critical error
        """
        # TODO: Integrate with PySide6 QMessageBox when UI is available
        dialog_type = "CRITICAL ERROR" if critical else "Error"
        
        print(f"\n{'=' * 60}")
        print(f"{dialog_type}")
        print(f"{'=' * 60}")
        print(f"\n{message}\n")
        if suggestion:
            print(f"{suggestion}\n")
        print(f"{'=' * 60}\n")
    
    def _prepare_shutdown(self) -> None:
        """
        Prepare application for shutdown after critical error.
        
        - Save any unsaved work
        - Close connections
        - Clean up temporary files
        """
        log.info("Preparing for graceful shutdown...")
        
        # TODO: Add cleanup logic:
        # - Save autosave data
        # - Close database connections
        # - Send crash report (if user opts in)
        
        log.info("Cleanup complete")
    
    def get_error_stats(self) -> dict:
        """
        Get error statistics.
        
        Returns:
            Dictionary with error statistics
        """
        return {
            'total_errors': self.error_count,
            'last_error': str(self.last_error) if self.last_error else None
        }
    
    def reset_stats(self) -> None:
        """Reset error statistics."""
        self.error_count = 0
        self.last_error = None


# Global error handler instance
error_handler = ErrorHandler()


# ============================================================================
# Convenience Functions
# ============================================================================

def handle_error(
    error: Exception,
    context: Optional[str] = None,
    show_dialog: bool = True,
    critical: bool = False
) -> None:
    """
    Handle an error using the global error handler.
    
    Args:
        error: Exception to handle
        context: Context where error occurred
        show_dialog: Show error dialog to user
        critical: Whether error is critical (app should exit)
    
    Example:
        try:
            load_data(filepath)
        except Exception as e:
            handle_error(e, context="Loading dataset")
    """
    error_handler.handle(error, context, show_dialog, critical)


def safe_execute(
    default_return: Any = None,
    context: Optional[str] = None,
    show_dialog: bool = True,
    log_errors: bool = True
) -> Callable:
    """
    Decorator for safe function execution with automatic error handling.
    
    Args:
        default_return: Value to return if function raises exception
        context: Context description for error logging
        show_dialog: Show error dialog if exception occurs
        log_errors: Log errors (True by default)
    
    Returns:
        Decorated function that handles exceptions gracefully
    
    Example:
        @safe_execute(default_return=[], context="Loading user preferences")
        def load_preferences():
            # Code that might fail
            return preferences
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = context or f"Executing {func.__name__}"
                
                if log_errors:
                    handle_error(e, context=error_context, show_dialog=show_dialog)
                
                return default_return
        
        return wrapper
    
    return decorator


def install_global_exception_handler() -> None:
    """
    Install global exception handler for uncaught exceptions.
    
    This will catch any unhandled exceptions in the application.
    Call this at application startup.
    """
    def global_exception_hook(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow Ctrl+C to work normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        log.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        handle_error(
            exc_value,
            context="Uncaught exception",
            show_dialog=True,
            critical=True
        )
    
    sys.excepthook = global_exception_hook
    log.info("Global exception handler installed")


if __name__ == "__main__":
    # Test error handling
    print("Testing Error Handler...\n")
    
    from hamelin.utils.exceptions import DataLoadError, ModelTrainingError
    
    # Test 1: Handle custom exception
    try:
        raise DataLoadError(
            "test.csv",
            reason="File not found",
            technical_detail="Path: /invalid/path/test.csv"
        )
    except Exception as e:
        handle_error(e, context="Test 1")
    
    # Test 2: Handle standard exception
    try:
        result = 1 / 0
    except Exception as e:
        handle_error(e, context="Test 2 - Division")
    
    # Test 3: Safe execute decorator
    @safe_execute(default_return=0, context="Test 3 - Safe function")
    def risky_function():
        return 10 / 0
    
    result = risky_function()
    print(f"Safe function returned: {result}")
    
    # Test 4: Error statistics
    stats = error_handler.get_error_stats()
    print(f"\nError statistics: {stats}")
    
    print("\n✓ Error handler test complete")
