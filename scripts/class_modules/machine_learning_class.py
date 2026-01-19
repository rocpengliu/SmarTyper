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
                raise ValueError("training file must not be empty")
            if parameter_class.get_analtype() == "snp" and t_df.shape[1] == 14:
                for locus, locus_df in t_df.groupby('Locus'):
                    self._mh_training_df_dict[locus] = locus_df
            elif parameter_class.get_analtype() == "sat":
                pass
        print(f"training file: {fpath} done")
    def training_model_clf(self, parameter_class):
        if parameter_class.get_analtype() == "snp":
            print(f"starting to trianing model")
            for locus, locus_df in self._mh_training_df_dict.items():
                print(f"starting to trianing model for maker: {locus}")   
                clf_accu = self.training_each_model_clf(locus_df, "snp")
                self._mh_training_model_clf_dict[locus] = clf_accu[0]
                self._mh_model_pred_accu_dict[locus] = pd.DataFrame({'accuracy':clf_accu[1]}, index=[0])
            joblib.dump(self._mh_training_model_clf_dict, os.path.join(parameter_class.get_mloutputdir(), "all_training_models.pkl"))
            print(f"trianing model done")
        elif parameter_class.get_analtype() == "sat":
            pass
    def training_each_model_clf(self, df, micro_type):
        if micro_type == "snp":
            X_tot = df.drop(['Locus', 'Zygosity'], axis = 1)
            if 'Zygosity' not in df.columns:
                raise ValueError("DataFrame missing 'Zygosity' column, cannot train!")
            y = df['Zygosity']
            X_train,X_test, y_train, y_test = train_test_split(X_tot, y, test_size = 0.2, random_state = 42, stratify=y)
            clf = GradientBoostingClassifier(random_state = 42)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            return [clf, accuracy]
        elif micro_type == "sat":
            pass
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