import platform
import ctypes
import os
import re
from tkinter import filedialog
import customtkinter as ctk
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image, ImageTk
import math
import threading
import datetime
import pprint

matplotlib_lock = threading.Lock()
thread_lock = threading.Lock()
print_lock = threading.Lock()
run_update_lock = threading.Lock()

def print_time(var_name):
    with print_lock:
        cur_time = datetime.datetime.now().strftime("[%H:%M:%S]: ")
        pprint.pprint(f'{cur_time} {var_name}')
def set_dpi_awareness():
    """Set DPI awareness depending on the operating system."""
    system = platform.system()
    try:
        if system == "Windows":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        elif system == "Darwin":
            os.environ['TK_SILENCE_DEPRECATION'] = '1'
        elif system == "Linux":
            os.environ['DISPLAY'] = 'localhost:0.0'
    except AttributeError as ae:
        print(f"Could not set DPI awareness: module 'ctypes' has no attribute 'windll', {ae}")
    except Exception as e:
        print(f"An error occurred while setting DPI awareness: {e}")

def universal_scroll(canvas, event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
def get_file_no_suffix(filename, suffix):
    fbase = os.path.basename(filename)
    return fbase.replace(suffix, "")
    
def get_base_fn(filename):
    """Get the base filename by removing known extensions and specific patterns."""
    known_exts = {".fastq.gz", ".FASTQ.GZ", ".fq.gz", ".FQ.GZ"}
    base_name = os.path.basename(filename)
    
    # Remove known extensions
    for ext in known_exts:
        if base_name.lower().endswith(ext.lower()):
            base_name = base_name[:-len(ext)]
            break

    # Remove suffix patterns
    patterns = [r'_R1_', r'\.R1\.', r'_R1\.']
    for pat in patterns:
        match = re.search(pat, base_name)
        if match:
            base_name = base_name[:match.start()]
            break  # Exit loop once a pattern is matched

    return base_name

def get_fl_types(direct, anno):
    fl_types = set()
    if anno == "index":
        for fl in os.listdir(direct):
            if fl.lower().endswith(".txt"):
                fl_types.add(("Text files", "*.txt"))
            #elif fl.lower().endswith(".tsv"):
                #fl_types.add(("Tab-separated files", "*.tsv"))
    elif anno == "input":
        for fl in os.listdir(direct):
            if fl.lower().endswith(".fastq.gz"):
                fl_types.add(("fastq.gz files", "*.fastq.gz"))
            if fl.lower().endswith(".fq.gz"):
                fl_types.add(("fq.gz files", "*.fq.gz"))
    elif anno=='fa':
        for fl in os.listdir(direct):
            if fl.lower().endswith(".fa"):
                fl_types.add(("fa files", "*.fa"))
    if not fl_types:
        fl_types.add(("All files", "*"))
    return fl_types

def get_com_prefix(fl1, fl2):
    basefl1 = os.path.basename(fl1)
    basefl1 = os.path.splitext(os.path.splitext(basefl1)[0])[0]
    basefl2 = os.path.basename(fl2)
    basefl2 = os.path.splitext(os.path.splitext(basefl2)[0])[0]
    
    com_prefix = os.path.commonprefix([basefl1, basefl2])
    while com_prefix.endswith((".", "_")):
        com_prefix = com_prefix[:-1]
    if com_prefix.lower().endswith("r"):
        com_prefix = com_prefix[:-1]
    while com_prefix.endswith((".", "_")):
        com_prefix = com_prefix[:-1]
    return com_prefix

def infile_browser(entry_widget, filetype, button_widget=None):
    from .modern_file_dialog import modern_file_dialog
    cur_dir = entry_widget.get() or '.'
    if not os.path.exists(cur_dir):
        cur_dir = os.path.dirname(cur_dir) if os.path.dirname(cur_dir) else '.'
    try:
        filename = modern_file_dialog(entry_widget.winfo_toplevel(), 
                                   title="Select File", 
                                   mode="file", 
                                   filetype=filetype,
                                   initialdir=cur_dir,
                                   button_widget=button_widget)
    except Exception as e:
        filename = modern_file_dialog(entry_widget.winfo_toplevel(), 
                                   title="Select File", 
                                   mode="file", 
                                   filetype=filetype,
                                   initialdir=cur_dir,
                                   button_widget=None)
    if filename:
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, filename)
    else:
        print(f"[DEBUG] No file selected or dialog cancelled.")

def indir_browser(entry_widget, filetype, button_widget=None):
    from .modern_file_dialog import modern_file_dialog
    cur_dir = entry_widget.get() or '.'
    if not os.path.exists(cur_dir):
        cur_dir = os.path.dirname(cur_dir) if os.path.dirname(cur_dir) else '.'
    filename = modern_file_dialog(entry_widget.winfo_toplevel(),
                                   title="Select Directory",
                                   mode="directory",
                                   filetype=filetype,
                                   initialdir=cur_dir,
                                   button_widget=button_widget)
    if filename:
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, filename)

def outfile_browser(entry_widget, ext = False, button_widget=None):
    from .modern_file_dialog import modern_file_dialog
    try:
        cur_dir = entry_widget.get() or '.'
        if not os.path.exists(cur_dir):
            cur_dir = os.path.dirname(cur_dir) if os.path.dirname(cur_dir) else '.'
        filename = modern_file_dialog(entry_widget.winfo_toplevel(),
                                       title="Select Output Directory",
                                       mode="directory",
                                       filetype="all",
                                       initialdir=cur_dir,
                                       button_widget=button_widget)
        if filename:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, filename)
    except Exception as e:
        print(f"Error in outfile_browser: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to standard dialog
        from tkinter import filedialog
        filename = filedialog.askdirectory(initialdir=cur_dir, title="Select Output Directory")
        if filename:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, filename)

def update_state(in1_entry, in2_entry, in2_button):
    if in1_entry.get():  # If entry1 is not empty
        in2_entry.configure(state="normal")  # Enable entry2
        in2_button.configure(state="normal")  # Enable button2
    else:
        in2_entry.configure(state="disabled")  # Disable entry2
        in2_button.configure(state="disabled")  # Disable button2

def update_prefix(in1_entry, prefix_entry):
    if in1_entry.get():
        prefix = get_base_fn(in1_entry.get())
        if prefix:
            prefix_entry.delete(0, 'end')
            prefix_entry.insert(0, prefix)
    
def infile_browser_and_update(in1_entry, in2_entry, in2_button, filetype, prefix_entry):
    if in1_entry.get():
        infile_browser(in2_entry, filetype)
    else:
        infile_browser(in1_entry, filetype)
        update_state(in1_entry, in2_entry, in2_button)
    
    if in2_entry.get():
        com_prefix = get_com_prefix(in1_entry.get(), in2_entry.get())
        if com_prefix:
            prefix_entry.delete(0, 'end')
            prefix_entry.insert(0, com_prefix)
    else:
        update_prefix(in1_entry, prefix_entry)

def freeze_ui(frame):
    for widget in frame.winfo_children():
        widget.configure(state="disabled")
        if isinstance(widget, ctk.CTkButton):
            widget.configure(state="disabled")

def unfreeze_ui(frame):
    for widget in frame.winfo_children():
        widget.configure(state="normal")
        if isinstance(widget, ctk.CTkButton):
            widget.configure(state="normal")
            
def check_and_convert(target_snppos):
    # Check if the value is the string 'nan' (case insensitive)
    if str(target_snppos).lower() == "nan":
        return []  # Return an empty list for 'nan'

    try:
        # Attempt to convert the value to a float
        float_value = float(target_snppos)
        if math.isnan(float_value):  # Check for NaN
            return []  # Return an empty list for NaN
        else:
            # If the conversion was successful and it's not NaN, return value as a list
            return [int(float_value)]  # Convert the float to int and return as a list
    except ValueError:
        # In the case of ValueError, check for pipe-separated values
        if '|' in str(target_snppos):
            # If the string contains pipes, split it and convert each part to an integer
            return list(map(int, str(target_snppos).split("|")))
        else:
            # If it's not a valid number or a pipe-separated string, return an empty list
            # Alternatively, you can raise an exception or return a custom value
            return []
