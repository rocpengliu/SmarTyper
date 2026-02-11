from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import accuracy_score
import joblib
import numpy as np
from ..utils.utils_common import print_time
from ..utils import modern_messagebox
from ..utils.utils_func import training_each_model_clf
import pdb


class MachineLearningClass:
    def __init__(self):
        self._mh_training_df_dict = {} # locus = pd.DataFrame()
        self._ms_traning_df_dict = {} # locus = pd.DataFrame()
        self._mh_training_model_clf_dict = {}
        self._ms_training_model_clf_dict = {}
        self._mh_model_pred_accu_dict = {} # model training accuracy locus = pd.dataframe()
        self._ms_model_pred_accu_dict = {} # model training accuracy
    
    def set_mh_training_df_dict(self, mh_training_df_dict):
        self._mh_training_df_dict = mh_training_df_dict
    def get_mh_training_df_dict(self):
        return self._mh_training_df_dict
    
    def set_ms_traning_df_dict(self, ms_traning_df_dict):
        self._ms_traning_df_dict = ms_traning_df_dict
    def get_ms_traning_df_dict(self):
        return self._ms_traning_df_dict
    
    def set_mh_training_model_clf_dict(self, mh_training_model_clf_dict):
        self._mh_training_model_clf_dict = mh_training_model_clf_dict
    def get_mh_training_model_clf_dict(self):
        return self._mh_training_model_clf_dict

    def set_ms_training_model_clf_dict(self, ms_training_model_clf_dict):
        self._ms_training_model_clf_dict = ms_training_model_clf_dict
    def get_ms_training_model_clf_dict(self):
        return self._ms_training_model_clf_dict
    
    def set_mh_model_pred_accu_dict(self, mh_model_pred_accu_dict):
        self._mh_model_pred_accu_dict = mh_model_pred_accu_dict
    def get_mh_model_pred_accu_dict(self):
        return self._mh_model_pred_accu_dict
    
    def set_ms_model_pred_accu_dict(self, ms_model_pred_accu_dict):
        self._ms_model_pred_accu_dict = ms_model_pred_accu_dict
    def get_ms_model_pred_accu_dict(self):
        return self._ms_model_pred_accu_dict
    
    def read_training_df(self, parameter_class):
        fpath = parameter_class.get_mlinputfile()
        print(f"reading training file: {fpath}")
        if os.path.isfile(fpath):
            t_df = pd.read_csv(fpath, sep='\t', header = 0)
            if t_df.shape[0] == 0:
                modern_messagebox.showerror("Invalid Input", "training file must not be empty!")
                raise ValueError("training file must not be empty")
            if parameter_class.get_analtype() == "snp" and t_df.shape[1] == 14:
                for locus, locus_df in t_df.groupby('Locus'):
                    self._mh_training_df_dict[locus] = locus_df
            elif parameter_class.get_analtype() == "sat":
                pass
        print(f"training file: {fpath} done")
        
    def training_model_clf(self, parameter_class, log_func = None):
        num_loc = 0
        pass_loc = 0
        failed_loc = 0
        if parameter_class.get_analtype() == "snp":
            print(f"starting to training model")
            with ProcessPoolExecutor() as executor:
                futures = {}
                for locus, locus_df in self._mh_training_df_dict.items():
                    print(f"starting to training model for marker: {locus}")
                    if 'Zygosity' in locus_df.columns:
                        if locus_df['Zygosity'].nunique() >= 3 and locus_df['Zygosity'].value_counts().min() >= 3: # at least 2 classes for training
                            future = executor.submit(training_each_model_clf, locus_df, "snp")
                            futures[future] = locus
                            pass_loc += 1
                        else:
                            failed_loc += 1
                            print(f"Marker {locus} has only {locus_df['Zygosity'].nunique()} members in 'Zygosity', skipping training for this marker.")
                            if log_func is not None:
                                log_func(f"Marker {locus} has only {locus_df['Zygosity'].nunique()} members in 'Zygosity', skipping training for this marker.")
                    else:
                        print(f"DataFrame for marker {locus} missing 'Zygosity' column, skipping training for this marker.")
                        if log_func is not None:
                            log_func(f"DataFrame for marker {locus} missing 'Zygosity' column, skipping training for this marker.")
                for future in as_completed(futures):
                    locus = futures[future]
                    try:
                        if log_func is not None:
                            log_func(f"Training model for marker {locus} completed...")
                        clf_accu = future.result()
                        self._mh_training_model_clf_dict[locus] = clf_accu[0]
                        self._mh_model_pred_accu_dict[locus] = pd.DataFrame({'accuracy':clf_accu[1]}, index=[0])
                        num_loc += 1
                        if num_loc % 10 == 0:
                            if log_func is not None:
                                log_func(f"Trained {num_loc} markers....")
                            print(f"Trained {num_loc} markers....")
                    except Exception as e:
                        print(f"Error training model for marker {locus}: {e}")
                        if log_func is not None:
                            log_func(f"Error training model for marker {locus}: {e}")
            print(f"model training completed")
            if log_func is not None:
                log_func(f"Model training completed for {num_loc} markers, {pass_loc} markers passed for submission, {failed_loc} markers failed the training criteria.\n\n")
                log_func("Model training completed.\n\n")
                log_func(f"Starting to dump training models...")
            joblib.dump(self._mh_training_model_clf_dict, os.path.join(parameter_class.get_mloutputdir(), "all_training_models.pkl"))
            print(f"training model done")
            if log_func is not None:
                log_func("Training models dumped successfully!")
        elif parameter_class.get_analtype() == "sat":
            pass
        return True
    
    def load_training_model_clf(self, parameter_class):
        fpath = parameter_class.get_mlmodelinputfile()
        print(f"reading ml training model file: {fpath}")
        if os.path.isfile(fpath):
            if parameter_class.get_analtype() == "snp":
                self._mh_training_model_clf_dict = joblib.load(fpath)
            elif parameter_class.get_analtype() == "sat":
                pass
            parameter_class.set_mlmodel(True)
        else:
            parameter_class.set_mlmodel(False)
    
    def predict_zygosity(self, parameter_class, locus, df):
        if parameter_class.get_analtype() == "snp":
            new_df = df.copy()
            if 'Sample' in new_df.columns:
                new_df = new_df.drop('Sample', axis = 1)
            if 'Zygosity' in new_df.columns:
                new_df = new_df.drop('Zygosity', axis = 1)
            if locus in self._mh_training_model_clf_dict:
                new_df = new_df.drop('Locus', axis = 1)
                zyg_pred = self._mh_training_model_clf_dict[locus].predict(new_df)
                return zyg_pred
            else:
                return None
        elif parameter_class.get_analtype() == "sat":
            pass