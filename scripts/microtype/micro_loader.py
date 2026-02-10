import traceback
import customtkinter as ctk
import tkinter as tk
import threading, queue, datetime
from ..utils.utils_common import *
from .micro_viewer import update_combox_from_others_micro
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
    
    label = ctk.CTkLabel(header_frame, text="◇ Microtype Loading", font=header_font,
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
    body_frame.grid_rowconfigure(2, weight=1) # 
    body_frame.grid_columnconfigure(0, weight=1) # top and bottom panels
    body_frame.grid_columnconfigure(1, weight=1) # top and bottom panels
    
    body_frame.top_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    body_frame.top_panel.grid(row=0, column=0, sticky="nsw", padx=(100,20), pady=(10,10))
    body_frame.top_panel.grid_columnconfigure(0, weight=1) #right panel
    body_frame.top_panel.grid_rowconfigure('all', weight=1)
    
    body_frame.result_queue = queue.Queue()
    body_frame.log_queue = queue.Queue()
    poll_log_text(body_frame)
    
    row = 0
    
    n_thread_var = tk.StringVar(value=str(genotype_class.get_parameter().get_thread()))
    ctk.CTkLabel(body_frame.top_panel, text="Num. thread:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.n_thread = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=n_thread_var, height=26)
    body_frame.top_panel.n_thread.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    n_thread_var.trace_add("write", lambda *args: (
        genotype_class.get_parameter().set_thread(
            int(n_thread_var.get()) if n_thread_var.get().isdigit() else genotype_class.get_parameter().get_thread()
        )
    ))
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
    loci_var.trace_add("write", lambda *args: (
        genotype_class.get_parameter().set_locifile(loci_var.get()),
        genotype_class.get_parameter().set_analtype('snp'),
        genotype_class.get_metadata().read_locifile(genotype_class.get_parameter(), genotype_class.get_post_microhap(), True)
    ))
    loci_rev_var = ctk.BooleanVar(value=genotype_class.get_parameter().get_revcomloci())
    ctk.CTkCheckBox(body_frame.top_panel, text="reverse complement", variable = loci_rev_var, font =brfont, text_color="white").grid(row=row, column=3, padx=(0, 0),sticky="w")
    loci_rev_var.trace_add("write", lambda *args: genotype_class.get_parameter().set_revcom(loci_rev_var.get()))
    row += 1
    
    inputdir_var = ctk.StringVar(value=genotype_class.get_parameter().get_cur_microhap_input_file())
    ctk.CTkLabel(body_frame.top_panel, text="Microtype input file:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,1), sticky="e")
    body_frame.top_panel.in_entry = ctk.CTkEntry(body_frame.top_panel, width=250, textvariable=inputdir_var,
                                         height=26, corner_radius=8, border_width=2)
    body_frame.top_panel.in_entry.grid(row=row, column=2, padx=body_frame.padx, pady=(1,1), sticky="w")
    input_browse_btn = ctk.CTkButton(body_frame.top_panel, text="Browse", font=brfont, height=child_button_size['height'], width=child_button_size['width'],
                  corner_radius=8, fg_color=COLORS['accent'], hover_color=COLORS['secondary'])
    input_browse_btn.configure(command=lambda btn=input_browse_btn: infile_browser(body_frame.top_panel.in_entry, "index", btn))
    input_browse_btn.grid(row=row, column=1, pady=(1,1), sticky="w")
    inputdir_var.trace_add("write", lambda *args: (
        genotype_class.get_parameter().set_cur_microhap_input_file(inputdir_var.get()),
        genotype_class.get_metadata().read_cur_microhap_file(genotype_class.get_parameter())
    ))
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
    micro_var.trace_add("write", lambda *args: (
        genotype_class.get_parameter().set_pre_microhap_input_file(micro_var.get()),
        genotype_class.get_parameter().set_has_pre_mh(True),
        genotype_class.get_metadata().read_pre_microhap_file(genotype_class.get_parameter())
    ))
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
    body_frame.top_panel.confirm_btn.configure(
        command=lambda: [
            body_frame.top_panel.confirm_btn.configure(state="disabled"),
            frame.after(100, lambda: confirm_inputfiles(frame, body_frame, genotype_class, body_frame.top_panel.confirm_btn))
        ]
    )
        # Create bottom panel for log_text
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

def confirm_inputfiles(frame, body_frame, genotype_class, confirm_btn):
    threading.Thread(
        target = run_pool,
        args=(genotype_class, body_frame),
        daemon=True
    ).start()
    frame.after(200, lambda: check_populate_result(frame, body_frame, genotype_class, confirm_btn))

def run_pool(genotype_class, body_frame):
    try:
        def log_msg(msg):
            body_frame.log_queue.put(msg)
        log_msg("Starting microhap processing. This could be slow and please be patient.....\n\n")
        log_msg("----------------------------------start step 1---------------------------------------")
        go0 = genotype_class.get_post_microhap().populate_pre_post_microhap_dict(genotype_class.get_parameter(), genotype_class.get_metadata(), log_func = log_msg)
        log_msg("-----------------------------------end  step 1----------------------------------------\n\n")
        log_msg("----------------------------------start step 2---------------------------------------")
        go1 = genotype_class.get_post_microhap().populate_microhap_dict(genotype_class.get_parameter(), genotype_class.get_metadata(), log_func = log_msg)
        log_msg("-----------------------------------end step 2----------------------------------------\n\n")
        log_msg("----------------------------------start step 3---------------------------------------")
        go2 = genotype_class.get_post_microhap().populate_final_mar_mh_df_dict( genotype_class.get_parameter(), genotype_class.get_metadata(), log_func = log_msg)
        log_msg("-----------------------------------end step 3----------------------------------------\n\n")
        log_msg("----------------------------------start step 4---------------------------------------")
        go3 = genotype_class.generate_all_mar_microhaps_fig(log_func = log_msg)
        log_msg("-----------------------------------end step 4----------------------------------------\n\n")
        log_msg("----------------------------------start step 5---------------------------------------")
        go4 = genotype_class.generate_all_sam_microhaps_fig(log_func = log_msg)
        log_msg("-----------------------------------end step 5----------------------------------------\n\n")
        log_msg("----------------------------------start step 6---------------------------------------")
        go5 = genotype_class.get_post_microhap().perform_seq_alignment(genotype_class.get_parameter(), log_func = log_msg)
        log_msg("-----------------------------------end step 6----------------------------------------\n\n")
        log_msg("----------------------------------start step 7---------------------------------------")
        go6 = genotype_class.dump_session("microtype", log_func = log_msg)
        log_msg("-----------------------------------end step 7----------------------------------------\n\n")
        go7 = go0 and go1 and go2 and go3 and go4 and go5 and go6
        body_frame.result_queue.put(('success', go7))
        if go7:
            log_msg("Microhap processing completed successfully. Please click 'Next' to proceed.")
            modern_messagebox.showinfo(body_frame.winfo_toplevel(), "Success", "Microhap processing completed successfully. Please click 'Next' to proceed.")
        else:
            log_msg("Microhap processing failed. Please check the input files and try again.")
            modern_messagebox.showerror(body_frame.winfo_toplevel(), "Error", "Microhap processing failed. Please check the input files and try again.")
    except Exception as e:
        traceback.print_exc()
        log_msg(f"Error during microhap processing: {e}")
        body_frame.result_queue.put(('error', str(e)))

def check_populate_result(frame, body_frame, genotype_class, confirm_btn):
    try:
        status, result = body_frame.result_queue.get_nowait()
    except queue.Empty:
        frame.after(200, lambda: check_populate_result(frame, body_frame, genotype_class, confirm_btn))
        return
    if status == 'success' and result:
        update_widget_state(frame, 'normal')
    else:
        update_widget_state(frame, 'disabled')
        modern_messagebox.showerror(frame.winfo_toplevel(), "Error", f"Microhap processing failed: {result}")
    confirm_btn.configure(text="Confirm", state="normal")

def poll_log_text(body_frame):
    try:
        while True:
            log_message = body_frame.log_queue.get_nowait()
            body_frame.log_text.configure(state="normal")
            cur_time = datetime.datetime.now().strftime("[%H:%M:%S]: ")
            body_frame.log_text.insert(tk.END, cur_time + log_message + "\n\n")
            body_frame.log_text.see(tk.END)
            body_frame.log_text.configure(state="disabled")
    except queue.Empty:
        pass
    body_frame.after(200, lambda: poll_log_text(body_frame))
    
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
        update_combox_from_others_micro(parent)
        parent.master.show_page("microtype_results")