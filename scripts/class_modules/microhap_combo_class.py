
from ..utils import modern_messagebox
import pandas as pd
    
class MicrohapCombo:
    def __init__(self):
        self._name = ""
        self._snp_pos = []
        self._base_freq_df = pd.DataFrame()

    
    def get_name(self):
        return self._name
    
    def set_name(self, name):
        try:
            if isinstance(name, str):
                self._name = name
            else:
                raise ValueError("Name must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_snp_pos(self):
        return self._snp_pos
    
    def set_snp_pos(self, snp_pos):
        try:
            if isinstance(snp_pos, list):
                self._snp_pos = sorted(snp_pos)
            else:
                raise ValueError("snp_pos must be a list")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    def get_base_freq_df(self):
        return self._base_freq_df
    
    def set_base_freq_df(self, base_freq_df):
        try:
            if isinstance(base_freq_df, pd.DataFrame):
                self._base_freq_df = base_freq_df
            else:
                raise ValueError("base_freq_df must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
