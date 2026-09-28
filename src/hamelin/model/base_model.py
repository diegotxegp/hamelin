"""
Base Model Class
~~~~~~~~~~~~~~~~

Abstract base class for all HAMELIN data models.

Provides:
- Common validation interface
- Serialization/deserialization
- State management
- Change tracking

All domain models should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from pathlib import Path

from hamelin.utils.logger import log
from hamelin.utils.exceptions import ValidationError


class BaseModel(ABC):
    """
    Abstract base class for all data models.
    
    Provides common functionality:
    - Validation
    - Serialization (to dict/JSON)
    - State tracking
    - Change detection
    """
    
    def __init__(self):
        """Initialize base model."""
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = datetime.now()
        self._is_dirty: bool = False  # Has unsaved changes
        self._errors: List[str] = []
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate model data.
        
        Returns:
            True if valid, False otherwise
            
        Implementation should:
        1. Clear self._errors list
        2. Perform validations
        3. Add errors to self._errors if found
        4. Return True if no errors
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.
        
        Returns:
            Dictionary representation of model
        """
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load model from dictionary.
        
        Args:
            data: Dictionary with model data
        """
        pass
    
    def to_json(self, filepath: Optional[Path] = None) -> str:
        """
        Convert model to JSON string or save to file.
        
        Args:
            filepath: If provided, save JSON to this file
            
        Returns:
            JSON string representation
        """
        data = self.to_dict()
        
        # Add metadata
        data['_metadata'] = {
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat(),
            'model_class': self.__class__.__name__
        }
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if filepath:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
            log.info(f"Model saved to {filepath}")
        
        return json_str
    
    def from_json(self, json_data: str = None, filepath: Path = None) -> None:
        """
        Load model from JSON string or file.
        
        Args:
            json_data: JSON string
            filepath: Path to JSON file (alternative to json_data)
        """
        if filepath:
            filepath = Path(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = f.read()
            log.info(f"Model loaded from {filepath}")
        
        if not json_data:
            raise ValueError("Either json_data or filepath must be provided")
        
        data = json.loads(json_data)
        
        # Extract metadata if present
        if '_metadata' in data:
            metadata = data.pop('_metadata')
            if 'created_at' in metadata:
                self._created_at = datetime.fromisoformat(metadata['created_at'])
            if 'updated_at' in metadata:
                self._updated_at = datetime.fromisoformat(metadata['updated_at'])
        
        self.from_dict(data)
        self._is_dirty = False
    
    def mark_dirty(self) -> None:
        """Mark model as having unsaved changes."""
        self._is_dirty = True
        self._updated_at = datetime.now()
    
    def mark_clean(self) -> None:
        """Mark model as saved (no pending changes)."""
        self._is_dirty = False
    
    def is_dirty(self) -> bool:
        """Check if model has unsaved changes."""
        return self._is_dirty
    
    def get_errors(self) -> List[str]:
        """Get list of validation errors."""
        return self._errors.copy()
    
    def has_errors(self) -> bool:
        """Check if model has validation errors."""
        return len(self._errors) > 0
    
    def clear_errors(self) -> None:
        """Clear validation errors."""
        self._errors.clear()
    
    def add_error(self, error: str) -> None:
        """
        Add a validation error.
        
        Args:
            error: Error message
        """
        self._errors.append(error)
    
    def get_created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    def get_updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at
    
    def __repr__(self) -> str:
        """String representation of model."""
        return f"{self.__class__.__name__}(created={self._created_at}, dirty={self._is_dirty})"
    
    def validate_required(self, field_name: str, value: Any) -> bool:
        """
        Validate that a required field has a value.
        
        Args:
            field_name: Name of the field
            value: Value to check
            
        Returns:
            True if valid, False otherwise
        """
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self.add_error(f"{field_name} is required")
            return False
        return True
    
    def validate_type(self, field_name: str, value: Any, expected_type: type) -> bool:
        """
        Validate that a field has the correct type.
        
        Args:
            field_name: Name of the field
            value: Value to check
            expected_type: Expected type
            
        Returns:
            True if valid, False otherwise
        """
        if value is not None and not isinstance(value, expected_type):
            self.add_error(
                f"{field_name} must be of type {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
            return False
        return True
    
    def validate_range(
        self,
        field_name: str,
        value: Any,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None
    ) -> bool:
        """
        Validate that a numeric field is within range.
        
        Args:
            field_name: Name of the field
            value: Value to check
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            True if valid, False otherwise
        """
        if value is None:
            return True
        
        if min_value is not None and value < min_value:
            self.add_error(f"{field_name} must be >= {min_value}")
            return False
        
        if max_value is not None and value > max_value:
            self.add_error(f"{field_name} must be <= {max_value}")
            return False
        
        return True
    
    def validate_length(
        self,
        field_name: str,
        value: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> bool:
        """
        Validate string length.
        
        Args:
            field_name: Name of the field
            value: String value to check
            min_length: Minimum length
            max_length: Maximum length
            
        Returns:
            True if valid, False otherwise
        """
        if value is None:
            return True
        
        length = len(value)
        
        if min_length is not None and length < min_length:
            self.add_error(f"{field_name} must be at least {min_length} characters")
            return False
        
        if max_length is not None and length > max_length:
            self.add_error(f"{field_name} must be at most {max_length} characters")
            return False
        
        return True


if __name__ == "__main__":
    # Example implementation for testing
    class TestModel(BaseModel):
        def __init__(self):
            super().__init__()
            self.name = ""
            self.age = 0
        
        def validate(self) -> bool:
            self.clear_errors()
            self.validate_required("name", self.name)
            self.validate_type("age", self.age, int)
            self.validate_range("age", self.age, min_value=0, max_value=150)
            return not self.has_errors()
        
        def to_dict(self) -> Dict[str, Any]:
            return {"name": self.name, "age": self.age}
        
        def from_dict(self, data: Dict[str, Any]) -> None:
            self.name = data.get("name", "")
            self.age = data.get("age", 0)
    
    # Test the model
    print("Testing BaseModel...\n")
    
    model = TestModel()
    model.name = "Test User"
    model.age = 30
    
    # Test validation
    if model.validate():
        print("✓ Model is valid")
    else:
        print("✗ Validation errors:", model.get_errors())
    
    # Test serialization
    json_str = model.to_json()
    print(f"\nJSON representation:\n{json_str}")
    
    # Test deserialization
    model2 = TestModel()
    model2.from_json(json_str)
    print(f"\n✓ Loaded model: {model2.to_dict()}")
    
    # Test validation errors
    model3 = TestModel()
    model3.name = ""  # Invalid
    model3.age = -5   # Invalid
    
    if not model3.validate():
        print(f"\n✗ Validation failed with errors:")
        for error in model3.get_errors():
            print(f"  - {error}")
    
    print("\n✓ BaseModel test complete")
