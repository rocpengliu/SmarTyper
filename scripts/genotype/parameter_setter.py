import customtkinter as ctk
import tkinter as tk
from .job_runner import run_seqtyper

def parameter_setter(parent):
    frame = ctk.CTkFrame(parent, fg_color="#3b3b3b")
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
    header_frame = ctk.CTkFrame(frame, fg_color="#2b2b2b")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10, 5), padx=(10, 10))
    header_frame.grid_columnconfigure(0, weight=1)  # Center header content
    
    label = ctk.CTkLabel(header_frame, text="Parameter setting", font=("Helvetica", 30, "bold"),
                         fg_color="#2b2b2b", text_color="green")
    label.pack(side=tk.LEFT, pady=(10, 10), padx=(100, 10))
    
    return header_frame

def create_label_entry(body_frame, sub_frame, row, column, label_name, def_value, parameter_name, parma):
    label_var = ctk.StringVar(value=def_value)
    ctk.CTkLabel(sub_frame, text=label_name, font=body_frame.bfont, text_color="white").grid(row=row, column=column, padx=(10, 10), pady=(5, 5), sticky="e")
    ctk.CTkEntry(sub_frame, justify="center", width=80, textvariable=label_var).grid(row=row, column=(column + 1), padx=(10, 10), pady=(5, 5), sticky="w")
    label_var.trace_add("write", lambda *arg: getattr(parma, 'set_' + parameter_name, label_var.get()))

def create_checkbox(body_frame, sub_frame, row, column, label_name, def_value, parameter_name, parma):
    checkbox_var = ctk.BooleanVar(value=def_value)
    ctk.CTkLabel(sub_frame, text=label_name, font=body_frame.bfont, text_color="white").grid(row=row, column=column, padx=(10, 10), pady=(5, 5), sticky="e")
    ctk.CTkCheckBox(sub_frame, text="yes", variable=checkbox_var, font=body_frame.bfont, text_color="white").grid(row=row, column=(column + 1), padx=(10, 10), pady=(5, 5), sticky="w")
    checkbox_var.trace_add("write", lambda *arg: getattr(parma, 'set_' + parameter_name, checkbox_var.get()))

def create_body(frame):
    body_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    body_frame.bfont = ("Helvetica", 15, "bold")
    body_frame.brfont = ("Helvetica", 10, "bold")
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
    
        # Create left panel
    left_body = ctk.CTkFrame(body_frame, fg_color="#3b3b3b")
    left_body.grid(row=0, column=0, columnspan=2, sticky="we")

    # Create middle panel
    middle_body = ctk.CTkFrame(body_frame, fg_color="#3b3b3b")
    middle_body.grid(row=0, column=2, columnspan=2, sticky="we")

    # Create right panel
    right_body = ctk.CTkFrame(body_frame, fg_color="#3b3b3b")
    right_body.grid(row=0, column=4, columnspan=2, sticky="w")
    
    # Configure panels
    left_body.grid_columnconfigure('all', weight=1)
    middle_body.grid_columnconfigure('all', weight=1)
    right_body.grid_columnconfigure('all', weight=1)
    
    left_body.grid_rowconfigure('all', weight=1)
    middle_body.grid_rowconfigure('all', weight=1)
    right_body.grid_rowconfigure('all', weight=1)
    
    param = frame.master.master.genotype_class.get_parameter()  # Adjusted to use parent.master.master
    
    row = 0
    ctk.CTkLabel(left_body, text="General options", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="e")
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Num. thread:", str(param.get_thread()), "thread", param)
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Min. read length:", str(param.get_length_required()), "length_required", param)
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Average quality:", str(param.get_average_qual()), "average_qual", param)
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Primer mismatches:", str(param.get_maxMismatchesPSeq()), "maxMismatchesPSeq", param)
    row += 1
    create_label_entry(body_frame, left_body, row, 0, "Min. reads:", str(param.get_minSeqs()), "minSeqs", param)
    row += 1
    
    fig_var = ctk.BooleanVar(value=param.is_pro_figure())
    ctk.CTkLabel(left_body, text="Figure:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="e")
    ctk.CTkCheckBox(left_body, text="", variable = fig_var, font =body_frame.bfont, text_color="white").grid(row=row, column=1, padx=(15, 15),sticky="w")
    fig_var.trace_add("write", lambda *args: param.set_pro_figure(fig_var.get()))
    row += 1

    row = 0
    ctk.CTkLabel(middle_body, text="Anal type:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="e")
    ctk.CTkLabel(middle_body, text=param.get_analtype(), font=body_frame.bfont, text_color="red").grid(row=row, column=1, padx=(30, 0), pady=body_frame.pady, sticky="w")
    row += 1

    if param.get_analtype() == "snp":
        create_label_entry(body_frame, middle_body, row, 0, "htJetter:", str(param.get_htJetter()), "htJetter", param)
        row += 1
        create_label_entry(body_frame, middle_body, row, 0, "hmPerH:", str(param.get_hmPerH()), "hmPerH", param)
        row += 1
        create_label_entry(body_frame, middle_body, row, 0, "hmPerL:", str(param.get_hmPerL()), "hmPerL", param)
        row += 1
        create_label_entry(body_frame, middle_body, row, 0, "minSeqsPerSnp:", str(param.get_minSeqsPerSnp()), "minSeqsPerSnp", param)
        row += 1
        create_label_entry(body_frame, middle_body, row, 0, "minReads4Filter:", str(param.get_minReads4Filter()), "minReads4Filter", param)
        row += 3
    else:
        pass
    
    row = 0
    ctk.CTkLabel(right_body, text="Sex options", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="e")
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "htJetter:", str(param.get_htJetter()), "htJetter", param)
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "hmPerH:", str(param.get_hmPerH()), "hmPerH", param)
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "hmPerL:", str(param.get_hmPerL()), "hmPerL", param)
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "minSeqsPerSnp:", str(param.get_minSeqsPerSnp()), "minSeqsPerSnp", param)
    row += 1
    create_label_entry(body_frame, right_body, row, 0, "minReads4Filter:", str(param.get_minReads4Filter()), "minReads4Filter", param)
    row += 3
    
    return body_frame

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(10, 10), padx=(10, 10), sticky="ew")
    
    # Configure footer_frame to center its content
    footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)
    
    # Previous Button
    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="Previous", font=("Helvetica", 12, "bold"),
                                    command=lambda: on_previous_button_click(parent))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")
    
    # Next Button
    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next", font=("Helvetica", 12, "bold"), state='disabled',
                                command=lambda: on_run_button_click(parent, footer_frame))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), sticky="w")
    return footer_frame

def on_previous_button_click(parent):
    parent.master.show_page("data")

def on_run_button_click(parent, footer_frame):
    data_frame=parent.master.pages.get('data', None)
    if data_frame is not None:
        data_frame.footer_frame.next_button.configure(state='disabled')
    parent.master.show_page("run")
    footer_frame.next_button.configure(state="disabled")
    parent.after(100, lambda:run_seqtyper(parent))
