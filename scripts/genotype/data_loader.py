import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from ..utils.utils_common import *
import os
import glob
from tkinter import messagebox
from ..class_modules.fastq_class import FastqFile, FastqFileSimple
from .results_viewer import update_combox_from_others

def data_loader(parent):
    frame = ctk.CTkFrame(parent, fg_color="#3b3b3b")
    frame.grid(row=0, column=0, sticky="nsew")
    
    # Configure grid row and column weights for expansion
    frame.grid_rowconfigure(0, weight=0)  # Header row does not expand
    frame.grid_rowconfigure(1, weight=1)  # Body row expands
    frame.grid_rowconfigure(2, weight=0)  # Footer row does not expand
    frame.grid_columnconfigure(0, weight=1)  # Center content horizontally
    frame.grid_columnconfigure(1, weight=1)
    
    frame.header_frame = create_header(frame)
    frame.body_frame = create_body(parent, frame)
    frame.footer_frame = create_footer(parent, frame)
    return frame

def create_header(frame):
    header_frame = ctk.CTkFrame(frame, fg_color="#2b2b2b")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10, 5), padx=(10, 10))
    header_frame.grid_columnconfigure(0, weight=1)  # Center header content
    
    label = ctk.CTkLabel(header_frame, text="Data loading", font=("Helvetica", 30, "bold"),
                         fg_color="#2b2b2b", text_color="green")
    label.pack(side=tk.LEFT, pady=(10, 10), padx=(100, 10))
    return header_frame
def create_body(parent, frame):
    genotype_class = parent.master.genotype_class
    
    body_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    body_frame.bfont = ("Helvetica", 15, "bold")
    body_frame.bmfont=("Helvetica", 12, "bold")
    body_frame.brfont = ("Helvetica", 10, "bold")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(2,2))
    
    body_frame.grid_rowconfigure(0, weight=1) #top panel
    body_frame.grid_rowconfigure(1, weight=6) # bottom panel
    body_frame.grid_columnconfigure(0, weight=1) # top and bottom panels
    
    top_panel = ctk.CTkFrame(body_frame, fg_color="#3b3b3b")
    top_panel.grid(row=0, column=0, sticky="nsw", padx=body_frame.padx, pady=(0,0))
    #top_panel.grid_propagate(False)
    
    bottom_panel = ctk.CTkFrame(body_frame, fg_color="#3b3b3b")
    bottom_panel.grid(row=1, column=0, sticky="nsew", padx=body_frame.padx,pady=(0,0))
    
    top_panel.grid_columnconfigure(0, weight=1) #right panel
    top_panel.grid_rowconfigure('all', weight=1)
    
    # Configure the bottom panel (full width)
    bottom_panel.grid_columnconfigure(0, weight=1)
    bottom_panel.grid_rowconfigure(0, weight=1)
    
    row = 0
    analtype_var = tk.StringVar(value="snp")
    ctk.CTkLabel(top_panel, text="Anal type: ", font = body_frame.bfont, text_color="white").grid(row=row,column=0,padx=body_frame.padx,pady=(1,1),sticky="e")
    ctk.CTkRadioButton(top_panel, text="Snp", font=body_frame.bmfont, value="snp", variable=analtype_var).grid(row=row, column=2, pady=(1,1), padx=(20,80), sticky="ew")  # Stick to right side of cell
    ctk.CTkRadioButton(top_panel, text="Sat", font=body_frame.bmfont, value="sat", variable=analtype_var).grid(row=row, column=2, pady=(1,1), padx=(80,0), sticky="ew")  
    analtype_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_analtype(analtype_var.get()))
    row+=1
    
    radio_readtype = ctk.StringVar(value="pe")
    ctk.CTkLabel(top_panel, text="Read type: ", font = body_frame.bfont, text_color="white").grid(row=row,column=0,padx=body_frame.padx,pady=(1,1),sticky="e")
    ctk.CTkRadioButton(top_panel, text="PE", font=body_frame.bmfont, value="pe", variable=radio_readtype).grid(row=row, column=2, pady=(1,1), padx=(20,80), sticky="ew")  # Stick to right side of cell
    ctk.CTkRadioButton(top_panel, text="SE", font=body_frame.bmfont, value="se", variable=radio_readtype).grid(row=row, column=2, pady=(1,1), padx=(80,0), sticky="ew")
    radio_readtype.trace_add("write", lambda *args: genotype_class.get_parameter().set_seqtype(radio_readtype.get()))
    row+=1
    
    inputdir_var = ctk.StringVar(value=genotype_class.get_parameter().get_inputdir())
    # Label
    ctk.CTkLabel(top_panel, text="Input folder:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    # Entry linked with the StringVar
    top_panel.in_entry = ctk.CTkEntry(top_panel, width=250, textvariable=inputdir_var)
    top_panel.in_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    # Browse Button
    ctk.CTkButton(top_panel, text="Browse", font=body_frame.brfont, height=20, width=50, 
                  command=lambda: indir_browser(top_panel.in_entry, "input")).grid(row=row, column=1, pady=(1,1), sticky="w")
    # Trace changes in the inputdir_var and update the genotype_class parameter accordingly
    inputdir_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_inputdir(inputdir_var.get()))
    row+=1
    
    # sample file
    sample_var = ctk.StringVar(value=genotype_class.get_parameter().get_samplefile())
    ctk.CTkLabel(top_panel, text="Sample file:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    top_panel.sample_entry = ctk.CTkEntry(top_panel, width=250, textvariable=sample_var)
    top_panel.sample_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    ctk.CTkButton(top_panel, text="Browse",font=body_frame.brfont, height=20, width=50, 
                  command=lambda: infile_browser(top_panel.sample_entry, "index")).grid(row=row, column=1, pady=(1,1), sticky="w")
    sample_var.trace_add("write", lambda *args: (genotype_class.get_parameter().set_samplefile(sample_var.get()), 
                                                 genotype_class.get_metadata().read_samplefile(genotype_class.get_parameter()),
                                                 update_combox_from_others(parent)))
    row+=1
    
    loci_var = ctk.StringVar(value=genotype_class.get_parameter().get_locifile())
    ctk.CTkLabel(top_panel, text="Loci file:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    top_panel.loci_entry = ctk.CTkEntry(top_panel, width=250, textvariable=loci_var)
    top_panel.loci_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    ctk.CTkButton(top_panel, text="Browse",font=body_frame.brfont, height=20, width=50, 
                  command=lambda: infile_browser(top_panel.loci_entry, "index")).grid(row=row, column=1, pady=(1,1), sticky="w")
    loci_var.trace_add("write", lambda *args: (genotype_class.get_parameter().set_locifile(loci_var.get()), 
                                               genotype_class.get_metadata().read_locifile(genotype_class.get_parameter(), genotype_class.get_post_microhap())))
    loci_rev_var = ctk.BooleanVar(value=genotype_class.get_parameter().get_revcomloci())
    ctk.CTkCheckBox(top_panel, text="reverse complement", variable = loci_rev_var, font =body_frame.bfont, text_color="white").grid(row=row, column=3, padx=(0, 150),sticky="w")
    loci_rev_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_revcom(loci_rev_var.get()))
    row += 1
    
    # training model
    model_var = ctk.StringVar(value=genotype_class.get_parameter().get_mlmodelinputfile())
    ctk.CTkLabel(top_panel, text="training model (optional):", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    top_panel.model_entry = ctk.CTkEntry(top_panel, width=250, textvariable=model_var)
    top_panel.model_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    ctk.CTkButton(top_panel, text="Browse",font=body_frame.brfont, height=20, width=50, 
                  command=lambda: infile_browser(top_panel.model_entry, "index")).grid(row=row, column=1, pady=(1,1), sticky="w")
    model_var.trace_add("write", lambda *args: (genotype_class.get_parameter().set_mlmodelinputfile(model_var.get()), 
                                              genotype_class.get_machine_learning().load_training_model_clf(genotype_class.get_parameter())))
    row +=1
    
    # sex file
    sex_var = ctk.StringVar(value=genotype_class.get_parameter().get_sexfile())
    ctk.CTkLabel(top_panel, text="Sex file (optional):", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    top_panel.sex_entry = ctk.CTkEntry(top_panel, width=250, textvariable=sex_var)
    top_panel.sex_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    ctk.CTkButton(top_panel, text="Browse",font=body_frame.brfont, height=20, width=50, 
                  command=lambda: infile_browser(top_panel.sex_entry, "index")).grid(row=row, column=1, pady=(1,1), sticky="w")
    sex_var.trace_add("write", lambda *args: (genotype_class.get_parameter().set_sexfile(sex_var.get()), 
                                              genotype_class.get_metadata().read_sexfile(genotype_class.get_parameter())))
    sex_rev_var = ctk.BooleanVar(value=genotype_class.get_parameter().get_revcomsex())
    ctk.CTkCheckBox(top_panel, text="reverse complement", variable = sex_rev_var, font=body_frame.bfont, text_color="white").grid(row=row, column=3, padx=(0, 150), sticky="w")
    sex_rev_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_revcomsex(sex_rev_var.get()))
    row +=1
    
    output_var = ctk.StringVar(value=genotype_class.get_parameter().get_outputdir())
    ctk.CTkLabel(top_panel, text="Output folder:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    top_panel.out_entry = ctk.CTkEntry(top_panel, width=250, textvariable=output_var)
    top_panel.out_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    ctk.CTkButton(top_panel, text="Browse",font=body_frame.brfont, height=20, width=50, 
                  command=lambda: outfile_browser(top_panel.out_entry)).grid(row=row, column=1, pady=(1,1), sticky="w")
    output_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_outputdir(output_var.get()))
    
    #confirm button
    ctk.CTkButton(top_panel, text="Confirm",font=("Helvetica", 18, "bold"), height=40, width=60,
                  command = lambda :confirm_inputfiles(frame, tree_frame, genotype_class)).grid(row=row-1, column=4, pady=(1,1), padx=(0,10), sticky="w")

     # Treeview with Scrollbar
    tree_frame = ctk.CTkFrame(bottom_panel)
    tree_frame.grid(row=0, column=0, columnspan=9, rowspan=20, pady=(0,2), padx=body_frame.padx, sticky="news")
    
    tree_frame.file_tree = ttk.Treeview(tree_frame, columns=('Id', 'File Name', 'Read1', 'Size1', 'Read2', 'Size2', 'Status'), show='headings')
    for col in tree_frame.file_tree['columns']:
        tree_frame.file_tree.heading(col, text=col)
        tree_frame.file_tree.column(col, anchor=tk.CENTER, stretch=True)
    tree_frame.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add Vertical Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree_frame.file_tree.yview)
    tree_frame.file_tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    return body_frame

def update_suffix_state(suffix2_entry, pe=True):
    if pe:
        suffix2_entry.configure(state="normal")
        suffix2_entry.delete(0, 'end')
        suffix2_entry.insert(0, "_R2_001.fastq.gz")
    else:
        suffix2_entry.delete(0, 'end')
        suffix2_entry.configure(state="disabled")

def list_files(dir_path, suffix1, suffix2, pe = True):
    rawfiles=[]
    pattern1 = os.path.join(dir_path, '*' + suffix1)
    files1 = glob.glob(pattern1)
    basesf1 = [get_file_no_suffix(f, suffix1) for f in files1]
    if pe:
        pattern2 = os.path.join(dir_path, '*' + suffix2)
        files2 = glob.glob(pattern2)
        if len(files1)!= len(files2):
            print("Unequal number of files for read1 and read2")
            messagebox.showerror("Error", f"Error running deplexer: pair end files are not paired, please check your files!")
            return []
        basesf2 = [get_file_no_suffix(file, suffix2) for file in files2]
        if basesf1 != basesf2:
            print("base names of read1 and 2 are not identical!")
            messagebox.showerror("Error", f"base names of read1 and 2 are not identical!!")
            return[]
        rawfiles =[FastqFile(dir_path, file, suffix1, suffix2, True) for i, file in enumerate(basesf1)]
    else:
        rawfiles =[FastqFile(dir_path, file, suffix1, suffix2, False) for i, file in enumerate(basesf1)]
    
    return rawfiles

def update_widget_state(frame, stat):
    frame.footer_frame.next_button.configure(state=stat)
    
def update_inputfiles(f):
    input_dir = f.in_entry.get()
    read_type = f.radio_readtype.get()
    is_pe = f.is_pe = (read_type == "pe")
    suffix1 = f.suffix1_entry.get()
    suffix2 = f.suffix2_entry.get()
    out_dir = f.out_entry.get()
    files = list_files(input_dir, suffix1, suffix2, is_pe)
    for tre in f.file_tree.get_children():
        f.file_tree.delete(tre)
    for file in files:
        f.file_tree.insert('', 'end', values=(file.name, file.read1, file.readable_size(), file.read2, file.readable_size(True)))
    
    if len(f.file_tree.get_children()) > 0:
        update_widget_state(f, "normal")
    
def confirm_inputfiles(frame, tree_frame, genotype_class):
    samtab = genotype_class.get_metadata().get_sample_df()
    inputdir = genotype_class.get_parameter().get_inputdir()
    rawfiles=[]
    for index, row in samtab.iterrows():
        if genotype_class.get_parameter().get_seqtype() == "pe":
            rawfiles.append(FastqFileSimple(index+1, row.iloc[0], row.iloc[1], row.iloc[2], inputdir, True))
        elif genotype_class.get_parameter().get_seqtype() == "se":
            rawfiles.append(FastqFileSimple(index+1, row.iloc[0], row.iloc[1], "", inputdir, False))
    
    for tre in tree_frame.file_tree.get_children():
        tree_frame.file_tree.delete(tre)
        
    for file in rawfiles:
        tree_frame.file_tree.insert('', 'end', values=(file.id, file.name, file.read1, file.readable_size(), file.read2, file.readable_size(True), file.status))
    
    if len(tree_frame.file_tree.get_children()) > 0:
        update_widget_state(frame, "normal")
        
def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(5,10), padx=(10, 10), sticky="ew")
    
    # Configure footer_frame to center its content
    footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)
    
    # Previous Button
    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="Previous", font=("Helvetica", 12, "bold"),
                                    command = lambda:parent.master.show_page("genotype"))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")
    
    # Next Button
    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next", font=("Helvetica", 12, "bold"),
                                state="disabled", command = lambda:on_click_next_button(parent, footer_frame))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), sticky="w")
    return footer_frame
def on_click_next_button(parent, footer_frame):
    if footer_frame.next_button.cget('state') == 'normal':
        param_frame = parent.master.pages.get("parameters", None)
        if param_frame is not None:
            param_frame.footer_frame.next_button.configure(state='normal')
    parent.master.genotype_class.get_microhap().init_sam_mar_dicts(parent.master.genotype_class)
    parent.master.show_page("parameters")
    