import tkinter as tk
from tkinter import messagebox
import pandas as pd

from ludwig.automl import auto_train, create_auto_config
from ludwig.api import LudwigModel
from ludwig.utils.dataset_utils import get_repeatable_train_val_test_split
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

    def read_file(self, dataset_path):
        """
        Read the dataframe of a file.
        """
        if dataset_path.endswith((".csv", ".fwf", ".tsv")):
            self.df = pd.read_csv(dataset_path)
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

    def auto_train(self):
        """
        Automatically trains a model.
        """
        columns = self.df.columns.tolist()
        self.target = columns[-1] # Last feature is commonly the target

        #split_df = get_repeatable_train_val_test_split(self.df, self.target, random_seed=42)

        auto_train_results = auto_train(
            dataset=self.df,
            target=self.target,
            time_limit_s=7200,
            tune_for_memory=False,
        )

        self.model = auto_train_results.best_model

        print("Model trained successfully")

        test = r"/home/diegotxe/Visual-Studio/AutoML-Interface/Datasets/Resultados-Ivan/Test/liver-disorders_test.csv"
        self.test = self.read_file(test)

        eval_stats, predictions, output_directory = self.model.evaluate(dataset=self.test)
        print("All Evaluation Metrics:")
        for metric_name, value in eval_stats.items():
            print(f"{metric_name}: {value}")

    def autoconfig(self, target):
        """
        Automatically generates a configuration file.
        """
        self.target = target

        self.split_df = get_repeatable_train_val_test_split(self.df, self.target, random_seed=42)

        self.config = create_auto_config(
            dataset=self.split_df,
            target=self.target,
            time_limit_s=7200,
            tune_for_memory=False,
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
        test = r"/home/diegotxe/Visual-Studio/AutoML-Interface/Comparativa-Resultados-Ivan/Datasets/Test/diabetes_test.csv"
        self.test = self.read_file(test)
        eval_stats, predictions, output_directory = self.model.evaluate(
            self.test,
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
        test = r"/home/diegotxe/Visual-Studio/AutoML-Interface/Comparativa-Resultados-Ivan/Datasets/Test/diabetes_test.csv"
        self.test = self.read_file(test)

        eval_stats, predictions, output_directory = self.model.evaluate(
            self.test,
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
        self.config["hyperopt"]["metric"] = self.metric
        self.config["hyperopt"]["goal"] = self.target
