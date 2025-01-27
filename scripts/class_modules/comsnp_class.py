from tkinter import messagebox  # Importing messagebox for error handling

class ComSnpClass:
    def __init__(self):
        self._name = ""
        self._snp_pos=set()
        self._indel_pos=set()
        self._snp_str = "" # 18(A|T), A is from ref, T is from query
        self._only_snp=True
    def get_name(self):
        return self._name
    
    def set_name(self, name):
        try:
            if isinstance(name, str):
                self._name = name
            else:
                raise ValueError("Name must be a string")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
    
    def get_snp_pos(self):
        return self._snp_pos
    
    def set_snp_pos(self, snp_pos):
        try:
            if isinstance(snp_pos, set):
                self._snp_pos = set(sorted(snp_pos))
            else:
                raise ValueError("snp_pos must be a set")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
    
    def get_indel_pos(self):
        return self._indel_pos
    
    def set_indel_pos(self, indel_pos):
        try:
            if isinstance(indel_pos, set):
                self._indel_pos = set(sorted(indel_pos))
            else:
                raise ValueError("indel_pos must be a set")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
    
    def get_snp_str(self):
        return self._snp_str
    
    def set_snp_str(self, snp_str):
        try:
            if isinstance(snp_str, str):
                self._snp_str = snp_str
            else:
                raise ValueError("snp_str must be a string")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def is_only_snp(self):
        return self._only_snp
    
    def set_only_snp(self, only_snp):
        try:
            if isinstance(only_snp, bool):
                self._only_snp = only_snp
            else:
                raise ValueError("only_snps must be a boolean")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
      