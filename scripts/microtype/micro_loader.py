
import customtkinter as ctk
import tkinter as tk
from ..utils.utils_common import *
from .micro_viewer import update_combox_from_others
from ..utils import modern_messagebox
from ..utils.colors import COLORS
from ..utils.common import parent_button_size, child_button_size, bfont, bmfont, brfont, header_font, pnbuttonfont, module_font

def micro_loader(parent):
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
    
    label = ctk.CTkLabel(header_frame, text="◇ Microhap Loading", font=header_font,
                         fg_color="transparent", text_color=COLORS['accent'])
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
    
    loci_var = ctk.StringVar(value=genotype_class.get_parameter().get_locifile())
    ctk.CTkLabel(body_frame.top_panel, text="Loci file:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.loci_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=loci_var,
                                         height=26, corner_radius=8, border_width=2)
    body_frame.top_panel.loci_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    loci_browse_btn = ctk.CTkButton(body_frame.top_panel, text="Browse",font=brfont, height=child_button_size['height'], width=child_button_size['width'],
                  corner_radius=8, fg_color=COLORS['accent'], hover_color=COLORS['secondary'])
    loci_browse_btn.configure(command=lambda btn=loci_browse_btn: infile_browser(body_frame.top_panel.loci_entry, "index", btn))
    loci_browse_btn.grid(row=row, column=1, pady=(1,1), sticky="w")
    def on_loci_change(*args):
        fpath = loci_var.get()
        genotype_class.get_parameter().set_locifile(fpath)
        if fpath and os.path.isfile(fpath):
            genotype_class.get_parameter().set_analtype('snp')
            genotype_class.get_metadata().read_locifile(genotype_class.get_parameter(), genotype_class.get_post_microhap(), True)
    loci_var.trace_add("write", on_loci_change)
    loci_rev_var = ctk.BooleanVar(value=genotype_class.get_parameter().get_revcomloci())
    ctk.CTkCheckBox(body_frame.top_panel, text="reverse complement", variable = loci_rev_var, font =brfont, text_color="white").grid(row=row, column=3, padx=(0, 0),sticky="w")
    loci_rev_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_revcom(loci_rev_var.get()))
    row += 1
    
    body_frame.top_panel.inputdir_var = ctk.StringVar(value=genotype_class.get_parameter().get_cur_microhap_input_file())
    ctk.CTkLabel(body_frame.top_panel, text="Microhap input file:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.in_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=body_frame.top_panel.inputdir_var,
                                         height=26, corner_radius=8, border_width=2)
    body_frame.top_panel.in_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    input_browse_btn = ctk.CTkButton(body_frame.top_panel, text="Browse", font=brfont, height=child_button_size['height'], width=child_button_size['width'],
                  corner_radius=8, fg_color=COLORS['accent'], hover_color=COLORS['secondary'])
    input_browse_btn.configure(command=lambda btn=input_browse_btn: infile_browser(body_frame.top_panel.in_entry, "index", btn))
    input_browse_btn.grid(row=row, column=1, pady=(1,1), sticky="w")
    def on_input_change(*args):
        fpath = body_frame.top_panel.inputdir_var.get()
        genotype_class.get_parameter().set_cur_microhap_input_file(fpath)
        if fpath and os.path.isfile(fpath):
            genotype_class.get_metadata().read_cur_microhap_file(genotype_class.get_parameter())
    body_frame.top_panel.inputdir_var.trace_add("write", on_input_change)
    row+=1
    
    micro_var = ctk.StringVar(value=genotype_class.get_parameter().get_pre_microhap_input_file())
    ctk.CTkLabel(body_frame.top_panel, text="Pre microhap file (optional):", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.microhap_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=micro_var,
                                         height=26, corner_radius=8, border_width=2)
    body_frame.top_panel.microhap_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    micro_browse_btn = ctk.CTkButton(body_frame.top_panel, text="Browse",font=brfont, height=child_button_size['height'], width=child_button_size['width'],
                  corner_radius=8, fg_color=COLORS['accent'], hover_color=COLORS['secondary'])
    micro_browse_btn.configure(command=lambda btn=micro_browse_btn: infile_browser(body_frame.top_panel.microhap_entry, "index", btn))
    micro_browse_btn.grid(row=row, column=1, pady=(1,1), sticky="w")
    def on_micro_change(*args):
        fpath = micro_var.get()
        genotype_class.get_parameter().set_pre_microhap_input_file(fpath)
        genotype_class.get_parameter().set_has_pre_mh(True)
        if fpath and os.path.isfile(fpath):
            genotype_class.get_metadata().read_pre_microhap_file(genotype_class.get_parameter())
    micro_var.trace_add("write", on_micro_change)
    row+=1
    
    output_var = ctk.StringVar(value=genotype_class.get_parameter().get_post_microhap_output_dir())
    ctk.CTkLabel(body_frame.top_panel, text="Output folder:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.out_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=output_var,
                                         height=26, corner_radius=8, border_width=2)
    body_frame.top_panel.out_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    output_browse_btn = ctk.CTkButton(body_frame.top_panel, text="Browse",font=brfont, height=child_button_size['height'], width=child_button_size['width'],
                  corner_radius=8, fg_color=COLORS['accent'], hover_color=COLORS['secondary'])
    output_browse_btn.configure(command=lambda btn=output_browse_btn: outfile_browser(body_frame.top_panel.out_entry, False, btn))
    output_browse_btn.grid(row=row, column=1, pady=(1,1), sticky="w")
    output_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_post_microhap_output_dir(output_var.get()))

     #confirm button
    body_frame.top_panel.confirm_btn = ctk.CTkButton(body_frame.top_panel, text="Confirm",font=("Segoe UI", 16, "bold"), height=parent_button_size['height'], width=parent_button_size['width'],
                  fg_color=COLORS['accent'], hover_color=COLORS['secondary'], corner_radius=10,
                  state="normal")
    body_frame.top_panel.confirm_btn.grid(row=row, column=3, pady=(5,5), padx=(10,10), sticky="w")
    def on_confirm():
        btn = body_frame.top_panel.confirm_btn
        btn.configure(text="Processing...", state="disabled")
        frame.after(100, lambda: confirm_inputfiles(frame, genotype_class, btn))
    body_frame.top_panel.confirm_btn.configure(command=on_confirm)

    return body_frame

def confirm_inputfiles(frame, genotype_class, confirm_btn):
    parent_win = frame.winfo_toplevel()
    if genotype_class.get_parameter().get_locifile() is None or not os.path.isfile(genotype_class.get_parameter().get_locifile()):
        modern_messagebox.showerror(parent_win, "Error", "Loci file is missing or corrupted.")
        confirm_btn.configure(text="Confirm", state="normal")
        return
    if genotype_class.get_parameter().get_cur_microhap_input_file() is None or not os.path.isfile(genotype_class.get_parameter().get_cur_microhap_input_file()):
        modern_messagebox.showerror(parent_win, "Error", "Microhap input file is missing or corrupted.")
        confirm_btn.configure(text="Confirm", state="normal")
        return
    if genotype_class.get_parameter().get_post_microhap_output_dir() is None or not os.path.isdir(genotype_class.get_parameter().get_post_microhap_output_dir()):
        modern_messagebox.showerror(parent_win, "Error", "Output folder is missing or corrupted.")
        confirm_btn.configure(text="Confirm", state="normal")
        return
    go = False
    try:
        genotype_class.get_post_microhap().populate_pre_post_microhap_dict(genotype_class.get_parameter(), genotype_class.get_metadata())
        genotype_class.get_post_microhap().populate_microhap_dict(genotype_class.get_parameter(), genotype_class.get_metadata())
        go =  genotype_class.get_post_microhap().populate_final_mar_mh_df_dict(genotype_class.get_parameter(), genotype_class.get_metadata())
        genotype_class.get_post_microhap().perform_seq_alignment(genotype_class.get_parameter())
        #genotype_class.get_post_microhap().extract_variants(genotype_class.get_parameter())
        #genotype_class.get_post_microhap().print()
    finally:
        confirm_btn.configure(text="Confirm", state="normal")
    if go:
        update_widget_state(frame, 'normal')
    else:
        update_widget_state(frame, 'disabled')
        modern_messagebox.showerror(parent_win, "Error", "One or more input files are missing or corrupted.")
        return

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
                                    fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                                    corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                    command = lambda:parent.master.show_page("genotype"))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")

    # Next Button
    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next →", font=pnbuttonfont,
                                fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                                corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                state="disabled", command = lambda:on_click_next_button(parent, footer_frame))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), sticky="w")
    return footer_frame
def on_click_next_button(parent, footer_frame):
    if footer_frame.next_button.cget('state') == 'normal':
        # param_frame = parent.master.pages.get("parameters", None)
        # if param_frame is not None:
        #     param_frame.footer_frame.next_button.configure(state='normal')
        update_combox_from_others(parent)
        parent.master.show_page("microtype_results")