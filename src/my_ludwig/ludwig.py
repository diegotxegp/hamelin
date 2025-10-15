import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os

from ludwig.automl import auto_train, create_auto_config
from ludwig.api import LudwigModel
from ludwig.utils.dataset_utils import get_repeatable_train_val_test_split
from ludwig.visualize import compare_performance
from ludwig.visualize import confusion_matrix

def check_available_memory():
    """Check available system memory."""
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        total_gb = memory.total / (1024**3)
        used_percent = memory.percent
        
        print(f"Memory status: {available_gb:.1f}GB available / {total_gb:.1f}GB total ({used_percent:.1f}% used)")
        
        if available_gb < 2.0:
            print("⚠️  Warning: Less than 2GB available memory. Training may fail.")
            return False
        elif available_gb < 4.0:
            print("⚠️  Caution: Less than 4GB available memory. Using conservative settings.")
            return True
        else:
            print("✅ Sufficient memory available for training.")
            return True
    except ImportError:
        print("psutil not available, cannot check memory status")
        return True

def configure_ray_memory():
    """Configure Ray for memory-constrained environments."""
    # Check memory first
    memory_ok = check_available_memory()
    
    # Set conservative memory limits
    os.environ["RAY_memory_usage_threshold"] = "0.85"  # Kill at 85% instead of 95%
    os.environ["RAY_memory_monitor_refresh_ms"] = "1000"  # Check memory every second
    os.environ["RAY_DISABLE_IMPORT_WARNING"] = "1"  # Reduce warnings
    
    # Try to initialize Ray with memory constraints
    try:
        import ray
        if not ray.is_initialized():
            # Adjust memory limits based on available memory
            if memory_ok:
                object_store_mem = 2000000000  # 2GB
                total_mem = 6000000000  # 6GB
            else:
                object_store_mem = 1000000000  # 1GB
                total_mem = 3000000000  # 3GB
                
            ray.init(
                num_cpus=1,  # Limit CPU usage to reduce parallelism
                object_store_memory=object_store_mem,
                _memory=total_mem,
                ignore_reinit_error=True,
                log_to_driver=False  # Reduce logging overhead
            )
        print("Ray configured with memory optimization")
    except Exception as e:
        print(f"Ray initialization warning: {e}")
        # Continue without Ray if it fails to initialize

# Configure Ray memory settings on module import
configure_ray_memory()

class Ludwig:
    def __init__(self):
        self.df = None
        self.target = None
        self.input_features = None
        self.samples = None
        self.separator = None
        self.missing_data = None
        self.runtime = None
        self.metric = None
        self.timedependable = None

        self.config = None
        self.model = None
        self.training_time = None
        self.num_trials = None

    def read_file(self, dataset_path):
        """
        Read the dataframe of a file.
        """
        if dataset_path.endswith((".csv", ".fwf", ".tsv")):
            self.df = pd.read_csv(dataset_path, encoding="utf-8")
        elif dataset_path.endswith((".xlsx", ".xls")):
            self.df =pd.read_excel(dataset_path)
        elif dataset_path.endswith((".feather")):
            self.df = pd.read_feather(dataset_path)
        elif dataset_path.endswith((".h5", ".hdf5")):
            self.df = pd.read_hdf(dataset_path)
        elif dataset_path.endswith((".html", ".htm")):
            self.df = pd.read_html(dataset_path)[0]
        elif dataset_path.endswith((".json", ".jsonl")):
            self.df = pd.read_json(dataset_path)
        elif dataset_path.endswith((".parquet")):
            self.df = pd.read_parquet(dataset_path)
        elif dataset_path.endswith((".pkl", ".pickle")):
            self.df = pd.read_pickle(dataset_path)
        elif dataset_path.endswith((".sas7bdat", ".xpt")):
            self.df = pd.read_sas(dataset_path)
        elif dataset_path.endswith((".sav")):
            self.df = pd.read_spss(dataset_path)
        elif dataset_path.endswith((".dta")):
            self.df = pd.read_stata(dataset_path)
        else:
            return
        
        return self.df

    def auto_train(self, primary_variable):
        """ Automatically trains a model with memory optimization. """

        # Check memory and dataset size before training
        memory_ok = check_available_memory()
        if not memory_ok:
            print("Proceeding with minimal memory configuration...")
            
        # Check dataset size and warn if too large
        dataset_size_mb = self.df.memory_usage(deep=True).sum() / (1024**2)
        num_rows, num_cols = self.df.shape
        print(f"Dataset: {num_rows} rows × {num_cols} columns ({dataset_size_mb:.1f}MB)")
        
        if dataset_size_mb > 500:  # > 500MB
            print("⚠️  Large dataset detected. Consider sampling or feature reduction to avoid memory issues.")
        elif dataset_size_mb > 200:  # > 200MB
            print("⚠️  Medium-large dataset. Using conservative training settings.")

        #split_df = get_repeatable_train_val_test_split(self.df, self.target, random_seed=42)

        # Use configured runtime or default to 7200 seconds
        runtime_limit = int(self.runtime) if self.runtime else 7200
        
        import time
        import os
        start_time = time.time()
        
        # Configure Ray for memory-constrained environments
        ray_config = {
            "cpu": 1,  # Limit to 1 CPU to reduce parallelism
            "memory": int(4 * 1024**3) if not memory_ok else int(6 * 1024**3),  # Adjust based on available memory  
        }
        
        # Set environment variables for Ray memory management
        os.environ["RAY_memory_usage_threshold"] = "0.80" if not memory_ok else "0.85"
        os.environ["RAY_memory_monitor_refresh_ms"] = "500" if not memory_ok else "1000"
        
        try:
            auto_train_results = auto_train(
                dataset=self.df,
                target=primary_variable,
                time_limit_s=runtime_limit,
                tune_for_memory=True,  # Enable memory optimization
                ray_config=ray_config,  # Apply memory constraints
            )
            
            end_time = time.time()
            self.training_time = end_time - start_time
            self.model = auto_train_results.best_model
            
        except Exception as e:
            end_time = time.time()
            self.training_time = end_time - start_time
            
            # Handle memory errors specifically
            if "memory" in str(e).lower() or "oom" in str(e).lower() or "killed" in str(e).lower():
                print("Memory error detected. Trying fallback approach with minimal configuration...")
                
                # Fallback: Use minimal configuration
                try:
                    # Shutdown Ray to free memory
                    import ray
                    if ray.is_initialized():
                        ray.shutdown()
                    
                    # Reinitialize with even more conservative settings
                    ray.init(
                        num_cpus=1,
                        object_store_memory=1000000000,  # 1GB object store
                        _memory=4000000000,  # 4GB total memory limit
                        ignore_reinit_error=True,
                        log_to_driver=False
                    )
                    
                    # Try again with shorter time limit
                    auto_train_results = auto_train(
                        dataset=self.df,
                        target=primary_variable,
                        time_limit_s=min(runtime_limit, 3600),  # Max 1 hour fallback
                        tune_for_memory=True,
                    )
                    
                    self.model = auto_train_results.best_model
                    print("Fallback training completed successfully")
                    
                except Exception as fallback_error:
                    raise Exception(f"Training failed due to memory constraints. Original error: {str(e)}. "
                                  f"Fallback also failed: {str(fallback_error)}. "
                                  f"Try reducing dataset size or increasing available memory.")
            else:
                raise e
        
        # Get number of trials from hyperopt results if available
        try:
            self.num_trials = len(auto_train_results.experiment_analysis.trials)
        except:
            self.num_trials = "Unknown"

        print("Model trained successfully")

        # Use the same dataset for evaluation (in a real scenario, you'd use a separate test set)
        eval_stats, predictions, output_directory = self.model.evaluate(dataset=self.df)
        print("All Evaluation Metrics:")
        for metric_name, value in eval_stats.items():
            print(f"{metric_name}: {value}")

    def autoconfig(self, target):
        """
        Automatically generates a configuration file.
        """
        self.target = target

        self.split_df = get_repeatable_train_val_test_split(self.df, self.target, random_seed=42)

        # Use configured runtime or default to 7200 seconds
        runtime_limit = int(self.runtime) if self.runtime else 7200
        
        # Configure memory optimization for autoconfig as well
        import os
        os.environ["RAY_memory_usage_threshold"] = "0.85"
        os.environ["RAY_memory_monitor_refresh_ms"] = "1000"
        
        self.config = create_auto_config(
            dataset=self.split_df,
            target=self.target,
            time_limit_s=runtime_limit,
            tune_for_memory=True,  # Enable memory optimization
            #user_config={'hyperopt': {'goal': 'maximize', 'metric': 'accuracy', 'output_feature': f"{self.target}"}},
        )

        print("Config generated successfully")

        self.input_features_from_config()
        self.target_from_config()
        self.metric_from_config()
        self.runtime_from_config()
        self.samples_from_config()

    def train(self):
        """
        Train the model.
        """
        self.model = LudwigModel(self.config)
        self.model.train(dataset=self.df)

    def compare_performance(self):
        # Use the training dataset for evaluation (in a real scenario, use a separate test set)
        eval_stats, predictions, output_directory = self.model.evaluate(
            self.df,
            split="full",
            collect_predictions=True,
            collect_overall_stats=True,
            skip_save_eval_stats=False,
            skip_save_predictions=False,
            output_directory="results/test_results",
            return_type="dict"
        )

        compare_performance(
            eval_stats,
            output_feature_name=self.target,
            model_names=None,
            output_directory=None,
            file_format='pdf'
        )

    def confusion_matrix(self):
        # Use the training dataset for evaluation (in a real scenario, use a separate test set)
        eval_stats, predictions, output_directory = self.model.evaluate(
            self.df,
            split="full",
            collect_predictions=True,
            collect_overall_stats=True,
            skip_save_eval_stats=False,
            skip_save_predictions=False,
            output_directory="results/test_results",
            return_type="dict"
        )
        
        confusion_matrix(
            [eval_stats],
            self.model.training_set_metadata,
            output_feature_name = self.target,
            top_n_classes = [10],
            normalize=True,
            model_names=None,
            output_directory=None,
            file_format='pdf'
        )

    def input_features_from_config(self):
        self.input_features = {i_f["column"]: i_f['type'] for i_f in self.config["input_features"]}
    
    def target_from_config(self):
        self.target = {o_f["column"]: o_f['type'] for o_f in self.config["output_features"]}
    
    def metric_from_config(self):
        self.metric = {self.config["hyperopt"]["metric"]:self.config["hyperopt"]["goal"]}
    
    def runtime_from_config(self):
        self.runtime = self.config["hyperopt"]["executor"]["time_budget_s"]
    
    def samples_from_config(self):
        self.samples = self.config["hyperopt"]["executor"]["num_samples"]

    def configuration_to_config(self):
        self.features_to_config()
        self.missing_data_to_config()
        self.runtime_to_config()
        self.metric_to_config()
    
    def features_to_config(self):
        """Set selected features into the config"""
        input_features = []
        output_features = []

        for feature_name, feature_type in self.input_features.items():
                feature = {
                    "name": feature_name,
                    "column": feature_name,
                    "type": feature_type
                }
                input_features.append(feature)

        for feature_name, feature_type in self.target.items():
                feature = {
                    "name": feature_name,
                    "column": feature_name,
                    "type": feature_type
                }
                output_features.append(feature)

        self.config["input_features"] = input_features
        self.config["output_features"] = output_features

        self.config["trainer"]["validation_field"] = output_features[0]["name"]
        self.config["hyperopt"]["output_feature"] = output_features[0]["name"]

        self.target = self.config["output_features"][0]["name"]

    def missing_data_to_config(self):
        self.config["preprocessing"]["missing_value_strategy"] = self.missing_data

    def runtime_to_config(self):
        self.config["hyperopt"]["executor"]["time_budget_s"] = self.runtime
        self.config["hyperopt"]["executor"]["scheduler"]["max_t"] = self.runtime

    def metric_to_config(self):
        for metric, goal in self.metric.items():
            self.config["hyperopt"]["metric"] = metric
            self.config["hyperopt"]["goal"] = goal
