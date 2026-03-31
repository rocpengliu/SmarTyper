from scripts.utils import modern_messagebox
from ..utils.common import parent_button_size, child_button_size, bfont, bmbfont,bmfont, brfont, header_font, confirm_button_font, pnbuttonfont
from ..utils.colors import COLORS
import customtkinter as ctk
import tkinter as tk
import os, datetime
import threading, queue
import traceback

def results_summary(parent):
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
    
    label = ctk.CTkLabel(header_frame, text="◙ Result Output", font=header_font,
                         fg_color="transparent", text_color=COLORS['primary'])
    label.pack(side=tk.LEFT, pady=(15, 15), padx=(30, 10))
    return header_frame

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="transparent")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(10,10), padx=(15, 15), sticky="ew")
    
    # Configure footer_frame to center its content
    footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)
    
    # Previous Button
    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="← Previous", font=pnbuttonfont,
                                    fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                    corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                    command = lambda:parent.master.show_page("results"))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")
    
    # Next Button
    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Microtype →", font=pnbuttonfont,
                                fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                state="disabled", command = lambda: go_button(parent))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), sticky="w")
    
    return footer_frame

def create_body(parent, frame):
    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(2,2))
    
    body_frame.grid_rowconfigure(0, weight=1) #top panel
    body_frame.grid_rowconfigure(1, weight=6) # bottom panel
    body_frame.grid_rowconfigure(2, weight=1) # 
    body_frame.grid_columnconfigure(0, weight=1) # top and bottom panels
    body_frame.grid_columnconfigure(1, weight=1) # top and bottom panels
    
    body_frame.top_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    body_frame.top_panel.grid(row=0, column=0, sticky="nsw", padx=body_frame.padx, pady=(0,0))
    #top_panel.grid_propagate(False)
    body_frame.top_panel.grid_columnconfigure(0, weight=1) #right panel
    body_frame.top_panel.grid_rowconfigure('all', weight=1)
    body_frame.log_queue = queue.Queue()
    body_frame.res_queue = queue.Queue()
    poll_log_text(body_frame)

    row = 0
    ctk.CTkLabel(body_frame.top_panel, 
                 text="This is to output all tables and figures to local storage! Please be patient, do not close the program.", 
                 font=bfont, 
                 text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(10,10), sticky="e")
    row += 1
    body_frame.bottom_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    body_frame.bottom_panel.grid(row=row, column=0, columnspan=1, sticky="nsew", padx=body_frame.padx, pady=(0,0))
    body_frame.bottom_panel.grid_columnconfigure(0, weight=1)
    body_frame.bottom_panel.grid_rowconfigure(0, weight=1)
    
    body_frame.log_text = ctk.CTkTextbox(
        body_frame.bottom_panel,
        wrap="word",
        font=bmfont,
        state="disabled",
        text_color="white",
        fg_color=COLORS['background'],
        border_color="white", border_width=3, corner_radius=8
    )
    body_frame.log_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
    
    return body_frame

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
    body_frame.after(100, lambda: poll_log_text(body_frame))

def run_thread(parent):
    threading.Thread(target = lambda:run_pool(parent), daemon=True).start()
    cur_frame = parent.master.pages.get('summary', None)
    cur_frame.after(100, lambda: check_res_run(cur_frame))

def run_pool(parent):
    try:
        genoclass = parent.master.genotype_class
        summary_frame = parent.master.pages.get('summary', None)
        if summary_frame is None:
            print(f'Error: summary page is not available')
            return
        run_frame = summary_frame.body_frame
        if run_frame is None:
            print(f'Error, summary frame is not available')
            return
        def log_msg(msg):
            run_frame.log_queue.put(msg)
        log_msg(f'This process is very memory intensive, it may take a while to finish. Please be patient and do not close the program.\n\n')
        log_msg(f"-------------------------------start step 1-----------------------------")
        log_msg(f"starting to dump genotyping project!")
        log_msg(f"This is slow, please be patient!")
        genoclass.dump_session("genotype") #must dump session first because generate_all may crash due to high memory usage
        log_msg(f"finished to dump genotyping project!")
        log_msg(f"-------------------------------end step 1-------------------------------\n\n")
        log_msg(f"-------------------------------start step 2-----------------------------")
        log_msg(f"starting to output all files!")
        go = genoclass.generate_all(log_func = log_msg)
        if go:
            log_msg(f"finished to output all files!")
            log_msg(f"-------------------------------end step 2-------------------------------\n\n")
            log_msg(f"Genotyping processing completed successfully. Please click 'Microtype →' for microtype analysis or 'Exit' to close the program.")
            run_frame.res_queue.put(('success', go))
        else:
            log_msg(f"Genotyping processing failed. Please check the log for details.")
            run_frame.res_queue.put(("Genotyping processing failed. Please check the log for details.", go))
    except Exception as e:
        traceback.print_exc()
        log_msg(f"Error during microhap processing: {e}")
        run_frame.res_queue.put((str(e), False))

def check_res_run(cur_frame):
    try:
        status, result = cur_frame.body_frame.res_queue.get_nowait()
        if status == 'success' and result:
            cur_frame.footer_frame.next_button.configure(state="normal")
            modern_messagebox.showsuccess(cur_frame.body_frame.winfo_toplevel(), "Success", "Please click 'Microtype →' for microtype analysis or 'Exit'.")
        else:
            cur_frame.footer_frame.next_button.configure(state="disabled")
            modern_messagebox.showerror(cur_frame.body_frame.winfo_toplevel(), "Error", f"Genotyping processing failed: {result}")
    except queue.Empty:
        cur_frame.body_frame.after(200, lambda: check_res_run(cur_frame))
        return   
def go_button(parent):
    genoclass = parent.master.genotype_class
    panel = parent.master.pages.get('microtype_data', None)
    if panel is not None:
        panel.body_frame.top_panel.loci_entry.delete(0, 'end')
        panel.body_frame.top_panel.loci_entry.insert(0, genoclass.get_parameter().get_locifile())
        genoclass.get_metadata().read_locifile2(genoclass.get_parameter(), genoclass.get_post_microhap(), True)
        if genoclass.get_parameter().get_outputdir() and os.path.isdir(genoclass.get_parameter().get_outputdir()):
            fpath = os.path.join(genoclass.get_parameter().get_outputdir(), 'All_sample_final_haplotype.txt')
            if os.path.isfile(fpath):
                genoclass.get_parameter().set_cur_microhap_input_file(fpath)
                panel.body_frame.top_panel.in_entry.delete(0, 'end')
                panel.body_frame.top_panel.in_entry.insert(0, fpath)
                genoclass.get_metadata().read_cur_microhap_file(genoclass.get_parameter())
        
    parent.master.toggle_menu("genotype", all=True)  # Fold all menus first
    parent.master.toggle_menu("microtype")           # Unfold microtype menu
    parent.master.button_clicked("microtype_data", "microtype")
    parent.master.show_page("microtype_data")