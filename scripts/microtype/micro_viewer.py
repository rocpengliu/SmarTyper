import customtkinter as ctk
import tkinter as tk
import matplotlib
import os
from .micro_dna_align import display_dna_seq_align
from .micro_aa_align import display_aa_seq_align
from .micro_table_fig import update_com_tab, update_sim_tab
from .micro_all_table_fig import display_all_mh_com_table, display_all_mh_sim_table
from .micro_tree import display_phylotre
from ..utils.common import child_button_size

matplotlib.use("Agg")

def micro_viewer(parent):
    frame = ctk.CTkFrame(parent, fg_color="#3b3b3b")
    frame.grid(row=0, column=0, sticky="nsew")

    # Configure grid rows and columns
    frame.grid_rowconfigure(0, weight=0)  # Header row does not expand
    frame.grid_rowconfigure(1, weight=1)  # Body row expands
    frame.grid_rowconfigure(2, weight=0)  # Footer row does not expand
    frame.grid_columnconfigure(0, weight=1)  # Center content horizontally
    #frame.grid_columnconfigure(1, weight=1)#can not set this, will cause huge problem

    create_header(frame)
    frame.body_frame = create_body(parent, frame)
    frame.footer_frame=create_footer(parent, frame)
    return frame

def create_header(frame):
    header_frame = ctk.CTkFrame(frame, fg_color="#2b2b2b")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10, 5), padx=(10, 10))
    header_frame.grid_columnconfigure(0, weight=1)  # Center header content
    label = ctk.CTkLabel(header_frame, text="Microtype Viewing", font=("Helvetica", 30, "bold"),
                         fg_color="#2b2b2b", text_color="green")
    label.pack(side=tk.LEFT, pady=(10, 10), padx=(100, 10))
    return header_frame

def create_body(parent, frame):
    body_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    body_frame.bfont = ("Helvetica", 15, "bold")
    body_frame.brfont = ("Helvetica", 10, "bold")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, sticky="nsew")

    body_frame.grid_rowconfigure(0, weight=0)  # Top panel
    body_frame.grid_rowconfigure(1, weight=1)  # Bottom panel
    body_frame.grid_columnconfigure(0, weight=1)  # Center columns
    #body_frame.grid_rowconfigure('all', weight=1)

    body_frame.top_panel = create_top_panel(parent, body_frame)
    body_frame.bottom_panel = create_bottom_panel(parent, body_frame)
    return body_frame

def create_top_panel(parent, body_frame):
    genoclass = parent.master.genotype_class
    #top_panel = ctk.CTkFrame(body_frame, width=200, height = 50, fg_color="#3b3b3b")
    top_panel = ctk.CTkFrame(body_frame, fg_color="#3b3b3b")
    top_panel.grid(row=0, column=0, sticky="ew", padx=body_frame.padx, pady=body_frame.pady)
    
    top_panel.grid_rowconfigure(0, weight=0)  # Ensure the top row does not expand vertically
    top_panel.grid_rowconfigure(1, weight=0)  # Ensure the top row does not expand vertically
    #top_panel.grid_rowconfigure(2, weight=0)  # Ensure the top row does not expand vertically
    top_panel.grid_columnconfigure('all', weight=0)  # Adjust if needed

    row = 0
    ctk.CTkLabel(top_panel, text="Marker:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,3), sticky="e")

    top_panel.options = []
    selected_option = tk.StringVar(value="")
    top_panel.combobox = ctk.CTkComboBox(top_panel, values=top_panel.options, variable=selected_option, font=body_frame.brfont)
    top_panel.combobox.grid(row=row, column=1, padx=(25, 10), pady=(3,3), sticky="w")
    selected_option.trace_add("write", lambda *args: (genoclass.get_post_microhap().set_selected_marker(selected_option.get()),
                                                      create_microhap_align_panel(body_frame.bottom_panel, genoclass)))
    row += 1
    ctk.CTkButton(top_panel, text="microtype alignment", font=("Helvetica", 12, "bold"),
                width=child_button_size['width'], height=child_button_size['height'],
                command=lambda:create_microhap_align_panel(body_frame.bottom_panel, genoclass)).grid(row=row, column=0, padx=(20,5), pady=(15,1), sticky='w')
    
    ctk.CTkButton(top_panel, text="microtype table", font=("Helvetica", 12, "bold"),
                width=child_button_size['width'], height=child_button_size['height'],
                command=lambda:create_microhap_fig_tbl_panel(body_frame.bottom_panel, genoclass)).grid(row=row, column=1, padx=(20,5), pady=(15,1), sticky='w')
    
    ctk.CTkButton(top_panel, text="microtype table (all)", font=("Helvetica", 12, "bold"),
                width=child_button_size['width'], height=child_button_size['height'],
                command=lambda:create_all_microhap_fig_tbl_panel(body_frame.bottom_panel, genoclass)).grid(row=row, column=2, padx=(20,5), pady=(15,1), sticky='w')
    
    return top_panel

def update_combox(genoclass, top_panel, type):
    """Update the options in the ComboBox based on the type."""
    top_panel.options = list(genoclass.get_post_microhap().get_working_markers_set())
    top_panel.combobox.configure(values=top_panel.options)
    top_panel.combobox.set(top_panel.options[0] if top_panel.options else "")  # Set the default value

def update_combox_from_others(parent):
    """Update the ComboBox options from other components."""
    try:
        genoclass = parent.master.genotype_class
        res_frame = parent.master.pages.get('micro_res', None)

        if res_frame is None:
            print("Error: 'micro_res' page is not available.")
            return
        top_panel = res_frame.body_frame.top_panel
        if top_panel is None:
            print("Error: 'top_panel' is not initialized.")
            return
        #sorted_markers = sorted(genoclass.get_post_microhap().get_loc_ref_dict().keys())
        sorted_markers = sorted(genoclass.get_metadata().get_cur_mh_markers_list())
        genoclass.get_post_microhap().set_working_markers_list(sorted_markers)
        top_panel.options = sorted_markers if len(sorted_markers) != 0 else []
        top_panel.combobox.configure(values=top_panel.options)
        top_panel.combobox.set(top_panel.options[0] if top_panel.options else "")
        genoclass.get_post_microhap().set_dna_or_aa('dna')
    except AttributeError as e:
        print(f"Attribute error: {e}")
        # Handle the error, maybe log it or notify the user

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="#3b3b3b")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(0, 0), padx=(10, 10), sticky="ew")

    #footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)

    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="Previous", font=("Helvetica", 12, "bold"),
                                                command=lambda: on_previous_button_click(parent))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), pady=(10, 10), sticky="e")

    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next", font=("Helvetica", 12, "bold"))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), pady=(10, 10), sticky="w")
    return footer_frame

def on_previous_button_click(parent):
    parent.master.show_page("micro_data")

def on_next_button_click(parent):
    # Placeholder for the next button action
    genoclass = parent.master.genotype_class
    genoclass.generate_all()
    panel = parent.master.pages.get('micro_data', None)
    if panel is not None:
        if genoclass.get_parameter().get_outputdir() and os.path.isdir(genoclass.get_parameter().get_outputdir()):
            genoclass.get_parameter().set_analtype('snp')
            genoclass.get_metadata().read_locifile(genoclass.get_parameter(), genoclass.get_post_microhap(), True)
            panel.body_frame.top_panel.loci_entry.delete(0, 'end')
            panel.body_frame.top_panel.loci_entry.insert(0, genoclass.get_parameter().get_locifile())
            
            outfile = os.path.join(genoclass.get_parameter().get_outputdir(), 'all_sample_final_genotype.txt')
            if os.path.exists(outfile):
                genoclass.get_parameter().set_cur_microhap_input_file(outfile)
                genoclass.get_metadata().read_microhap_file(genoclass.get_parameter())
                panel.body_frame.top_panel.inputdir_var.delete(0, 'end')
                panel.body_frame.top_panel.inputdir_var.insert(0, outfile)
    parent.master.show_page("micro_data")

def create_bottom_panel(parent, body_frame):
    bottom_panel = ctk.CTkFrame(body_frame, fg_color="#3b3b3b")
    bottom_panel.grid(row=1, column=0, sticky="news", padx=(0,0), pady=(0,0))
    bottom_panel.grid_rowconfigure(0, weight=1)
    #bottom_panel.grid_rowconfigure(1,weight=1)#for the page flib page
    bottom_panel.grid_columnconfigure(0, weight=1)
    return bottom_panel

def create_microhap_fig_tbl_panel(bottom_panel, genoclass):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    
    # Configure bottom_panel to expand
    for rid in range(bottom_panel.grid_size()[1]):
        bottom_panel.grid_rowconfigure(rid, weight=0)
    for cid in range(bottom_panel.grid_size()[0]):
        bottom_panel.grid_columnconfigure(cid, weight=0)
    bottom_panel.grid(row=1, column=0, sticky="nsew", padx=(0,0), pady=(0,0))
    bottom_panel.grid_rowconfigure(0, weight=0)
    bottom_panel.grid_rowconfigure(1, weight=1)
    bottom_panel.grid_columnconfigure(0, weight=1)
    
    fig_tab_top_panel = ctk.CTkFrame(bottom_panel, bg_color="#3b3b3b")
    fig_tab_top_panel.grid(row=0, column=0, sticky='ew')  # Ensure horizontal expansion

    fig_tab_bottom_panel = ctk.CTkFrame(bottom_panel, bg_color="#3b3b3b")
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=0)  # Ensure both horizontal and vertical expansion

    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)  # Ensure vertical expansion
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)  # Ensure horizontal expansion
    
    update_com_tab(genoclass, fig_tab_bottom_panel)
    ctk.CTkButton(fig_tab_top_panel, text="comprehensive", font=("Helvetica", 10, "bold"),
                  width=child_button_size['width'], height=child_button_size['height'],
                command=lambda: update_com_tab(genoclass, fig_tab_bottom_panel)).grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")

    ctk.CTkButton(fig_tab_top_panel, text="simple", font=("Helvetica", 10, "bold"),
                  width=child_button_size['width'], height=child_button_size['height'],
                command=lambda: update_sim_tab(genoclass, fig_tab_bottom_panel)).grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Add a frame to act as the resize handle
    resize_handle = tk.Frame(fig_tab_bottom_panel, cursor="bottom_right_corner", bg="#3b3b3b")
    resize_handle.grid(row=2, column=1, sticky="se", padx=(0, 5), pady=(0, 5))  # Place in the bottom-right corner

    # Variables to store the initial position when resizing starts
    initial_x = initial_y = 0

    # Function to start resizing
    def start_resize(event):
        nonlocal initial_x, initial_y
        initial_x, initial_y = event.x_root, event.y_root

    # Function to perform resizing
    def perform_resize(event):
        nonlocal initial_x, initial_y
        dx = event.x_root - initial_x
        dy = event.y_root - initial_y
        new_width = fig_tab_bottom_panel.winfo_width() + dx
        new_height = fig_tab_bottom_panel.winfo_height() + dy
        fig_tab_bottom_panel.config(width=new_width, height=new_height)
        initial_x, initial_y = event.x_root, event.y_root

    # Bind mouse events to the resize handle
    resize_handle.bind("<ButtonPress-1>", start_resize)  # Start resizing on mouse press
    resize_handle.bind("<B1-Motion>", perform_resize)  # Perform resizing during mouse drag

def create_all_microhap_fig_tbl_panel(bottom_panel, genoclass):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
        
    for rid in range(bottom_panel.grid_size()[1]):
        bottom_panel.grid_rowconfigure(rid, weight=0)
    for cid in range(bottom_panel.grid_size()[0]):
        bottom_panel.grid_columnconfigure(cid, weight=0)
        
    bottom_panel.grid(row=1, column=0, sticky="news", padx=(2,2), pady=(2,2))
    bottom_panel.grid_rowconfigure(0, weight=0)
    bottom_panel.grid_rowconfigure(1, weight=1)
    bottom_panel.grid_columnconfigure(0, weight=1)
    
    fig_tab_top_panel = ctk.CTkFrame(bottom_panel, fg_color="#3b3b3b")
    fig_tab_top_panel.grid(row=0, column=0, sticky="ew")
    
    fig_tab_bottom_panel=ctk.CTkFrame(bottom_panel, fg_color="#3b3b3b")
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="news")
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)
    display_all_mh_com_table(fig_tab_bottom_panel, genoclass)
    ctk.CTkButton(fig_tab_top_panel, text="comprehensive", font=("Helvetica", 10, "bold"), width=child_button_size['width'], height=child_button_size['height'],
                command=lambda: display_all_mh_com_table(fig_tab_bottom_panel, genoclass)).grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
    
    ctk.CTkButton(fig_tab_top_panel, text="simple", font=("Helvetica", 10, "bold"), width=child_button_size['width'], height=child_button_size['height'],
                command=lambda: display_all_mh_sim_table(fig_tab_bottom_panel, genoclass)).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
     # Add a frame to act as the resize handle
    resize_handle = tk.Frame(fig_tab_bottom_panel, cursor="bottom_right_corner", bg="#3b3b3b")
    resize_handle.grid(row=2, column=1, sticky="se", padx=(0, 5), pady=(0, 5))  # Place in the bottom-right corner

    # Variables to store the initial position when resizing starts
    initial_x = initial_y = 0

    # Function to start resizing
    def start_resize(event):
        nonlocal initial_x, initial_y
        initial_x, initial_y = event.x_root, event.y_root

    # Function to perform resizing
    def perform_resize(event):
        nonlocal initial_x, initial_y
        dx = event.x_root - initial_x
        dy = event.y_root - initial_y
        new_width = fig_tab_bottom_panel.winfo_width() + dx
        new_height = fig_tab_bottom_panel.winfo_height() + dy
        fig_tab_bottom_panel.config(width=new_width, height=new_height)
        initial_x, initial_y = event.x_root, event.y_root

    # Bind mouse events to the resize handle
    resize_handle.bind("<ButtonPress-1>", start_resize)  # Start resizing on mouse press
    resize_handle.bind("<B1-Motion>", perform_resize)  # Perform resizing during mouse drag

def create_microhap_align_panel(bottom_panel, genoclass):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
        
    for rid in range(bottom_panel.grid_size()[1]):
        bottom_panel.grid_rowconfigure(rid, weight=0)
    for cid in range(bottom_panel.grid_size()[0]):
        bottom_panel.grid_columnconfigure(cid, weight=0)
        
    bottom_panel.grid(row=1, column=0, sticky="news", padx=(2,2), pady=(2,2))
    bottom_panel.grid_rowconfigure(0, weight=0)
    bottom_panel.grid_rowconfigure(1, weight=1)
    bottom_panel.grid_columnconfigure(0, weight=1)
    
    fig_tab_top_panel = ctk.CTkFrame(bottom_panel, fg_color="#3b3b3b")
    fig_tab_top_panel.grid(row=0, column=0, sticky="ew")
    fig_tab_top_panel.grid_rowconfigure(0,weight=0)
    
    fig_tab_bottom_panel=ctk.CTkFrame(bottom_panel, fg_color="#3b3b3b")
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="news")
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)
    fig_tab_bottom_panel.page_num = 0
    display_align(fig_tab_bottom_panel, genoclass, 'dna')
    ctk.CTkButton(fig_tab_top_panel, text="DNA", font=("Helvetica", 10, "bold"), width=child_button_size['width'], height=child_button_size['height'],
                command=lambda: display_align(fig_tab_bottom_panel, genoclass, 'dna')).grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
    
    ctk.CTkButton(fig_tab_top_panel, text="protien", font=("Helvetica", 10, "bold"), width=child_button_size['width'], height=child_button_size['height'],
                command=lambda: display_align(fig_tab_bottom_panel, genoclass, 'aa')).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    ctk.CTkButton(fig_tab_top_panel, text="phylo tree", font=("Helvetica", 10, "bold"), width=child_button_size['width'], height=child_button_size['height'],
                command=lambda: display_phylotre(fig_tab_bottom_panel, genoclass)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
     # Add a frame to act as the resize handle

    resize_handle = tk.Frame(fig_tab_bottom_panel, cursor="bottom_right_corner", bg="#3b3b3b")
    resize_handle.grid(row=2, column=1, sticky="se", padx=(0, 5), pady=(0, 5))  # Place in the bottom-right corner

    # Variables to store the initial position when resizing starts
    initial_x = initial_y = 0

    # Function to start resizing
    def start_resize(event):
        nonlocal initial_x, initial_y
        initial_x, initial_y = event.x_root, event.y_root

    # Function to perform resizing
    def perform_resize(event):
        nonlocal initial_x, initial_y
        dx = event.x_root - initial_x
        dy = event.y_root - initial_y
        new_width = fig_tab_bottom_panel.winfo_width() + dx
        new_height = fig_tab_bottom_panel.winfo_height() + dy
        fig_tab_bottom_panel.config(width=new_width, height=new_height)
        initial_x, initial_y = event.x_root, event.y_root

    # Bind mouse events to the resize handle
    resize_handle.bind("<ButtonPress-1>", start_resize)  # Start resizing on mouse press
    resize_handle.bind("<B1-Motion>", perform_resize)  # Perform resizing during mouse drag

def display_align(fig_tab_bottom_panel, genoclass, dna_aa):
    if dna_aa == 'dna':
        genoclass.get_post_microhap().set_dna_or_aa('dna')
        display_dna_seq_align(fig_tab_bottom_panel, genoclass)
    else:
        genoclass.get_post_microhap().set_dna_or_aa('aa')
        display_aa_seq_align(fig_tab_bottom_panel, genoclass)