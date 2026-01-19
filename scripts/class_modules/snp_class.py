from ..utils import modern_messagebox
import pandas as pd
     
class SnpClass:
    def __init__(self):
        self._samples = pd.DataFrame()
        self._microhaps = pd.DataFrame()
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

    # Getter and Setter for microhaps
    def get_microhaps(self):
        return self._microhaps

    def set_microhaps(self, microhaps):
        try:
            if isinstance(microhaps, pd.DataFrame):
                self._microhaps = microhaps
            else:
                raise ValueError("microhaps must be a pandas DataFrame")
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
