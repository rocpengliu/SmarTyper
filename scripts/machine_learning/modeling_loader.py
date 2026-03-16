import queue
from ..utils.common import parent_button_size, child_button_size
import customtkinter as ctk
import tkinter as tk
from ..utils.utils_common import *
from ..utils.colors import COLORS
from ..utils.common import bfont, bmfont, brfont, bmfont, header_font, pnbuttonfont, confirm_button_font, fig_font, parent_button_size, child_button_size
import pdb
from ..utils.modern_messagebox import showsuccess, showerror
import threading

def modeling_loader(parent):
    frame = ctk.CTkFrame(parent, fg_color=COLORS['background'])
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
    header_frame = ctk.CTkFrame(frame, fg_color=COLORS['card'], corner_radius=12)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(15, 10), padx=(15, 15))
    header_frame.grid_columnconfigure(0, weight=1)  # Center header content
    label = ctk.CTkLabel(header_frame, text="★ Model Training", font=header_font,
                         fg_color="transparent", text_color=COLORS['success'])
    label.pack(side=tk.LEFT, pady=(15, 15), padx=(30, 10))
    return header_frame

def create_body(parent, frame):
    genotype_class = parent.master.genotype_class

    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, sticky="nsew", pady=(2,2))

    body_frame.grid_rowconfigure(0, weight=1) #top panel
    body_frame.grid_rowconfigure(1, weight=6) # bottom panel
    body_frame.grid_rowconfigure(2, weight=1) # 
    body_frame.grid_columnconfigure(0, weight=1) # top and bottom panels
    body_frame.grid_columnconfigure(1, weight=1) # top and bottom panels
    
    body_frame.top_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    body_frame.top_panel.grid(row=0, column=0, sticky="nsw", padx=(100,20), pady=(10,10))
    body_frame.top_panel.grid_columnconfigure(0, weight=1) #right panel
    body_frame.top_panel.grid_rowconfigure('all', weight=1)
    body_frame.log_queue = queue.Queue()
    body_frame.res_queue = queue.Queue()
    poll_log_text(body_frame)

    row = 0
    analtype_var = tk.StringVar(value="snp")
    ctk.CTkLabel(body_frame.top_panel, text="Analysis type: ", font = bfont, text_color="white").grid(row=row,column=0,padx=body_frame.padx,pady=(1,1),sticky="e")
    ctk.CTkRadioButton(body_frame.top_panel, text="Snp", font=bmfont, value="snp", variable=analtype_var,
                       fg_color=COLORS['success'], hover_color=COLORS['accent']).grid(row=row, column=2, pady=(1,1), padx=(20,80), sticky="ew")  # Stick to right side of cell
    ctk.CTkRadioButton(body_frame.top_panel, text="Sat", font=bmfont, value="sat", variable=analtype_var,
                       fg_color=COLORS['success'], hover_color=COLORS['accent']).grid(row=row, column=2, pady=(1,1), padx=(80,0), sticky="ew")  
    analtype_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_analtype(analtype_var.get()))
    row+=1
    
    #training file
    training_var = ctk.StringVar(value=genotype_class.get_parameter().get_mlinputfile())
    ctk.CTkLabel(body_frame.top_panel, text="Training file:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.training_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=training_var,
                                         height=26, corner_radius=8, border_width=2)
    body_frame.top_panel.training_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    training_browse_btn = ctk.CTkButton(body_frame.top_panel, text="Browse",font=brfont, height=child_button_size['height'], width=child_button_size['width'],
                  corner_radius=8, fg_color=COLORS['success'], hover_color=COLORS['accent'])
    training_browse_btn.configure(command=lambda btn=training_browse_btn: infile_browser(body_frame.top_panel.training_entry, "index", btn))
    training_browse_btn.grid(row=row, column=1, pady=(1,1), sticky="w")
    training_var.trace_add("write", lambda *args: (genotype_class.get_parameter().set_mlinputfile(training_var.get()),
                                                    genotype_class.get_machine_learning().read_training_df(genotype_class.get_parameter())))
    row += 1
    
    output_var = ctk.StringVar(value=genotype_class.get_parameter().get_mloutputdir())
    ctk.CTkLabel(body_frame.top_panel, text="Output folder:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.out_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=output_var,
                                         height=26, corner_radius=8, border_width=2)
    body_frame.top_panel.out_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    ml_output_browse_btn = ctk.CTkButton(body_frame.top_panel, text="Browse",font=brfont, height=child_button_size['height'], width=child_button_size['width'],
                  corner_radius=8, fg_color=COLORS['success'], hover_color=COLORS['accent'])
    ml_output_browse_btn.configure(command=lambda btn=ml_output_browse_btn: outfile_browser(body_frame.top_panel.out_entry, False, btn))
    ml_output_browse_btn.grid(row=row, column=1, pady=(1,1), sticky="w")
    output_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_mloutputdir(output_var.get()))

     #confirm button
    body_frame.top_panel.confirm_btn = ctk.CTkButton(body_frame.top_panel, text="Confirm",font=confirm_button_font, height=parent_button_size['height'], width=parent_button_size['width'],
                  fg_color=COLORS['success'], hover_color=COLORS['accent'], corner_radius=10, state="normal")
    body_frame.top_panel.confirm_btn.configure(
        command=lambda: on_confirm(body_frame.top_panel.confirm_btn, frame, body_frame, genotype_class)
    )
    body_frame.top_panel.confirm_btn.grid(row=row, column=3, pady=(5,5), padx=(10,10), sticky="w")
    
    body_frame.bottom_panel = ctk.CTkFrame(body_frame, fg_color=COLORS['border'], border_color="white", border_width=3, corner_radius=8)
    body_frame.bottom_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(50,10), pady=(10,10))
    body_frame.bottom_panel.grid_rowconfigure(0, weight=1)
    body_frame.bottom_panel.grid_columnconfigure(0, weight=1)

    body_frame.log_text = ctk.CTkTextbox(
        body_frame.bottom_panel,
        wrap="word",
        font=bmfont,
        state="disabled",
        text_color="white",
        fg_color=COLORS['background']
    )
    body_frame.log_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
    
    return body_frame

def on_confirm(btn, frame, body_frame, genotype_class):
    btn.configure(text="Processing...", state="disabled")
    threading.Thread(target = run_pool,
                     args = (genotype_class, body_frame),
                     daemon=True).start()
    frame.after(100, lambda: check_res_run(frame, body_frame, genotype_class, btn))

def run_pool(genotype_class, body_frame):
    def log_msg(msg):
            body_frame.log_queue.put(msg)
    log_msg("Starting model training and this could take a while. Please be patient...\n\n")
    try:
        go = genotype_class.get_machine_learning().training_model_clf(genotype_class.get_parameter(), log_func = log_msg)
        if go:
            log_msg("Model training completed successfully! Please upload to 'Genotype module' to continue!")
            body_frame.res_queue.put(("success", go))
        else:
            log_msg("Model training failed. Please check the input files and try again.")
            body_frame.res_queue.put(("error", go))
    except Exception as e:
        error_msg = str(e)
        body_frame.after(0, lambda: showerror(body_frame, "Error", f"An error occurred during model training: {error_msg}"))
        log_msg(f"An error occurred during model training: {error_msg}")
        body_frame.res_queue.put((error_msg, False))
        return
    
def check_res_run(frame, body_frame, genotype_class, btn):
    try:
        status, res = body_frame.res_queue.get_nowait()
        if status == "success" and res:
            btn.configure(text="Confirm", state="normal")
            frame.footer_frame.next_button.configure(state="normal")
            showsuccess(frame, "Success", "Model training completed successfully!")
        else:
            btn.configure(text="Confirm", state="normal")
            showerror(frame, "Error", "Model training failed. Please check the input files and try again.")
    except queue.Empty:
        frame.after(100, lambda: check_res_run(frame, body_frame, genotype_class, btn))
        
def poll_log_text(body_frame):
    try:
        while True:
            msg = body_frame.log_queue.get_nowait()
            body_frame.log_text.configure(state="normal")
            cur_time = datetime.datetime.now().strftime("[%H:%M:%S]: ")
            body_frame.log_text.insert(tk.END, cur_time + msg + "\n\n")
            body_frame.log_text.see(tk.END)
            body_frame.log_text.configure(state="disabled")
    except queue.Empty:
        pass
    body_frame.after(100, lambda: poll_log_text(body_frame))

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="transparent")
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
    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Home →", font=pnbuttonfont, state="disabled",
                                            fg_color=COLORS['success'], hover_color=COLORS['accent'],
                                            corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                            command=lambda: parent.master.show_page("home"))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), pady=(10, 10), sticky="w")
    return footer_frame