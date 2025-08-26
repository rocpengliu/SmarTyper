import customtkinter as ctk
import tkinter as tk
from ..utils.utils_common import *
import pdb

def modeling_loader(parent):
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
    label = ctk.CTkLabel(header_frame, text="Training data loading", font=("Helvetica", 30, "bold"),
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
    body_frame.grid(row=1, column=0, sticky="nsew", pady=(2,2))

    body_frame.grid_rowconfigure(0, weight=1) #top panel
    body_frame.grid_rowconfigure(1, weight=1) # bottom panel
    body_frame.grid_columnconfigure(0, weight=1) # top and bottom panels
    body_frame.grid_columnconfigure(1, weight=1) # top and bottom panels
    
    body_frame.top_panel = ctk.CTkFrame(body_frame, fg_color="#3b3b3b")
    body_frame.top_panel.grid(row=0, column=0, sticky="nsw", padx=(100,20), pady=(10,10))
    body_frame.top_panel.grid_columnconfigure(0, weight=1) #right panel
    body_frame.top_panel.grid_rowconfigure('all', weight=1)

    row = 0
    analtype_var = tk.StringVar(value="snp")
    ctk.CTkLabel(body_frame.top_panel, text="Anal type: ", font = body_frame.bfont, text_color="white").grid(row=row,column=0,padx=body_frame.padx,pady=(1,1),sticky="e")
    ctk.CTkRadioButton(body_frame.top_panel, text="Snp", font=body_frame.bmfont, value="snp", variable=analtype_var).grid(row=row, column=2, pady=(1,1), padx=(20,80), sticky="ew")  # Stick to right side of cell
    ctk.CTkRadioButton(body_frame.top_panel, text="Sat", font=body_frame.bmfont, value="sat", variable=analtype_var).grid(row=row, column=2, pady=(1,1), padx=(80,0), sticky="ew")  
    analtype_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_analtype(analtype_var.get()))
    row+=1
    
    #training file
    training_var = ctk.StringVar(value=genotype_class.get_parameter().get_mlinputfile())
    ctk.CTkLabel(body_frame.top_panel, text="Traning file:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.training_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=training_var)
    body_frame.top_panel.training_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    ctk.CTkButton(body_frame.top_panel, text="Browse",font=body_frame.brfont, height=20, width=50, 
                  command=lambda: infile_browser(body_frame.top_panel.training_entry, "index")).grid(row=row, column=1, pady=(1,1), sticky="w")
    training_var.trace_add("write", lambda *args: (genotype_class.get_parameter().set_mlinputfile(training_var.get()),
                                                    genotype_class.get_machine_learning().read_training_df(genotype_class.get_parameter())))
    row += 1
    
    output_var = ctk.StringVar(value=genotype_class.get_parameter().get_mloutputdir())
    ctk.CTkLabel(body_frame.top_panel, text="Output folder:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.out_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=output_var)
    body_frame.top_panel.out_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    ctk.CTkButton(body_frame.top_panel, text="Browse",font=body_frame.brfont, height=20, width=50, 
                  command=lambda: outfile_browser(body_frame.top_panel.out_entry)).grid(row=row, column=1, pady=(1,1), sticky="w")
    output_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_mloutputdir(output_var.get()))

     #confirm button
    ctk.CTkButton(body_frame.top_panel, text="Confirm",font=("Helvetica", 18, "bold"), height=40, width=60,
                  command = lambda :confirm_inputfiles(frame, genotype_class)).grid(row=row-1, column=4, pady=(1,1), padx=(20,10), sticky="w")
    return body_frame

def confirm_inputfiles(frame, genotype_class):
    genotype_class.get_machine_learning().training_model_clf(genotype_class.get_parameter())
    # if go:
    #     update_widget_state(frame, 'normal')
    # else:
    #     update_widget_state(frame, 'disabled')
    #     messagebox.showerror("Error", "One or more input files are missing or corrupted.")
    #     return

#def update_widget_state(frame, stat):
    #frame.footer_frame.next_button.configure(state=stat)

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(5,10), padx=(10, 10), sticky="ew")

    # Configure footer_frame to center its content
    footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)

    # Previous Button
    #footer_frame.previous_button = ctk.CTkButton(footer_frame, text="Previous", font=("Helvetica", 12, "bold"),
                                    #command = lambda:parent.master.show_page("project"))
    #footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")

    # Next Button
    #footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next", font=("Helvetica", 12, "bold"),
                                #state="disabled", command = lambda:on_click_next_button(parent, footer_frame))
    #footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), sticky="w")
    return footer_frame