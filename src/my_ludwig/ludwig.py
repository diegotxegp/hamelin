import tkinter as tk
from tkinter import messagebox
import pandas as pd

from ludwig.automl import auto_train, create_auto_config
from ludwig.api import LudwigModel
from ludwig.utils.dataset_utils import get_repeatable_train_val_test_split
from sklearn.model_selection import train_test_split
from ludwig.visualize import compare_performance
from ludwig.visualize import confusion_matrix

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
        """ Automatically trains a model. """

        #split_df = get_repeatable_train_val_test_split(self.df, self.target, random_seed=42)

        # Use configured runtime or default to 7200 seconds
        runtime_limit = int(self.runtime) if self.runtime else 7200
        
        import time
        start_time = time.time()
        
        auto_train_results = auto_train(
            dataset=self.df,
            target=primary_variable,
            time_limit_s=runtime_limit,
            tune_for_memory=False,
        )

        end_time = time.time()
        self.training_time = end_time - start_time
        self.model = auto_train_results.best_model
        
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

        # Determine if target is continuous or discrete
        is_continuous = False
        
        # Validate that target variable has enough samples per class/value
        # Check if variable is numeric
        if pd.api.types.is_numeric_dtype(self.df[target]):
            unique_count = self.df[target].nunique(dropna=True)
            total_count = len(self.df[target].dropna())
            
            print(f"DEBUG: Target '{target}' has {unique_count} unique values out of {total_count} total samples")
            print(f"DEBUG: Uniqueness ratio: {unique_count/total_count:.2%}")
            print(f"DEBUG: Data type: {self.df[target].dtype}")
            
            # Check if variable has real decimal values (not just .0)
            has_decimals = False
            if self.df[target].dtype == 'float64':
                has_decimals = (self.df[target].dropna() % 1 != 0).any()
                print(f"DEBUG: Has real decimal values: {has_decimals}")
            
            # Treat as continuous if: has real decimals OR >50% values are unique
            if has_decimals or unique_count > total_count * 0.5:
                print(f"DEBUG: Variable treated as continuous (regression) - using random split")
                is_continuous = True
            else:
                # It's discrete/categorical - check for values with only 1 sample
                counts = self.df[target].value_counts(dropna=True)
                min_count = counts.min()
                values_with_one = (counts == 1).sum()
                
                print(f"DEBUG: Minimum count per value: {min_count}")
                print(f"DEBUG: Values with only 1 sample: {values_with_one}")
                
                if min_count < 2:
                    raise ValueError(
                        f"The target variable '{target}' has {values_with_one} value(s) with only 1 sample. "
                        f"All values must have at least 2 samples for cross-validation. "
                        f"Please review your inclusion/exclusion criteria or choose a different target variable."
                    )
        else:
            # For categorical/object types
            unique_count = self.df[target].nunique(dropna=True)
            print(f"DEBUG: Target '{target}' has {unique_count} unique categories")
            
            counts = self.df[target].value_counts(dropna=True)
            min_count = counts.min()
            print(f"DEBUG: Minimum count per category: {min_count}")
            
            if min_count < 2:
                raise ValueError(
                    f"The target variable '{target}' has at least one category with only {min_count} sample(s). "
                    f"All categories must have at least 2 samples for cross-validation. "
                    f"Please review your inclusion/exclusion criteria or choose a different target variable."
                )

        # Use different split strategy based on variable type
        if is_continuous:
            # For continuous variables, use random split (no stratification)
            # Split: 70% train, 15% validation, 15% test
            train_val, test = train_test_split(self.df, test_size=0.15, random_state=42)
            train, val = train_test_split(train_val, test_size=0.1765, random_state=42)  # 0.1765 * 0.85 ≈ 0.15
            
            # Add split column
            train['split'] = 0
            val['split'] = 1
            test['split'] = 2
            
            self.split_df = pd.concat([train, val, test], ignore_index=True)
        else:
            # For discrete/categorical variables, use stratified split
            self.split_df = get_repeatable_train_val_test_split(self.df, self.target, random_seed=42)

        # Use configured runtime or default to 7200 seconds
        runtime_limit = int(self.runtime) if self.runtime else 7200
        
        self.config = create_auto_config(
            dataset=self.split_df,
            target=self.target,
            time_limit_s=runtime_limit,
            tune_for_memory=False,
            #user_config={'hyperopt': {'goal': 'maximize', 'metric': 'accuracy', 'output_feature': f"{self.target}"}},
        )

        print("Config generated successfully")
        
        # CRITICAL: Fix metric goal IMMEDIATELY after config generation
        self._fix_metric_goal()

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

    def compare_performance(self, output_dir="results/visualizations"):
        """Generate and save performance comparison chart."""
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
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

        # Get the target name (first output feature)
        target_name = list(self.target.keys())[0] if isinstance(self.target, dict) else self.target

        compare_performance(
            eval_stats,
            output_feature_name=target_name,
            model_names=None,
            output_directory=output_dir,
            file_format='png'
        )
        
        # Ludwig generates the file as compare_performance_{target_name}.png
        return os.path.join(output_dir, f"compare_performance_{target_name}.png")

    def confusion_matrix(self, output_dir="results/visualizations"):
        """Generate and save confusion matrix chart."""
        import os
        import glob
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
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
        
        # Get the target name (first output feature)
        target_name = list(self.target.keys())[0] if isinstance(self.target, dict) else self.target
        
        confusion_matrix(
            [eval_stats],
            self.model.training_set_metadata,
            output_feature_name=target_name,
            top_n_classes=[10],
            normalize=True,
            model_names=None,
            output_directory=output_dir,
            file_format='png'
        )
        
        # Ludwig generates confusion matrix files with pattern: confusion_matrix__{target_name}_top*.png
        # Search for the generated file
        pattern = os.path.join(output_dir, f"confusion_matrix__{target_name}_top*.png")
        matching_files = glob.glob(pattern)
        
        if matching_files:
            # Return the first matching file (usually there's only one)
            return matching_files[0]
        else:
            # Fallback to expected name if pattern search fails
            return os.path.join(output_dir, f"confusion_matrix_{target_name}.png")

    def input_features_from_config(self):
        self.input_features = {i_f["column"]: i_f['type'] for i_f in self.config["input_features"]}
    
    def target_from_config(self):
        self.target = {o_f["column"]: o_f['type'] for o_f in self.config["output_features"]}
    
    def metric_from_config(self):
        """Extract metric and goal from config (goal should already be corrected by _fix_metric_goal)."""
        metric_name = self.config["hyperopt"]["metric"]
        goal = self.config["hyperopt"]["goal"]
        self.metric = {metric_name: goal}
    
    def runtime_from_config(self):
        self.runtime = self.config["hyperopt"]["executor"]["time_budget_s"]
    
    def samples_from_config(self):
        self.samples = self.config["hyperopt"]["executor"]["num_samples"]
    
    def is_classification(self):
        """Check if the target is a classification task (category/binary) or regression (number)."""
        if self.target is None or self.config is None:
            return False
        
        # Get the output feature type
        output_type = self.config["output_features"][0].get("type", "")
        
        # Classification types: category, binary, set
        # Regression types: number
        return output_type in ["category", "binary", "set"]
    
    def _fix_metric_goal(self):
        """Fix the hyperopt goal based on the metric type. Called immediately after config generation."""
        if self.config is None or "hyperopt" not in self.config:
            return
        
        metric_name = self.config["hyperopt"].get("metric", "")
        current_goal = self.config["hyperopt"].get("goal", "")
        
        # Metrics that should be MINIMIZED (lower is better)
        minimize_metrics = [
            "mean_squared_error",
            "mean_absolute_error", 
            "root_mean_squared_error",
            "root_mean_squared_percentage_error",
            "loss"
        ]
        
        # Metrics that should be MAXIMIZED (higher is better)
        maximize_metrics = [
            "accuracy",
            "precision",
            "recall",
            "roc_auc",
            "specificity",
            "hits_at_k"
        ]
        
        # Determine correct goal
        correct_goal = None
        if metric_name in minimize_metrics:
            correct_goal = "minimize"
        elif metric_name in maximize_metrics:
            correct_goal = "maximize"
        
        # Apply correction if needed
        if correct_goal and current_goal != correct_goal:
            print(f"⚠️  Ludwig set goal='{current_goal}' for metric '{metric_name}'")
            print(f"✅ Auto-correcting to goal='{correct_goal}'")
            self.config["hyperopt"]["goal"] = correct_goal

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