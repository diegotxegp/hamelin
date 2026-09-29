"""
Data Model
~~~~~~~~~~

Model for dataset operations and management.

Features:
- Load datasets from CSV/Excel
- Data type detection and conversion
- Missing value handling
- Data quality checks
- Column metadata
- Data transformations

This model wraps pandas DataFrame with additional functionality
specific to clinical research data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from hamelin.model.base_model import BaseModel
from hamelin.utils.logger import log
from hamelin.utils.exceptions import DataLoadError, DataValidationError
from hamelin.utils.config_manager import config
import json


class DataModel(BaseModel):
    """
    Clinical research dataset model.
    
    Manages dataset loading, validation, and transformations.
    Provides metadata about columns and data quality.
    """
    
    def __init__(self):
        """Initialize data model."""
        super().__init__()
        
        self.df: Optional[pd.DataFrame] = None
        self.filepath: Optional[Path] = None
        self.column_metadata: Dict[str, Dict[str, Any]] = {}
        # User-overridden column types (column name -> ludwig type)
        self.column_types: Dict[str, str] = {}
        
        # Data quality metrics
        self.n_rows: int = 0
        self.n_columns: int = 0
        self.missing_values: Dict[str, int] = {}
        self.data_types: Dict[str, str] = {}

        # Outlier exclusions — set of df.index values to filter out before analysis
        self.excluded_rows: set = set()
        # Columns explicitly excluded/hidden by the user (not persisted to disk)
        self.excluded_columns: set = set()
        # Dated history of user changes (see hamelin.core.dataset_changes)
        self.change_log: list = []
        self._logged_state = None
        self._change_reason = None
    
    def load_from_file(
        self,
        filepath: str | Path,
        auto_detect_types: bool = True
    ) -> None:
        """
        Load dataset from file.
        
        Args:
            filepath: Path to CSV or Excel file
            auto_detect_types: Automatically detect and convert data types
            
        Raises:
            DataLoadError: If file cannot be loaded
        """
        filepath = Path(filepath)
        self.filepath = filepath
        
        if not filepath.exists():
            raise DataLoadError(
                filepath.name,
                reason="File not found",
                technical_detail=f"Path: {filepath.absolute()}"
            )
        
        try:
            # Load based on file extension
            extension = filepath.suffix.lower()
            
            if extension == '.csv':
                self.df = pd.read_csv(filepath, encoding='utf-8')
                log.info(f"Loaded CSV file: {filepath.name}")

            elif extension == '.tsv':
                self.df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
                log.info(f"Loaded TSV file: {filepath.name}")

            elif extension in ['.xlsx', '.xls']:
                self.df = pd.read_excel(filepath)
                log.info(f"Loaded Excel file: {filepath.name}")

            elif extension == '.parquet':
                try:
                    self.df = pd.read_parquet(filepath)
                    log.info(f"Loaded Parquet file: {filepath.name}")
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read Parquet file",
                        technical_detail=(f"{type(e).__name__}: {e}.\n" 
                                          "Please ensure 'pyarrow' or 'fastparquet' is installed.")
                    )

            elif extension in ['.jsonl', '.json']:
                # Try JSON Lines first for .jsonl; for .json try lines=True then fallback
                try:
                    if extension == '.jsonl':
                        self.df = pd.read_json(filepath, lines=True)
                    else:
                        try:
                            self.df = pd.read_json(filepath, lines=True)
                        except ValueError:
                            self.df = pd.read_json(filepath)
                    log.info(f"Loaded JSON/JSONL file: {filepath.name}")
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read JSON/JSONL file",
                        technical_detail=f"{type(e).__name__}: {e}"
                    )

            elif extension == '.feather':
                try:
                    self.df = pd.read_feather(filepath)
                    log.info(f"Loaded Feather file: {filepath.name}")
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read Feather file",
                        technical_detail=(f"{type(e).__name__}: {e}.\n" 
                                          "Please ensure 'pyarrow' is installed.")
                    )

            elif extension in ['.h5', '.hdf5']:
                try:
                    # read_hdf may return a dict-like structure; assume first key
                    self.df = pd.read_hdf(filepath)
                    log.info(f"Loaded HDF5 file: {filepath.name}")
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read HDF5 file",
                        technical_detail=f"{type(e).__name__}: {e}. Ensure 'pytables' is installed."
                    )

            elif extension in ['.html', '.htm']:
                try:
                    tables = pd.read_html(filepath)
                    if len(tables) == 0:
                        raise ValueError("No tables found in HTML file")
                    self.df = tables[0]
                    log.info(f"Loaded HTML table from: {filepath.name}")
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read HTML file",
                        technical_detail=f"{type(e).__name__}: {e}"
                    )

            elif extension == '.sav':
                # SPSS
                try:
                    # pandas >=1.0 has read_spss
                    if hasattr(pd, 'read_spss'):
                        self.df = pd.read_spss(filepath)
                    else:
                        # fallback to pyreadstat
                        import pyreadstat
                        df, meta = pyreadstat.read_sav(str(filepath))
                        self.df = df
                    log.info(f"Loaded SPSS (.sav) file: {filepath.name}")
                except ImportError:
                    raise DataLoadError(
                        filepath.name,
                        reason="Missing dependency to read SPSS files",
                        technical_detail="Install 'pyreadstat' (pip install pyreadstat)"
                    )
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read SPSS (.sav) file",
                        technical_detail=f"{type(e).__name__}: {e}"
                    )

            elif extension == '.dta':
                try:
                    self.df = pd.read_stata(filepath)
                    log.info(f"Loaded Stata (.dta) file: {filepath.name}")
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read Stata (.dta) file",
                        technical_detail=f"{type(e).__name__}: {e}"
                    )

            elif extension == '.fwf':
                # Fixed Width Format - documented Ludwig-supported format
                # (docs/ludwig/03_user_guide/user_guide__datasets__
                # supported_formats.md). pandas infers column widths from
                # the file's own alignment when none are given explicitly.
                try:
                    self.df = pd.read_fwf(filepath)
                    log.info(f"Loaded Fixed Width Format file: {filepath.name}")
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read Fixed Width Format (.fwf) file",
                        technical_detail=f"{type(e).__name__}: {e}"
                    )

            elif extension in ['.pkl', '.pickle']:
                # Pickled Pandas DataFrame - documented Ludwig-supported
                # format (same source as .fwf above). Only load pickle
                # files you trust: unpickling can execute arbitrary code,
                # same caveat as opening any other Python pickle.
                try:
                    self.df = pd.read_pickle(filepath)
                    if not isinstance(self.df, pd.DataFrame):
                        raise ValueError(
                            f"Pickle file does not contain a DataFrame (got {type(self.df).__name__})"
                        )
                    log.info(f"Loaded Pickled DataFrame file: {filepath.name}")
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read pickled DataFrame (.pkl) file",
                        technical_detail=f"{type(e).__name__}: {e}"
                    )

            elif extension in ['.xpt', '.sas7bdat']:
                # SAS formats: try pandas.read_sas or pyreadstat
                try:
                    # pandas.read_sas supports 'xport' / 'sas7bdat' depending on engine
                    if hasattr(pd, 'read_sas'):
                        # pandas.read_sas may require sas7bdat or xport support
                        self.df = pd.read_sas(filepath)
                    else:
                        import pyreadstat
                        if extension == '.xpt':
                            df, meta = pyreadstat.read_xport(str(filepath))
                        else:
                            df, meta = pyreadstat.read_sas7bdat(str(filepath))
                        self.df = df
                    log.info(f"Loaded SAS file: {filepath.name}")
                except ImportError:
                    raise DataLoadError(
                        filepath.name,
                        reason="Missing dependency to read SAS files",
                        technical_detail="Install 'pyreadstat' (pip install pyreadstat)"
                    )
                except Exception as e:
                    raise DataLoadError(
                        filepath.name,
                        reason="Failed to read SAS file",
                        technical_detail=f"{type(e).__name__}: {e}"
                    )

            else:
                raise DataLoadError(
                    filepath.name,
                    reason=f"Unsupported file format: {extension}",
                    technical_detail=(
                        "Supported formats: .csv, .tsv, .xlsx, .xls, .parquet, .json, .jsonl, "
                        ".feather, .h5/.hdf5, .html, .sav (SPSS), .dta (Stata), .xpt/.sas7bdat (SAS), "
                        ".fwf (Fixed Width Format), .pkl/.pickle (Pickled DataFrame)"
                    )
                )
            
            # Auto-detect types if requested
            if auto_detect_types:
                self._auto_detect_types()
            
            # Calculate metrics
            self._calculate_metrics()
            
            # Generate column metadata
            self._generate_column_metadata()
            
            self.mark_dirty()
            log.info(f"Dataset loaded: {self.n_rows} rows × {self.n_columns} columns")
            
        except pd.errors.EmptyDataError:
            raise DataLoadError(
                filepath.name,
                reason="File is empty",
                technical_detail="No data found in file"
            )
        
        except Exception as e:
            raise DataLoadError(
                filepath.name,
                reason=str(e),
                technical_detail=f"{type(e).__name__}: {str(e)}"
            )
    
    def _auto_detect_types(self) -> None:
        """
        Automatically detect and convert column data types.
        
        Detects:
        - Numeric columns
        - Categorical columns
        - Date columns
        - Boolean columns
        """
        if self.df is None:
            return
        
        # Get missing value indicators from config
        missing_indicators = config.get('data.missing_value_indicators', ['', 'NA'])
        
        # Replace missing value indicators with NaN
        self.df.replace(missing_indicators, np.nan, inplace=True)
        
        # Try to convert numeric columns
        for col in self.df.columns:
            # Skip if already numeric
            if pd.api.types.is_numeric_dtype(self.df[col]):
                continue

            # Test on a COPY first — only overwrite the column if conversion succeeds
            try:
                converted = pd.to_numeric(self.df[col], errors='coerce')
                if converted.notna().sum() > 0:
                    self.df[col] = converted
                    log.debug(f"Converted '{col}' to numeric")
                    continue
            except Exception:
                pass

            # Try date conversion on a COPY — only apply if at least one value parses
            date_formats = config.get('data.date_formats', ['%Y-%m-%d'])
            for date_format in date_formats:
                try:
                    converted = pd.to_datetime(self.df[col], format=date_format, errors='coerce')
                    if converted.notna().sum() > 0:
                        self.df[col] = converted
                        log.debug(f"Converted '{col}' to datetime")
                        break
                except Exception:
                    continue
        # After auto-detection, keep inferred types in data_types map
        self.data_types = {col: self._map_dtype_to_ludwig(col) for col in self.df.columns}
    
    def _calculate_metrics(self) -> None:
        """Calculate data quality metrics."""
        if self.df is None:
            return
        
        self.n_rows = len(self.df)
        self.n_columns = len(self.df.columns)
        
        # Missing values per column
        self.missing_values = self.df.isnull().sum().to_dict()
        
        # Data types per column
        self.data_types = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
    
    def _generate_column_metadata(self) -> None:
        """Generate metadata for each column."""
        if self.df is None:
            return
        
        max_categorical = config.get('data.max_categorical_unique', 20)
        
        for col in self.df.columns:
            metadata = {
                'name': col,
                'dtype': str(self.df[col].dtype),
                'missing_count': int(self.df[col].isnull().sum()),
                'missing_percent': float(self.df[col].isnull().sum() / len(self.df) * 100),
                'unique_count': int(self.df[col].nunique()),
                'is_numeric': pd.api.types.is_numeric_dtype(self.df[col]),
                'is_categorical': False,
                'is_datetime': pd.api.types.is_datetime64_any_dtype(self.df[col])
            }
            
            # Determine if column should be treated as categorical
            if metadata['unique_count'] <= max_categorical and not metadata['is_numeric']:
                metadata['is_categorical'] = True
            
            # Add statistics for numeric columns
            if metadata['is_numeric']:
                metadata['min'] = float(self.df[col].min()) if self.df[col].notna().any() else None
                metadata['max'] = float(self.df[col].max()) if self.df[col].notna().any() else None
                metadata['mean'] = float(self.df[col].mean()) if self.df[col].notna().any() else None
                metadata['median'] = float(self.df[col].median()) if self.df[col].notna().any() else None
                metadata['std'] = float(self.df[col].std()) if self.df[col].notna().any() else None
            
            # Add categories for categorical columns
            if metadata['is_categorical']:
                metadata['categories'] = self.df[col].unique().tolist()

            # Inferred Ludwig-friendly type
            metadata['inferred_type'] = self._map_dtype_to_ludwig(col)
            # If user has overridden type, record it
            if col in self.column_types:
                metadata['assigned_type'] = self.column_types[col]
            else:
                metadata['assigned_type'] = None

            self.column_metadata[col] = metadata

    def _map_dtype_to_ludwig(self, col: str) -> str:
        """
        Map pandas column to a simplified Ludwig type string.
        This is a best-effort mapping used for UI/inference display.
        """
        if self.df is None or col not in self.df.columns:
            return 'text'
        series = self.df[col]
        # Numeric
        if pd.api.types.is_integer_dtype(series) or pd.api.types.is_float_dtype(series) or pd.api.types.is_numeric_dtype(series):
            # If only two unique non-null values, treat as binary
            uniques = series.dropna().unique()
            if len(uniques) == 2:
                return 'binary'
            return 'number'
        # Datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'date'
        # Object/string with low cardinality -> category
        unique_count = int(series.nunique(dropna=True)) if series is not None else 0
        max_categorical = config.get('data.max_categorical_unique', 20)
        if unique_count <= max_categorical:
            return 'category'
        # Fallback to text
        return 'text'

    def set_column_type(self, column: str, ludwig_type: str) -> None:
        """
        Set/override the Ludwig type for a given column.

        This stores the override in `self.column_types` and updates
        column metadata. It does not automatically persist to disk — callers
        should call `save_state()` to persist project-level state.
        """
        if self.df is None or column not in self.df.columns:
            raise DataValidationError(f"Column not found: {column}")
        # store override
        self.column_types[column] = ludwig_type
        # update metadata entry
        meta = self.column_metadata.get(column, {})
        meta['assigned_type'] = ludwig_type
        self.column_metadata[column] = meta
        self.mark_dirty()

    def clear_column_type(self, column: str) -> None:
        """Remove any user override for `column`."""
        if column in self.column_types:
            del self.column_types[column]
        if column in self.column_metadata:
            self.column_metadata[column]['assigned_type'] = None
        self.mark_dirty()

    def reset_column_types(self) -> None:
        """Remove every user type override, reverting all columns to
        whatever type was originally inferred for them."""
        self.column_types.clear()
        for meta in self.column_metadata.values():
            meta['assigned_type'] = None
        self.mark_dirty()
    
    # ── Outlier exclusion ────────────────────────────────────────────────

    def exclude_outliers(self, std_threshold: float = 3.0) -> int:
        """
        Mark rows with any numeric value beyond ``std_threshold`` standard
        deviations from the column mean as excluded.

        Only numeric columns are considered.  NaN values are ignored when
        computing mean/SD and do not themselves trigger exclusion.

        Args:
            std_threshold: Number of SDs beyond which a value is an outlier.

        Returns:
            Number of *newly* excluded rows (rows already in excluded_rows
            are not double-counted).
        """
        if self.df is None:
            return 0

        numeric_cols = self.get_numeric_columns()
        if not numeric_cols:
            return 0

        outlier_mask = pd.Series(False, index=self.df.index)
        for col in numeric_cols:
            series = self.df[col].dropna()
            if series.empty:
                continue
            mean = series.mean()
            sd = series.std()
            if sd == 0 or np.isnan(sd):
                continue
            col_mask = (self.df[col] - mean).abs() > std_threshold * sd
            outlier_mask = outlier_mask | col_mask.fillna(False)

        new_indices = set(self.df.index[outlier_mask]) - self.excluded_rows
        self._change_reason = f"outliers beyond {std_threshold:g} standard deviations"
        self.excluded_rows.update(new_indices)
        log.info(
            f"exclude_outliers(threshold={std_threshold}): "
            f"{len(new_indices)} new rows excluded, "
            f"{len(self.excluded_rows)} total"
        )
        return len(new_indices)

    def restore_excluded_rows(self) -> None:
        """Clear all outlier exclusions, restoring the full dataset for analysis."""
        count = len(self.excluded_rows)
        self.excluded_rows.clear()
        log.info(f"restore_excluded_rows: {count} rows restored")

    def get_active_df(self) -> "pd.DataFrame":
        """
        Return a copy of the DataFrame with excluded rows removed.

        This is the DataFrame that should be used for analysis / training.
        When no rows are excluded this is equivalent to ``df.copy()``.

        Returns:
            Filtered copy of the DataFrame, or an empty DataFrame if none
            is loaded.
        """
        if self.df is None:
            return pd.DataFrame()

        # Start from the full DataFrame copy
        df = self.df.copy()

        # Apply row exclusions (outliers / removed rows)
        if self.excluded_rows:
            mask = ~df.index.isin(self.excluded_rows)
            df = df.loc[mask]

        # Apply column exclusions (hidden columns)
        if self.excluded_columns:
            cols_to_drop = [c for c in self.excluded_columns if c in df.columns]
            if cols_to_drop:
                df = df.drop(columns=cols_to_drop, errors='ignore')

        return df.copy()

    def get_column_info(self, column: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific column.
        
        Args:
            column: Column name
            
        Returns:
            Column metadata dictionary, or None if not found
        """
        return self.column_metadata.get(column)
    
    def get_numeric_columns(self) -> List[str]:
        """Get list of numeric column names."""
        return [
            col for col, meta in self.column_metadata.items()
            if meta['is_numeric']
        ]
    
    def get_categorical_columns(self) -> List[str]:
        """Get list of categorical column names."""
        return [
            col for col, meta in self.column_metadata.items()
            if meta['is_categorical']
        ]
    
    def get_datetime_columns(self) -> List[str]:
        """Get list of datetime column names."""
        return [
            col for col, meta in self.column_metadata.items()
            if meta['is_datetime']
        ]
    
    def get_quality_report(self) -> Dict[str, Any]:
        """
        Generate data quality report.
        
        Returns:
            Dictionary with quality metrics
        """
        if self.df is None:
            return {}
        
        total_cells = self.n_rows * self.n_columns
        total_missing = sum(self.missing_values.values())
        
        return {
            'n_rows': self.n_rows,
            'n_columns': self.n_columns,
            'total_cells': total_cells,
            'total_missing': total_missing,
            'missing_percent': (total_missing / total_cells * 100) if total_cells > 0 else 0,
            'columns_with_missing': sum(1 for v in self.missing_values.values() if v > 0),
            'numeric_columns': len(self.get_numeric_columns()),
            'categorical_columns': len(self.get_categorical_columns()),
            'datetime_columns': len(self.get_datetime_columns()),
            'duplicate_rows': int(self.df.duplicated().sum())
        }
    
    def validate(self) -> bool:
        """
        Validate dataset.
        
        Returns:
            True if valid, False otherwise
        """
        self.clear_errors()
        
        if self.df is None:
            self.add_error("No dataset loaded")
            return False
        
        if self.df.empty:
            self.add_error("Dataset is empty")
            return False
        
        if len(self.df.columns) == 0:
            self.add_error("Dataset has no columns")
            return False
        
        # Check for duplicate column names
        if len(self.df.columns) != len(set(self.df.columns)):
            self.add_error("Dataset has duplicate column names")
        
        return not self.has_errors()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert data model to dictionary.
        
        Note: Does not include DataFrame data, only metadata.
        
        Returns:
            Dictionary representation
        """
        return {
            'filepath': str(self.filepath) if self.filepath else None,
            'n_rows': self.n_rows,
            'n_columns': self.n_columns,
            'column_metadata': self.column_metadata,
            'missing_values': self.missing_values,
            'data_types': self.data_types
        }

    # ------------------------------------------------------------------
    # Project state persistence
    # ------------------------------------------------------------------

    def _project_state_path(self, project_dir: Path) -> Path:
        """Return the canonical path for the project state file."""
        return (Path(project_dir) / 'project_state.json').resolve()

    def save_state(self, project_dir: Path, extra_state: Optional[Dict[str, Any]] = None) -> None:
        """Save project-level UI/state information to project_state.json.

        The saved object includes: filepath (last dataset), excluded_columns,
        excluded_rows and any keys provided in extra_state.
        """
        try:
            path = self._project_state_path(Path(project_dir))
            payload: Dict[str, Any] = {
                'filepath': str(self.filepath) if self.filepath else None,
                'excluded_columns': sorted(list(self.excluded_columns)) if self.excluded_columns else [],
                'excluded_rows': sorted(list(self.excluded_rows)) if self.excluded_rows else [],
                'saved_at': datetime.utcnow().isoformat() + 'Z'
            }
            if extra_state:
                payload.update(extra_state)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
            log.info(f"Project state saved to {path}")
            from hamelin.core.dataset_changes import save_record
            save_record(self, project_dir)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Failed to save project state to {project_dir}: {exc}")

    def load_state(self, project_dir: Path) -> Dict[str, Any]:
        """Load project_state.json if present.

        Returns a dict with the saved keys. Also applies excluded_rows/columns
        to the current DataModel instance when present.
        """
        result: Dict[str, Any] = {}
        try:
            path = self._project_state_path(Path(project_dir))
            if not path.exists():
                return result
            text = path.read_text(encoding='utf-8')
            obj = json.loads(text)
            # apply known keys
            cols = obj.get('excluded_columns', [])
            rows = obj.get('excluded_rows', [])
            if cols and isinstance(cols, list):
                self.excluded_columns = set([c for c in cols if c in (self.df.columns if self.df is not None else [])])
            if rows and isinstance(rows, list) and self.df is not None:
                # Only keep indices that exist in the current dataframe
                existing = set(self.df.index)
                self.excluded_rows = set([r for r in rows if r in existing])
            # store the full loaded object for UI consumers
            self.project_state = obj
            from hamelin.core.dataset_changes import mark_baseline
            mark_baseline(self, project_dir)
            result = obj
            log.info(f"Project state loaded from {path}")
        except Exception as exc:  # noqa: BLE001
            log.warning(f"Failed to load project state from {project_dir}: {exc}")
        return result
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load data model from dictionary.
        
        Note: Does not restore DataFrame, only metadata.
        
        Args:
            data: Dictionary with model data
        """
        self.filepath = Path(data['filepath']) if data.get('filepath') else None
        self.n_rows = data.get('n_rows', 0)
        self.n_columns = data.get('n_columns', 0)
        self.column_metadata = data.get('column_metadata', {})
        self.missing_values = data.get('missing_values', {})
        self.data_types = data.get('data_types', {})
        
        self.mark_clean()


if __name__ == "__main__":
    # Test DataModel
    print("Testing DataModel...\n")
    
    # Create dummy dataset for testing
    test_data = {
        'patient_id': range(1, 11),
        'age': [45, 52, 38, 61, 29, 55, 48, None, 43, 50],
        'sex': ['M', 'F', 'M', 'M', 'F', 'M', 'F', 'M', 'F', 'M'],
        'diagnosis': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C'],
        'surgery_date': ['2023-01-15', '2023-02-20', '2023-03-10', None, 
                        '2023-05-01', '2023-06-15', '2023-07-20', '2023-08-05',
                        '2023-09-10', '2023-10-15']
    }
    
    test_df = pd.DataFrame(test_data)
    test_file = Path('/tmp/test_dataset.csv')
    test_df.to_csv(test_file, index=False)
    
    # Load data
    model = DataModel()
    model.load_from_file(test_file)
    
    # Validate
    if model.validate():
        print("✓ Dataset is valid\n")
    else:
        print("✗ Validation errors:")
        for error in model.get_errors():
            print(f"  - {error}")
    
    # Get quality report
    print("Data Quality Report:")
    quality = model.get_quality_report()
    for key, value in quality.items():
        print(f"  {key}: {value}")
    
    # Get column types
    print(f"\nNumeric columns: {model.get_numeric_columns()}")
    print(f"Categorical columns: {model.get_categorical_columns()}")
    print(f"Datetime columns: {model.get_datetime_columns()}")
    
    # Get column info
    print(f"\nAge column info:")
    age_info = model.get_column_info('age')
    for key, value in age_info.items():
        print(f"  {key}: {value}")
    
    print("\n✓ DataModel test complete")
