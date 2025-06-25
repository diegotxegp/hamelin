# File formats
file_formats=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("Feather files", "*.feather"),
                ("FWF files", "*.fwf"),
                ("HDF5 files", "*.h5;*.hdf5"),
                ("HTML files", "*.html;*.htm"),
                ("JSON files", "*.json;*.jsonl"),
                ("Parquet files", "*.parquet"),
                ("Pickle files", "*.pkl;*.pickle"),
                ("SAS files", "*.sas7bdat;*.xpt"),
                ("SPSS files", "*.sav"),
                ("Stata files", "*.dta"),
                ("TSV files", "*.tsv"),
                ("All files", "*.*")
            ]

# Types available for input features
input_feature_types = ["binary", "number", "category", "bag", "set", "sequence", "text", "vector", "audio", "date", "h3", "image", "timeseries"]

# Types available for output features
output_feature_types = ["binary", "number", "category", "bag", "set", "sequence", "text", "vector"]

# Punctuation marks to separate columns in datasets
separators = ["comma", "semicolon", "backslash"]

# Options to treat missing data
missing_data_options = ["fill_with_const", "fill_with_mode", "fill_with_mean", "fill_with_false", "bfill", "ffill", "drop_row"]

# Options to select a metric
metrics = {
    "binary": [
        "accuracy", 
        "loss", 
        "precision", 
        "recall", 
        "roc_auc", 
        "specifity"
    ],
    "number": [
        "mean_squared_error", 
        "mean_absolute_error", 
        "root_mean_squared_error", 
        "root_mean_squared_percentage_error", 
        "loss"
    ],
    "category": [
        "accuracy",
        "hits_at_k",
        "loss"
    ]
}

goals = ["maximize", "minimize"]