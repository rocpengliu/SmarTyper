import customtkinter as ctk
import tkinter as tk
from ..utils.utils_common import *
from ..genotype.results_geno_combo import update_genotype_tab
from ..genotype.results_viewer import update_combox_from_others
import pdb

def project_loader(parent):
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
    label = ctk.CTkLabel(header_frame, text="Project loading", font=("Helvetica", 30, "bold"),
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

    n_thread_var = tk.IntVar(value=genotype_class.get_parameter().get_thread())
    ctk.CTkLabel(body_frame.top_panel, text="Num. thread:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.n_thread = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=n_thread_var)
    body_frame.top_panel.n_thread.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    n_thread_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_thread(n_thread_var.get()))
    row += 1

    input_var = ctk.StringVar(value=genotype_class.get_parameter().get_outputdir())
    ctk.CTkLabel(body_frame.top_panel, text="Input folder:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.out_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=input_var)
    body_frame.top_panel.out_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    ctk.CTkButton(body_frame.top_panel, text="Browse",font=body_frame.brfont, height=20, width=50, 
                  command=lambda: outfile_browser(body_frame.top_panel.out_entry)).grid(row=row, column=1, pady=(1,1), sticky="w")
    input_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_outputdir(input_var.get()))
    row += 1

     #confirm button
    ctk.CTkButton(body_frame.top_panel, text="Confirm",font=("Helvetica", 18, "bold"), height=40, width=60,
                  command = lambda :confirm_inputfiles(frame, genotype_class)).grid(row=row-1, column=4, pady=(1,1), padx=(20,10), sticky="w")
    return body_frame

def confirm_inputfiles(frame, genotype_class):
    go = genotype_class.load_session("genotype")
    if go:
        update_widget_state(frame, 'normal')
    else:
        update_widget_state(frame, 'disabled')
        messagebox.showerror("Error", "One or more input files are missing or corrupted.")
        return

def update_widget_state(frame, stat):
    frame.footer_frame.next_button.configure(state=stat)

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(5,10), padx=(10, 10), sticky="ew")

    # Configure footer_frame to center its content
    footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)

    # Previous Button
    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="Previous", font=("Helvetica", 12, "bold"),
                                    command = lambda:parent.master.show_page("project"))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")

    # Next Button
    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next", font=("Helvetica", 12, "bold"),
                                state="disabled", command = lambda:on_click_next_button(parent, footer_frame))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), sticky="w")
    return footer_frame
def on_click_next_button(parent, footer_frame):
    if footer_frame.next_button.cget('state') == 'normal':
        parent.after(100, lambda:parent.master.show_page("results"))
        panel = parent.master.pages.get('results').body_frame.bottom_panel
        if panel.winfo_exists():
            update_combox_from_others(parent)
            update_genotype_tab(parent,panel)