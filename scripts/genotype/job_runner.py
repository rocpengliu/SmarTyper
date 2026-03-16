import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
import queue
import seqtyper_core
import time
import datetime
import os
from .results_geno_combo import update_genotype_tab
import pdb
from ..utils.utils_common import print_time, run_update_lock
from ..utils.common import parent_button_size, child_button_size, bfont,bmfont,pnbuttonfont, header_font
from ..utils.colors import COLORS
from ..utils import modern_messagebox

def job_runner(parent):
    frame = ctk.CTkFrame(parent, fg_color=COLORS['background'])
    frame.grid(row=0, column=0, sticky="nsew")

    # Configure grid weights
    frame.grid_rowconfigure(0, weight=0)  # Header row expand
    frame.grid_rowconfigure(1, weight=1)  # Content row expands
    frame.grid_rowconfigure(2, weight=0)  # Footer row doesn't expand
    frame.grid_columnconfigure(0, weight=1)  # Center content horizontally

    frame.header_frame = create_header(frame)
    frame.body_frame = create_body(parent, frame)
    frame.footer_frame = create_footer(parent, frame)
    return frame

def create_body(parent, frame):
    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, sticky="nsew")

     # Configure the body_frame grid to expand properly
    body_frame.grid_rowconfigure(0, weight=0)  # Timer label row doesn't expand
    #body_frame.grid_rowconfigure(1, weight=0)
    body_frame.grid_rowconfigure(1, weight=0)  # progress bar
    body_frame.grid_rowconfigure(2, weight=1)  # Log text row expands
    body_frame.grid_columnconfigure(0, weight=1)  # Center content horizontally

    # Create a frame for progress info
    progress_info_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
    progress_info_frame.grid(row=0, column=0, padx=(20,20), pady=(10,5), sticky="ew")
    progress_info_frame.grid_columnconfigure(0, weight=1)
    progress_info_frame.grid_columnconfigure(1, weight=1)
    progress_info_frame.grid_columnconfigure(2, weight=1)
    
    body_frame.progress_label = ctk.CTkLabel(progress_info_frame, text="0 / 0 samples (0%)", 
                                             font=bfont, 
                                             text_color=COLORS['text_primary'])
    body_frame.progress_label.grid(row=0, column=0, padx=(10,15), pady=5, sticky="w")
    
    body_frame.timer_label = ctk.CTkLabel(progress_info_frame, text="Elapsed time: 0s", 
                                          font=bfont, 
                                          text_color=COLORS['secondary'])
    body_frame.timer_label.grid(row=0, column=1, padx=(0,15), pady=5, sticky="w")
    
    # Modern progress bar with CustomTkinter
    body_frame.progress_bar = ctk.CTkProgressBar(body_frame, height=25, corner_radius=10,
                                                 progress_color=COLORS['primary'],
                                                 fg_color=COLORS['card'])
    body_frame.progress_bar.grid(row=1, column=0, padx=(20,20), pady=(5,10), sticky="ew")
    body_frame.progress_bar.set(0)  # Set initial value to 0
    
    body_frame.log_text = ctk.CTkTextbox(body_frame, wrap="word", font=bmfont, state="disabled", 
                                         text_color="white", fg_color=COLORS['background'],
                                        border_color="white", border_width=3, corner_radius=8)
    body_frame.log_text.grid(row=2, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="nsew")

    return body_frame

def create_header(frame):
    header_frame = ctk.CTkFrame(frame, fg_color=COLORS['card'], corner_radius=12)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(15, 10), padx=(15, 15))
    header_frame.grid_columnconfigure(0, weight=1)  # Center header content
    label = ctk.CTkLabel(header_frame, text="► Job Monitoring", font=header_font,
                         fg_color="transparent", text_color=COLORS['primary'])
    label.pack(side=tk.LEFT, pady=(15, 15), padx=(30, 10))
    return header_frame

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="transparent")
    footer_frame.grid(row=2, column=0, sticky="ew", pady=(10, 10), padx=(15, 15))
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)

    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="← Previous", font=pnbuttonfont,
                                        fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                        corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                        command=lambda: parent.master.show_page("parameters"))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")

    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next →", font=pnbuttonfont, state="disabled",
                                    fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                    corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                    command=lambda:on_click_res(parent, footer_frame))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), sticky="w")
    return footer_frame

def on_click_res(parent, footer_frame):
    footer_frame.next_button.configure(state='disabled', text="Loading...")
    footer_frame.next_button.update_idletasks()
    def after_show():
        panel = parent.master.pages.get('results').body_frame.bottom_panel
        if panel.winfo_exists():
            print_time(f"updating genotype tab from job runner")
            update_genotype_tab(parent, panel)
        footer_frame.next_button.configure(state='normal', text="Next →")
        parent.master.show_page("results")
    parent.master.after(100, after_show)

def update_log_text(run_frame):
        if not run_frame.run_finished.is_set() or not run_frame.output_queue.empty():  # Check if there's still work to do
            try:
                # Try to perform an update if there's new data.
                while not run_frame.output_queue.empty():
                    try:
                        message = run_frame.output_queue.get_nowait()
                        if message.strip():
                            cur_time = datetime.datetime.now().strftime("[%H:%M:%S]: ")
                            time_stamped_msg = f"{cur_time}{message}"
                            run_frame.after(0, lambda msg=time_stamped_msg: insert_to_log_text(run_frame, msg))
                    except queue.Empty:
                        break
            except queue.Empty:
                pass  # If we hit this, the queue is empty and we'll wait for next scheduled call.
            finally:
                # Wait for a bit before scheduling the next call.
                #run_frame.after(10, update_log_text, run_frame)
                pass
        else:
            # Cleanup if needed when run is finished, like enabling buttons or other controls.
            # This is a good place to re-enable UI which has been frozen during the long-running task.
            if not run_frame.output_queue.empty():
                while not run_frame.output_queue.empty():
                    run_frame.output_queue.get_nowait()
                run_frame.output_queue.queue.clear()
                del run_frame.output_queue

def insert_to_log_text(frame, msg):
    frame.log_text.configure(state="normal")
    frame.log_text.insert("end", str(msg) + "\n")
    frame.log_text.configure(state="disabled")
    frame.log_text.yview("end")
    frame.update_idletasks()  # Process internal Tkinter event queue
    
    # Real-time append to log file if handle is open
    if hasattr(frame, 'log_file_handle') and frame.log_file_handle:
        try:
            frame.log_file_handle.write(str(msg) + "\n")
            frame.log_file_handle.flush()  # Force write to disk immediately
        except Exception as e:
            print_time(f"Error writing to log file: {str(e)}")
    
def update_timer(run_frame):
    if not run_frame.run_finished.is_set():
        elapsed_time = int(time.time() - run_frame.start_time)
        hours = elapsed_time // 3600
        minutes = (elapsed_time % 3600) // 60
        seconds = elapsed_time % 60
        run_frame.timer_label.configure(text=f"Elapsed time: {hours:02d}h:{minutes:02d}m:{seconds:02d}s")
            #frame.after(1, update_timer, frame, start_time, run_finished)

def update_progressbar(run_frame):
    if not run_frame.run_finished.is_set():
        s3 = (run_frame.cur_sam_idx - 1) * 100 / run_frame.tot_sams
        formatted_s3 = f"{s3:.2f}"
        formatted_s3=str(formatted_s3)
        run_frame.progress_bar.set(s3 / 100)  # CTkProgressBar uses 0.0 to 1.0
        run_frame.progress_label.configure(text=f"processing {str(run_frame.cur_sam_idx)} out of {str(run_frame.tot_sams)} samples with {str(run_frame.tot_mars)} markers ({formatted_s3}% finished)")
        run_frame.update_idletasks()
    else:
        run_frame.progress_bar.set(1.0)  # CTkProgressBar uses 0.0 to 1.0 (1.0 = 100%)
        run_frame.progress_label.configure(text=f"processing {str(run_frame.tot_sams)} out of {str(run_frame.tot_sams)} samples with {str(run_frame.tot_mars)} markers  (100%)")

def capture_output(run_frame, sample_event):
    while not sample_event.is_set():
        output = str(seqtyper_core.get_seqtyper_output())
        if output:
            time.sleep(0.05)
            with run_update_lock:
                run_frame.output_queue.put(output)
        else:
            time.sleep(0.05)

def run_seqtyper(parent):
    threading.Thread(target=lambda: target(parent), daemon=True).start()

def target(parent):
    #pdb.set_trace()
    genoclass = parent.master.genotype_class
    run_frame = parent.master.pages.get("run", None)
    if run_frame is None:
        print(f"Error: 'run' page is not available.")
        return
    run_frame = run_frame.body_frame
    if run_frame is None:
        print(f"Error: 'run_frame.body_frame' is not initialized.")
        return

    subargs = {}
    subargs['var'] = genoclass.get_parameter().get_analtype()
    subargs["loc"] = genoclass.get_parameter().get_locifile()
    subargs['revCom'] = genoclass.get_parameter().get_revcomloci()
    subargs['minSeqs'] = genoclass.get_parameter().get_minSeqs()
    subargs['maxMismatchesPSeq'] = genoclass.get_parameter().get_maxMismatchesPSeq()
    subargs['thread'] = genoclass.get_parameter().get_thread()
    subargs['average_qual'] = genoclass.get_parameter().get_average_qual()
    subargs['length_required'] = genoclass.get_parameter().get_length_required()
    if genoclass.get_parameter().get_analtype() == "snp":
        # Keep internal parameter names decoupled from CLI flags expected by seqtyper core.
        subargs['ssProH'] = genoclass.get_parameter().get_ssProH()
        subargs['ssProL'] = genoclass.get_parameter().get_ssProL()
        subargs['msProH'] = genoclass.get_parameter().get_msProH()
        subargs['msProL'] = genoclass.get_parameter().get_msProL()
        subargs['sPro3'] = genoclass.get_parameter().get_sPro3()
        subargs['minSeqsProSnp'] = genoclass.get_parameter().get_minSeqsProSnp()
        subargs['minReads4Filter'] = genoclass.get_parameter().get_minReads4Filter()
    else:
        pass

    # Creating the argument list based on the provided arguments
    run_frame.args_dir = {}
    for index, row in genoclass.get_metadata().get_sample_df().iterrows():
        subargs['prefix'] = os.path.join(genoclass.get_parameter().get_outputdir(), row["sample"])
        subargs['in1'] = os.path.join(genoclass.get_parameter().get_inputdir(), row["read1"])
        if 'read2' in genoclass.get_metadata().get_sample_df().columns:
            subargs['in2'] = os.path.join(genoclass.get_parameter().get_inputdir(), row["read2"])
        subargs['verbose'] = True
        args_list = []
        args_list.append("seqtyper")
        for key, value in subargs.items():
            if isinstance(value, bool):
                if value:
                    args_list.append(f'--{key}')
            elif value is not None:
                args_list.append(f'--{key}' if len(key) > 1 else f'-{key[0]}')
                args_list.append(str(value))
        run_frame.args_dir[row["sample"]]=args_list

    print_time(f"starting to run seq2type")
    run_frame.output_queue = queue.Queue()
    run_frame.run_finished = threading.Event()
    run_frame.start_time = time.time()
    run_frame.cur_sam_idx = 0
    run_frame.tot_sams = len(run_frame.args_dir)
    run_frame.tot_mars = len(genoclass.get_metadata().get_ref_markers_list())
    
    # Set up real-time log file path
    output_dir = genoclass.get_parameter().get_outputdir()
    run_frame.log_file_path = os.path.join(output_dir, "smartyper_log.txt")
    # Open log file handle for real-time writing
    try:
        run_frame.log_file_handle = open(run_frame.log_file_path, 'w', encoding='utf-8', buffering=1)  # Line buffered
    except Exception as e:
        print_time(f"Error creating log file: {str(e)}")
        run_frame.log_file_handle = None
    
    run_thread = threading.Thread(target=run_wrapper, args=(parent, run_frame), daemon=True)
    run_thread.start()

    # Ensure that run_frame is set correctly
    if run_frame is not None:
        while True:
            time.sleep(0.05)
            with run_update_lock:
                update_timer(run_frame)
                update_log_text(run_frame)
                update_progressbar(run_frame)
                if run_frame.run_finished.is_set():
                    # Close log file handle when finished
                    if hasattr(run_frame, 'log_file_handle') and run_frame.log_file_handle:
                        try:
                            run_frame.log_file_handle.close()
                        except:
                            pass
                    run_frame.master.footer_frame.next_button.configure(state='normal')
                    break
    else:
        print(f"Error: 'run_frame' is not initialized.")

def run_wrapper(parent, run_frame):
    try:
        genoclass = parent.master.genotype_class
        res_frame = parent.master.pages.get('results').footer_frame
        res_frame.next_button.configure(state='disabled')
        with run_update_lock:
            run_frame.output_queue.put(f"Starting Seq2Type for genotyping!\n\n")
        for index, (sample, arg_lst) in enumerate(run_frame.args_dir.items()):
            with run_update_lock:
                run_frame.cur_sam_idx = index + 1
                run_frame.output_queue.put(f'---------------------------------------------------------start index: {index+1}--------------------------------------------------' + '\n')
                run_frame.output_queue.put(f'Start to process sample: {sample}, {index+1} out of {run_frame.tot_sams} samples\n')
                run_frame.output_queue.put(f'Running Seq2Type for sample: {sample}, this is slow and please be patient!\n')

            # Per-sample event for capture thread
            sample_event = threading.Event()
            capture_thread = threading.Thread(target=capture_output, args=(run_frame, sample_event), daemon=True)
            capture_thread.start()

            seqtyper_core.run_seqtyper_wrapper(arg_lst)

            # Signal capture thread to stop and wait for it
            sample_event.set()
            capture_thread.join()

            with run_update_lock:
                run_frame.output_queue.put(f'reading sample {sample} outputs\n')
                genoclass.read_sam_outputs(sample, run_frame)
                run_frame.output_queue.put(f'Finish the processing sample: {sample}, {index+1} out of {run_frame.tot_sams} samples\n')
                run_frame.output_queue.put(f'---------------------------------------------------------end index: {index+1}----------------------------------------------------' + '\n\n\n')
        with run_update_lock:
            run_frame.output_queue.put(f'starting to generate all sample figures\n')
        if genoclass.get_parameter().is_pro_figure():
            genoclass.pro_all_sample_figs(run_frame.output_queue)
        
        with run_update_lock:
            run_frame.output_queue.put(f"Log file saved to: {run_frame.log_file_path}\n")
            run_frame.output_queue.put("Congrats! Seq2Type ran successfully! Please click 'Next' to proceed.\n")
            parent.master.after(0, lambda: modern_messagebox.showsuccess(run_frame, "Success", "Seq2Type ran successfully"))
            parent.master.pages.get('results').footer_frame.next_button.configure(state='normal')
            run_frame.run_finished.set()
    except Exception as e:
        emsg = f"Error running Seq2Type: {str(e)}"
        with run_update_lock:
            run_frame.output_queue.put(emsg)
        parent.master.after(0, lambda msg=emsg: modern_messagebox.showerror(run_frame, "Error", msg))
    finally:
        # Don't close file here - let main thread close it after processing all messages
        with run_update_lock:
            run_frame.run_finished.set()
