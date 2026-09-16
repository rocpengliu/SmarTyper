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
from ..utils.utils_common import print_time
from ..utils.app_logger import log_action, log_parameters, log_run_summary
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
                                          font=bfont, text_color=COLORS['secondary'])
    body_frame.timer_label.grid(row=0, column=1, padx=(0,15), pady=5, sticky="w")
    
    body_frame.remain_time_label = ctk.CTkLabel(progress_info_frame, text="Estimated remaining time: 0s", 
                                               font=bfont, text_color=COLORS['danger'])
    body_frame.remain_time_label.grid(row=0, column=2, padx=(0,10), pady=5, sticky="w")
    
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
    while True:
        try:
            message = run_frame.output_queue.get_nowait()
        except queue.Empty:
            break

        if message.strip():
            cur_time = datetime.datetime.now().strftime("[%H:%M:%S]: ")
            time_stamped_msg = f"{cur_time}{message}"
            insert_to_log_text(run_frame, time_stamped_msg)
            log_action(message)

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

def format_duration(seconds):
    seconds = max(0, int(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
    
def update_timer(run_frame):
    if not run_frame.run_finished.is_set():
        elapsed_time = time.time() - run_frame.start_time
        run_frame.timer_label.configure(text=f"Elapsed time: {format_duration(elapsed_time)}")
        finished_samples = run_frame.last_finished_sample_idx
        if finished_samples > 0:
            if finished_samples >= run_frame.tot_sams:
                run_frame.remain_time_label.configure(text=f"Estimated remaining time: waiting for finalizing...")
            else:
                sample_durations = getattr(run_frame, 'sample_durations', [])
                if sample_durations:
                    average_sample_time = sum(sample_durations) / len(sample_durations)
                else:
                    average_sample_time = elapsed_time / finished_samples
                current_sample_elapsed = max(0, time.time() - getattr(run_frame, 'current_sample_start_time', time.time()))
                current_sample_remaining = max(0, average_sample_time - current_sample_elapsed)
                not_started_samples = max(0, run_frame.tot_sams - run_frame.cur_sam_idx)
                remaining_time = current_sample_remaining + (average_sample_time * not_started_samples)
                run_frame.remain_time_label.configure(text=f"Estimated remaining time: {format_duration(remaining_time)}")
        else:
            run_frame.remain_time_label.configure(text=f"Estimated remaining time: calculating...")
    else:
        run_frame.remain_time_label.configure(text=f"Estimated remaining time: 0s")

def update_progressbar(run_frame):
    if run_frame.tot_sams <= 0:
        run_frame.progress_bar.set(1.0)
        run_frame.progress_label.configure(text="processing 0 out of 0 samples with 0 loci (100%)")
        run_frame.update_idletasks()
        return

    if not run_frame.run_finished.is_set():
        s3 = (run_frame.cur_sam_idx - 1) * 100 / run_frame.tot_sams
        formatted_s3 = f"{s3:.2f}"
        formatted_s3=str(formatted_s3)
        run_frame.progress_bar.set(s3 / 100)  # CTkProgressBar uses 0.0 to 1.0
        run_frame.progress_label.configure(text=f"processing {str(run_frame.cur_sam_idx)} out of {str(run_frame.tot_sams)} samples with {str(run_frame.tot_mars)} loci ({formatted_s3}% finished)")
        run_frame.update_idletasks()
    else:
        run_frame.progress_bar.set(1.0)  # CTkProgressBar uses 0.0 to 1.0 (1.0 = 100%)
        run_frame.progress_label.configure(text=f"processing {str(run_frame.tot_sams)} out of {str(run_frame.tot_sams)} samples with {str(run_frame.tot_mars)} loci  (100%)")

def drain_seqtyper_output(run_frame):
    while True:
        output = str(seqtyper_core.get_seqtyper_output())
        if not output:
            break
        run_frame.output_queue.put(output)

def capture_output(run_frame, sample_event):
    while not sample_event.is_set():
        output = str(seqtyper_core.get_seqtyper_output())
        if output:
            time.sleep(0.05)
            run_frame.output_queue.put(output)
        else:
            time.sleep(0.05)

def run_seqtyper(parent):
    target(parent)

def poll_run_status(parent, run_frame):
    update_timer(run_frame)
    update_log_text(run_frame)
    update_progressbar(run_frame)

    if run_frame.run_finished.is_set() and run_frame.output_queue.empty():
        if hasattr(run_frame, 'log_file_handle') and run_frame.log_file_handle:
            try:
                run_frame.log_file_handle.close()
            except Exception as e:
                print_time(f"Error closing log file: {str(e)}")
            finally:
                run_frame.log_file_handle = None

        run_frame.master.footer_frame.next_button.configure(state='normal')
        result_footer = parent.master.pages.get('results').footer_frame
        if getattr(run_frame, 'run_error_message', None):
            modern_messagebox.showerror(run_frame, "Error", run_frame.run_error_message)
        elif getattr(run_frame, 'run_success_message', None):
            modern_messagebox.showsuccess(run_frame, "Success", run_frame.run_success_message)
            result_footer.next_button.configure(state='normal')
        return

    run_frame.after(200, poll_run_status, parent, run_frame)

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
    subargs['minReads4Locus'] = genoclass.get_parameter().get_minReads4Locus()
    subargs['maxMismatchesPSeq'] = genoclass.get_parameter().get_maxMismatchesPSeq()
    subargs['thread'] = genoclass.get_parameter().get_thread()
    subargs['average_qual'] = genoclass.get_parameter().get_average_qual()
    subargs['length_required'] = genoclass.get_parameter().get_length_required()
    subargs['nanopore_default'] = genoclass.get_parameter().get_nanopore_default()
    if genoclass.get_parameter().get_sex_analysis():
        subargs['sex'] = genoclass.get_parameter().get_sexfile()
        subargs['maxMismatchesSexPSeq'] = genoclass.get_parameter().get_maxMismatchesPSeqSex()
        subargs['maxMismatchesSexRefSeq'] = genoclass.get_parameter().get_maxMismatchesRefSeqSex()
        subargs['yxRatio'] = genoclass.get_parameter().get_yxRatio()
        subargs['minReadsSexAllele'] = genoclass.get_parameter().get_minReadsSexAllele()
        subargs['minReadsSexVariant'] = genoclass.get_parameter().get_minReadsSexVariant()
    if genoclass.get_parameter().get_analtype() == "snp":
        # Keep internal parameter names decoupled from CLI flags expected by seqtyper core.
        subargs['smProp1H'] = genoclass.get_parameter().get_smProp1H()
        subargs['smProp1L'] = genoclass.get_parameter().get_smProp1L()
        subargs['mmProp1H'] = genoclass.get_parameter().get_mmProp1H()
        subargs['mmProp1L'] = genoclass.get_parameter().get_mmProp1L()
        subargs['mProp2'] = genoclass.get_parameter().get_mProp2()
        #subargs['sProp3'] = genoclass.get_parameter().get_sProp3()
        subargs['minReads4Allele'] = genoclass.get_parameter().get_minReads4Allele()
        subargs['maxRVs4Align'] = genoclass.get_parameter().get_maxRVs4Align()
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

    log_parameters(genoclass.get_parameter(), context="seq2type run")
    for sample, args_list in run_frame.args_dir.items():
        log_action(f"seqtyper command for sample {sample}: {' '.join(args_list)}")

    print_time(f"starting to run seq2type")
    run_frame.output_queue = queue.Queue()
    run_frame.run_finished = threading.Event()
    run_frame.start_time = time.time()
    run_frame.cur_sam_idx = 0
    run_frame.last_finished_sample_idx = 0
    run_frame.current_sample_start_time = None
    run_frame.sample_durations = []
    run_frame.tot_sams = len(run_frame.args_dir)
    run_frame.tot_mars = len(genoclass.get_metadata().get_ref_markers_list())
    run_frame.run_error_message = None
    run_frame.run_success_message = None
    
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
    poll_run_status(parent, run_frame)

def run_wrapper(parent, run_frame):
    try:
        genoclass = parent.master.genotype_class
        run_frame.output_queue.put(f"Starting Seq2Type for genotyping!\n\n")
        for index, (sample, arg_lst) in enumerate(run_frame.args_dir.items()):
            drain_seqtyper_output(run_frame)
            run_frame.cur_sam_idx = index + 1
            run_frame.current_sample_start_time = time.time()
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
            drain_seqtyper_output(run_frame)

            run_frame.output_queue.put(f'reading sample {sample} outputs\n')
            genoclass.read_sam_outputs(sample, run_frame)
            run_frame.output_queue.put(f'Finish the processing sample: {sample}, {index+1} out of {run_frame.tot_sams} samples\n')
            run_frame.output_queue.put(f'---------------------------------------------------------end index: {index+1}----------------------------------------------------' + '\n\n\n')
            
            run_frame.last_finished_sample_idx = run_frame.cur_sam_idx
            sample_duration = time.time() - run_frame.current_sample_start_time
            run_frame.sample_durations.append(sample_duration)
        run_frame.output_queue.put(f'starting to generate all sample figures\n')
        if genoclass.get_parameter().is_pro_figure():
            genoclass.pro_all_sample_figs(run_frame.output_queue)
        
        run_frame.output_queue.put(f"Log file saved to: {run_frame.log_file_path}\n")
        run_frame.output_queue.put("Congrats! Seq2Type ran successfully! Please click 'Next' to proceed.\n")
        log_run_summary(run_frame.start_time, context="seq2type run")
        run_frame.run_success_message = "Seq2Type ran successfully"
        run_frame.run_finished.set()
    except Exception as e:
        emsg = f"Error running Seq2Type: {str(e)}"
        run_frame.output_queue.put(emsg)
        run_frame.run_error_message = emsg
    finally:
        # Don't close file here - let main thread close it after processing all messages
        run_frame.run_finished.set()
