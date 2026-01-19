from ..utils.common import parent_button_size, child_button_size
import customtkinter as ctk
import tkinter as tk
from ..utils import modern_messagebox
from ..utils.utils_common import *
from ..utils.common import header_font, pnbuttonfont, confirm_button_font, bfont, brfont
from ..utils.colors import COLORS
from ..genotype.results_geno_combo import update_genotype_tab
from ..genotype.results_viewer import update_combox_from_others
import pdb


def project_loader(parent):
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
    header_frame.grid_columnconfigure(0, weight=1)
    label = ctk.CTkLabel(header_frame, text="● Project Loading", font=header_font,
                         fg_color="transparent", text_color=COLORS['workflow_gold'])
    label.pack(side=tk.LEFT, pady=(15, 15), padx=(30, 10))
    return header_frame

def create_body(parent, frame):
    genotype_class = parent.master.genotype_class

    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, sticky="nsew", pady=(2,2))

    body_frame.grid_rowconfigure(0, weight=1) #top panel
    body_frame.grid_rowconfigure(1, weight=1) # bottom panel
    body_frame.grid_columnconfigure(0, weight=1) # top and bottom panels
    body_frame.grid_columnconfigure(1, weight=1) # top and bottom panels
    
    body_frame.top_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    body_frame.top_panel.grid(row=0, column=0, sticky="nsw", padx=(100,20), pady=(10,10))
    body_frame.top_panel.grid_columnconfigure(0, weight=1) #right panel
    body_frame.top_panel.grid_rowconfigure('all', weight=1)

    row = 0

    n_thread_var = tk.IntVar(value=genotype_class.get_parameter().get_thread())
    ctk.CTkLabel(body_frame.top_panel, text="Num. thread:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.n_thread = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=n_thread_var, height=26)
    body_frame.top_panel.n_thread.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    n_thread_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_thread(n_thread_var.get()))
    row += 1

    input_var = ctk.StringVar(value=genotype_class.get_parameter().get_outputdir())
    ctk.CTkLabel(body_frame.top_panel, text="Input folder:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.out_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=input_var,
                                      height=26, corner_radius=8, border_width=2)
    body_frame.top_panel.out_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    project_browse_btn = ctk.CTkButton(body_frame.top_panel, text="Browse",font=brfont, height=child_button_size['height'], width=child_button_size['width'],
                  corner_radius=8, fg_color=COLORS['workflow_gold'], hover_color=COLORS['secondary'])
    project_browse_btn.configure(command=lambda btn=project_browse_btn: outfile_browser(body_frame.top_panel.out_entry, False, btn))
    project_browse_btn.grid(row=row, column=1, pady=(1,1), sticky="w")
    input_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_outputdir(input_var.get()))
    row += 1

    # Confirm button with feedback
    confirm_btn = ctk.CTkButton(body_frame.top_panel, text="Confirm", font=confirm_button_font, height=parent_button_size['height'], width=parent_button_size['width'],
                                fg_color=COLORS['workflow_gold'], hover_color=COLORS['secondary'], corner_radius=10)
    confirm_btn.configure(command=lambda btn=confirm_btn: on_confirm(btn, frame, genotype_class))
    confirm_btn.grid(row=row-1, column=4, pady=(10,10), padx=(20,10), sticky="w")
    return body_frame

def on_confirm(btn, frame, genotype_class):
    btn.configure(text="Processing...", state="disabled")
    frame.after(100, lambda: confirm_inputfiles(frame, genotype_class, btn))
def confirm_inputfiles(frame, genotype_class, btn=None):
    try:
        go = genotype_class.load_session("genotype", parent=frame)
        if go:
            update_widget_state(frame, 'normal')
        else:
            update_widget_state(frame, 'disabled')
            modern_messagebox.showerror(frame, "Error", "One or more input files are missing or corrupted.")
    except Exception as e:
        update_widget_state(frame, 'disabled')
        modern_messagebox.showerror(frame, "Error", str(e))
    finally:
        if btn is not None:
            btn.configure(text="Confirm", state="normal")

def update_widget_state(frame, stat):
    frame.footer_frame.next_button.configure(state=stat)

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="transparent")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(5,10), padx=(10, 10), sticky="ew")

    # Configure footer_frame to center its content
    footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)

    # Previous Button
    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="← Previous", font=pnbuttonfont,
                                    fg_color=COLORS['workflow_gold'], hover_color=COLORS['secondary'],
                                    corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                    command = lambda:parent.master.show_page("project"))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")

    # Next Button
    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next →", font=pnbuttonfont,
                                fg_color=COLORS['workflow_gold'], hover_color=COLORS['secondary'],
                                corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
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