import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
import queue
from tkinter import messagebox
import seqtyper_core
import time
import datetime
import os
from .results_geno_combo import update_genotype_tab
import pdb
from ..utils.utils_common import print_time, run_update_lock

def job_runner(parent):
    frame = ctk.CTkFrame(parent, fg_color="#3b3b3b")
    frame.grid(row=0, column=0, sticky="nsew")

    # Configure grid weights
    frame.grid_rowconfigure(0, weight=0)  # Header row expand
    frame.grid_rowconfigure(1, weight=1)  # Content row expands
    frame.grid_rowconfigure(2, weight=0)  # Footer row doesn't expand
    frame.grid_columnconfigure(0, weight=1)  # Center content horizontally

    frame.bfont = ("Helvetica", 15, "bold")
    frame.brfont = ("Helvetica", 10, "bold")

    frame.header_frame = create_header(frame)
    frame.body_frame = create_body(parent, frame)
    frame.footer_frame = create_footer(parent, frame)
    return frame

def create_body(parent, frame):
    body_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    body_frame.bfont = ("Helvetica", 15, "bold")
    body_frame.brfont = ("Helvetica", 10, "bold")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, sticky="nsew")

     # Configure the body_frame grid to expand properly
    body_frame.grid_rowconfigure(0, weight=0)  # Timer label row doesn't expand
    #body_frame.grid_rowconfigure(1, weight=0)
    body_frame.grid_rowconfigure(1, weight=0)  # progress bar
    body_frame.grid_rowconfigure(2, weight=1)  # Log text row expands
    body_frame.grid_columnconfigure(0, weight=1)  # Center content horizontally

   
    body_frame.progress_label = ctk.CTkLabel(body_frame, text="0 / 0 samples (0%)", font=frame.bfont, text_color = "yellow", fg_color="transparent")
    body_frame.progress_label.grid(row=0, column=0, padx=(100,10), pady=body_frame.pady, sticky="w")
     # Timer label
    body_frame.timer_label = ctk.CTkLabel(body_frame, text="Elapsed time: 0s", font=frame.bfont, text_color="white")
    body_frame.timer_label.grid(row=0, column=0, padx=(300, 10), pady=body_frame.pady, sticky="w")
    
    body_frame.progress_bar = ttk.Progressbar(body_frame, orient="horizontal", mode="determinate")
    body_frame.progress_bar.grid(row=1, column=0, padx=(100,100), pady=body_frame.pady, sticky="ew")
    body_frame.progress_bar["maximum"] = 100  # Set maximum value
    body_frame.progress_bar["value"] = 0
    
    body_frame.log_text = ctk.CTkTextbox(body_frame, wrap="word", font=("Helvetica", 15), state="normal", text_color="white")
    body_frame.log_text.grid(row=2, column=0, padx=body_frame.padx, pady=body_frame.pady, sticky="nsew")

    return body_frame

def create_header(frame):
    header_frame = ctk.CTkFrame(frame, fg_color="#2b2b2b")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10, 5), padx=(10, 10))
    header_frame.grid_columnconfigure(0, weight=1)  # Center header content
    label = ctk.CTkLabel(header_frame, text="Job monitoring", font=("Helvetica", 30, "bold"),
                         fg_color="#2b2b2b", text_color="green")
    label.pack(side=tk.LEFT, pady=(10, 10), padx=(100, 10))
    return header_frame

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    footer_frame.grid(row=2, column=0, sticky="ew", pady=(10, 10), padx=(10, 10))
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)

    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="Previous", font=("Helvetica", 12, "bold"),
                                    command=lambda: parent.master.show_page("parameters"))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")

    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next", font=("Helvetica", 12, "bold"), state="disabled",
                                command=lambda:on_click_res(parent))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), sticky="w")
    return footer_frame

def on_click_res(parent):
    parent.after(100, lambda:parent.master.show_page("results"))
    panel = parent.master.pages.get('results').body_frame.bottom_panel
    if panel.winfo_exists():
        update_genotype_tab(parent,panel)

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
                            # frame.log_text.configure(state="normal")
                            # frame.log_text.insert("end", time_stamped_msg + "\n")
                            # frame.log_text.configure(state="disabled")
                            # frame.log_text.yview("end")
                            # frame.update_idletasks()  # Process internal Tkinter event queue
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
    frame.log_text.insert("end", str(msg) + "\n")
    frame.log_text.yview("end")
    frame.update_idletasks()  # Process internal Tkinter event queue
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
        s3 = run_frame.cur_sam_idx * 100 / run_frame.tot_sams
        formatted_s3 = f"{s3:.2f}"
        formatted_s3=str(formatted_s3)
        run_frame.progress_bar["value"] = s3
        run_frame.progress_label.configure(text=f"{str(run_frame.cur_sam_idx)}/{str(run_frame.tot_sams)} samples ({formatted_s3}%)")
        run_frame.update_idletasks()
    else:
            #frame.progress_bar.set(100)
        run_frame.progress_bar["value"] = 100
        run_frame.progress_label.configure(text=f"{str(run_frame.tot_sams)}/{str(run_frame.tot_sams)} samples (100%)")

def capture_output(run_frame):
    while True:
        #print_time(f"00000000000000000000000000000000000")
        #run_frame.output_queue.put(f"0000000000000000000000")
        output = str(seqtyper_core.get_seqtyper_output())
        #print_time(f"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ {output} #######################################")
        if output:
            time.sleep(0.05)
            with run_update_lock:
                run_frame.output_queue.put(output)
                #print_time(f"capture_output {output}, ***********************************")
                if run_frame.run_finished.is_set():
                    break
        else:
            if run_frame.run_finished.is_set():
                break

def run_seqtyper(parent):
    threading.Thread(target=lambda: target(parent), daemon=True).start()

def target(parent):
    #pdb.set_trace()
    genoclass = parent.master.genotype_class
    run_frame = parent.master.pages.get("run", None)
    if run_frame is None:
        print("Error: 'run' page is not available.")
        return
    run_frame = run_frame.body_frame
    if run_frame is None:
        print("Error: 'run_frame.body_frame' is not initialized.")
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
        pass
        # subargs['htJetter'] = genoclass.get_parameter().get_htJetter()
        # subargs['hmPerH'] = genoclass.get_parameter().get_hmPerH()
        # subargs['hmPerL'] = genoclass.get_parameter().get_hmPerL()
        # subargs['minSeqsPerSnp'] = genoclass.get_parameter().get_minSeqsPerSnp()
        # subargs['minReads4Filter'] = genoclass.get_parameter().get_minReads4Filter()
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

    print_time("starting to run seq2type")
    run_frame.output_queue = queue.Queue()
    run_frame.run_finished = threading.Event()
    run_frame.start_time = time.time()
    run_frame.cur_sam_idx = 0
    run_frame.tot_sams = len(run_frame.args_dir)
    #capture_thread = threading.Thread(target=capture_output, args=(run_frame), daemon=True)
    run_thread = threading.Thread(target=run_wrapper, args=(parent, run_frame), daemon=True)
    #capture_thread.start()
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
                    run_frame.master.footer_frame.next_button.configure(state='normal')
                    break
    else:
        print("Error: 'run_frame' is not initialized.")

def run_wrapper(parent, run_frame):
    try:
        # freeze_ui(par_frame)
        genoclass = parent.master.genotype_class
        res_frame=parent.master.pages.get('results').footer_frame
        res_frame.next_button.configure(state='disabled')
        with run_update_lock:
            run_frame.output_queue.put("\nStarting SeqTyper!\n")
        #update_progressbar(run_frame)
        for index, (sample, arg_lst) in enumerate(run_frame.args_dir.items()):
            with run_update_lock:
                run_frame.cur_sam_idx = index + 1
                run_frame.output_queue.put(f'Start to process sample: {sample}, {index+1} out of {run_frame.tot_sams} samples\n')
            seqtyper_core.run_seqtyper_wrapper(arg_lst)
            with run_update_lock:
                run_frame.output_queue.put(f'reading sample {sample} outputs\n')
                genoclass.read_sam_outputs(sample)
                run_frame.output_queue.put(f'Finish the processing sample: {sample}, {index+1} out of {run_frame.tot_sams} samples\n')
            #run_frame.after(0, lambda : update_progressbar(run_frame))
            #update_progressbar(run_frame, (index+1), tot_sams, run_finished)
        # unfreeze_ui(par_frame)
        with run_update_lock:
            run_frame.output_queue.put(f'starting to generate all sample figures\n')
        if genoclass.get_parameter().is_pro_figure():
            genoclass.pro_all_sample_figs(run_frame.output_queue)
        with run_update_lock:
            run_frame.output_queue.put("\nCongrats! SeqTyper run completed successfully.\n")
            parent.master.after(0, lambda: messagebox.showinfo("Success", "SeqTyper ran successfully"))
            parent.master.pages.get('results').footer_frame.next_button.configure(state='normal')
            run_frame.run_finished.set()
    except Exception as e:
        emsg = f"Error running SeqTyper: {str(e)}"
        with run_update_lock:
            run_frame.output_queue.put(emsg)
        parent.master.after(0, lambda msg=emsg: messagebox.showerror("Error", msg))
    finally:
        with run_update_lock:
            run_frame.run_finished.set()
        #parent.master.after(0, lambda:update_progressbar(run_frame))
