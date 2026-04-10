from ..utils.common import *
from ..utils.colors import COLORS
import customtkinter as ctk
import tkinter as tk
from .job_runner import run_seqtyper
from ..utils.common import bfont, bmfont, header_font, child_button_size

def parameter_setter(parent):
    frame = ctk.CTkFrame(parent, fg_color=COLORS['background'])
    frame.grid(row=0, column=0, sticky="nsew")
    
    # Configure grid row and column weights for expansion
    frame.grid_rowconfigure(0, weight=0)  # Header row does not expand
    frame.grid_rowconfigure(1, weight=1)  # Body row expands
    frame.grid_rowconfigure(2, weight=0)  # Footer row does not expand
    frame.grid_columnconfigure(0, weight=1)  # Center content horizontally
    frame.grid_columnconfigure(1, weight=1)
    
    create_header(frame)
    create_body(frame)
    frame.footer_frame=create_footer(parent, frame)
    return frame

def create_header(frame):
    header_frame = ctk.CTkFrame(frame, fg_color=COLORS['card'], corner_radius=12)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(15, 10), padx=(15, 15))
    header_frame.grid_columnconfigure(0, weight=1)  # Center header content
    
    label = ctk.CTkLabel(header_frame, text="⚙ Parameter Setting", font=header_font,
                         fg_color="transparent", text_color=COLORS['primary'])
    label.pack(side=tk.LEFT, pady=(15, 15), padx=(30, 10))
    
    return header_frame

def create_label_entry(body_frame, sub_frame, row, column, label_name, def_value, parameter_name, parma):
    label_var = ctk.StringVar(value=def_value)
    ctk.CTkLabel(sub_frame, text=label_name, font=bmbfont, text_color="white").grid(row=row, column=column, padx=(10, 10), pady=(5, 5), sticky="e")
    ctk.CTkEntry(sub_frame, justify="center", width=80, textvariable=label_var, height=26).grid(row=row, column=(column + 1), padx=(10, 10), pady=(5, 5), sticky="w")
    label_var.trace_add("write", lambda *arg: getattr(parma, 'set_' + parameter_name, label_var.get()))

def create_checkbox(body_frame, sub_frame, row, column, label_name, def_value, parameter_name, parma):
    checkbox_var = ctk.BooleanVar(value=def_value)
    ctk.CTkLabel(sub_frame, text=label_name, font=bmfont, text_color="white").grid(row=row, column=column, padx=(10, 10), pady=(5, 5), sticky="e")
    ctk.CTkCheckBox(sub_frame, text="yes", variable=checkbox_var, font=bmfont, text_color="white").grid(row=row, column=(column + 1), padx=(10, 10), pady=(5, 5), sticky="w")
    checkbox_var.trace_add("write", lambda *arg: getattr(parma, 'set_' + parameter_name, checkbox_var.get()))

def create_body(frame):
    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
    
     # Configure body_frame columns and rows
    body_frame.grid_columnconfigure(0, weight=1)  # Left panel (2 columns wide)
    body_frame.grid_columnconfigure(1, weight=1)  # Left panel (2 columns wide)
    body_frame.grid_columnconfigure(2, weight=1)  # Middle panel (1 column wide)
    body_frame.grid_columnconfigure(3, weight=1)  # Middle panel (1 column wide)
    body_frame.grid_columnconfigure(4, weight=4)  # Right panel (2 columns wide)
    body_frame.grid_columnconfigure(5, weight=4)  # Right panel (2 columns wide)
    
    body_frame.grid_rowconfigure('all', weight=1)
    
        # Create left panel blended with background
    left_body = ctk.CTkFrame(body_frame, fg_color="transparent")
    left_body.grid(row=0, column=0, columnspan=2, sticky="nw", padx=5, pady=5)

    # Create middle panel blended with background
    middle_body = ctk.CTkFrame(body_frame, fg_color="transparent")
    middle_body.grid(row=0, column=2, columnspan=2, sticky="nw", padx=5, pady=5)

    # Create right panel blended with background
    right_body = ctk.CTkFrame(body_frame, fg_color="transparent")
    right_body.grid(row=0, column=4, columnspan=2, sticky="nw", padx=5, pady=5)
    
    # Configure panels
    left_body.grid_columnconfigure('all', weight=1)
    middle_body.grid_columnconfigure('all', weight=1)
    right_body.grid_columnconfigure('all', weight=1)
    
    left_body.grid_rowconfigure('all', weight=1)
    middle_body.grid_rowconfigure('all', weight=1)
    right_body.grid_rowconfigure('all', weight=1)
    
    param = frame.master.master.genotype_class.get_parameter()  # Adjusted to use parent.master.master
    
    row = 0
    ctk.CTkLabel(left_body, text="General options:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="e")
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Num. thread:", str(param.get_thread()), "thread", param)
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Min. read length:", str(param.get_length_required()), "length_required", param)
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Average quality:", str(param.get_average_qual()), "average_qual", param)
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Primer mismatches:", str(param.get_maxMismatchesPSeq()), "maxMismatchesPSeq", param)
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Min. reads 4 locus:", str(param.get_minReads4Locus()), "minReads4Locus", param)
    row += 1
    
    fig_var = ctk.BooleanVar(value=param.is_pro_figure())
    ctk.CTkLabel(left_body, text="Figure:", font=bmbfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="e")
    ctk.CTkCheckBox(left_body, text="", variable = fig_var, font =bmfont, text_color="white").grid(row=row, column=1, padx=(15, 15),sticky="w")
    fig_var.trace_add("write", lambda *args: param.set_pro_figure(fig_var.get()))
    row += 1

    row = 0
    ctk.CTkLabel(middle_body, text="Analysis type:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="e")
    ctk.CTkLabel(middle_body, text=param.get_analtype(), font=bfont, text_color="red").grid(row=row, column=1, padx=(30, 0), pady=body_frame.pady, sticky="w")
    row += 1

    if param.get_analtype() == "snp":
        create_label_entry(body_frame, middle_body, row, 0, "smProp1H:", str(param.get_smProp1H()), "smProp1H", param)
        row += 1
        create_label_entry(body_frame, middle_body, row, 0, "smProp1L:", str(param.get_smProp1L()), "smProp1L", param)
        row += 1
        create_label_entry(body_frame, middle_body, row, 0, "mmProp1H:", str(param.get_mmProp1H()), "mmProp1H", param)
        row += 1
        create_label_entry(body_frame, middle_body, row, 0, "mmProp1L:", str(param.get_mmProp1L()), "mmProp1L", param)
        row += 1
        create_label_entry(body_frame, middle_body, row, 0, "mProp2:", str(param.get_mProp2()), "mProp2", param)
        row += 1
        # create_label_entry(body_frame, middle_body, row, 0, "sProp3:", str(param.get_sProp3()), "sProp3", param)
        # row += 1
        create_label_entry(body_frame, middle_body, row, 0, "Min. reads for allele:", str(param.get_minReads4Allele()), "minReads4Allele", param)
        row += 1
        create_label_entry(body_frame, middle_body, row, 0, "Max. read variants for alignment:", str(param.get_maxRVs4Align()), "maxRVs4Align", param)
    else:
        pass
    
    row = 0
    ctk.CTkLabel(right_body, text="Sex identification options:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="e")
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "Primer mismatches:", str(param.get_maxMismatchesPSeqSex()), "maxMismatchesPSeqSex", param)
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "Ref. mismatches:", str(param.get_maxMismatchesRefSeqSex()), "maxMismatchesRefSeqSex", param)
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "yxRatio:", str(param.get_yxRatio()), "yxRatio", param)
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "Min. reads for sex allele:", str(param.get_minReadsSexAllele()), "minReadsSexAllele", param)
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "Min. reads for sex variant:", str(param.get_minReadsSexVariant()), "minReadsSexVariant", param)
    return body_frame

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="transparent")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(10, 10), padx=(10, 10), sticky="ew")
    
    # Configure footer_frame to center its content
    footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)
    
    # Previous Button
    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="← Previous", font=pnbuttonfont,
                                    fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                    corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                    command=lambda: on_previous_button_click(parent))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")
    
    # Next Button
    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next →", font=pnbuttonfont,
                                fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                corner_radius=10, height=child_button_size['height'], width=child_button_size['width'], state='disabled',
                                command=lambda: on_run_button_click(parent, footer_frame))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), sticky="w")
    return footer_frame

def on_previous_button_click(parent):
    parent.master.show_page("data")

def on_run_button_click(parent, footer_frame):
    parent.master.genotype_class.get_parameter().check_parameters_valid()
    data_frame=parent.master.pages.get('data', None)
    if data_frame is not None:
        data_frame.footer_frame.next_button.configure(state='disabled')
    parent.master.show_page("run")
    footer_frame.next_button.configure(state="disabled")
    parent.after(100, lambda:run_seqtyper(parent))
