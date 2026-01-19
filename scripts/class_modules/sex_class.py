from ..utils import modern_messagebox
import pandas as pd

class SexClass:
    def __init__(self):
        self._samples = pd.DataFrame()
        self._sex_loci = pd.DataFrame()
        self._loci = pd.DataFrame()

    # Getter and Setter for samples
    def get_samples(self):
        return self._samples

    def set_samples(self, samples):
        try:
            if isinstance(samples, pd.DataFrame):
                self._samples = samples
            else:
                raise ValueError("samples must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    # Getter and Setter for sex_loci
    def get_sex_loci(self):
        return self._sex_loci

    def set_sex_loci(self, sex_loci):
        try:
            if isinstance(sex_loci, pd.DataFrame):
                self._sex_loci = sex_loci
            else:
                raise ValueError("sex_loci must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    # Getter and Setter for loci
    def get_loci(self):
        return self._loci

    def set_loci(self, loci):
        try:
            if isinstance(loci, pd.DataFrame):
                self._loci = loci
            else:
                raise ValueError("loci must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
