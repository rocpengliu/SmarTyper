import customtkinter as ctk
import tkinter as tk
import matplotlib
from .results_geno_fig import update_geno_figs
from .results_geno_tab import update_geno_tab
from .results_geno_combo import update_genotype_tab, display_page
from .results_geno_tab_all import update_geno_tab_all
from .results_reads import update_reads_qual_distri
from .results_reads_all import update_all_reads_qual_distri
from ..utils.common import child_button_size

matplotlib.use("Agg")

def results_viewer(parent):
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
    label = ctk.CTkLabel(header_frame, text="Result Viewing", font=("Helvetica", 30, "bold"),
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
    top_panel.grid_rowconfigure(2, weight=0)  # Ensure the top row does not expand vertically
    top_panel.grid_columnconfigure('all', weight=0)  # Adjust if needed

    row = 0
    ctk.CTkLabel(top_panel, text="Sample or Marker:", font=body_frame.bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,3), sticky="e")

    top_panel.res_type = ctk.StringVar(value=genoclass.get_res_param().get_res_type())
    ctk.CTkRadioButton(top_panel, text="sample", variable=top_panel.res_type, value="sample", font=body_frame.brfont,
                       command=lambda: update_combox(genoclass, top_panel, "sample")).grid(row=row, column=1, pady=(1,3), padx=(20, 80), sticky="w")
    ctk.CTkRadioButton(top_panel, text="marker", variable=top_panel.res_type, value="marker", font=body_frame.brfont,
                       command=lambda: update_combox(genoclass, top_panel, "marker")).grid(row=row, column=1, pady=(1,3), padx=(80, 0), sticky="e")

    top_panel.res_type.trace_add("write", lambda *args: genoclass.get_res_param().set_res_type(top_panel.res_type.get()))

    # Initialize ComboBox with an empty list
    top_panel.options = []
    selected_option = tk.StringVar(value="")
    top_panel.combobox = ctk.CTkComboBox(top_panel, values=top_panel.options, variable=selected_option, font=body_frame.brfont)
    top_panel.combobox.grid(row=row, column=2, padx=(25, 10), pady=(3,3), sticky="w")
    selected_option.trace_add("write", lambda *args: (genoclass.get_res_param().set_sample_or_marker(selected_option.get()),
                                                      print(f"Selected sample or marker: {selected_option.get()}"),
                                                      update_genotype_tab(parent, body_frame.bottom_panel)))
    row += 1
    ctk.CTkButton(top_panel, text="geno combo", font=("Helvetica", 12, "bold"),
                width=child_button_size['width'], height=child_button_size['height'],
                command=lambda:display_page(body_frame.bottom_panel, genoclass)).grid(row=row, column=0, padx=(5,5), pady=(1,1), sticky='w')
    
    ctk.CTkButton(top_panel, text="geno fig & tab", font=("Helvetica", 12, "bold"),
                  width=child_button_size['width'], height=child_button_size['height'],
                command=lambda:create_geno_fig_tab_panel(parent,body_frame.bottom_panel)).grid(row=row, column=1, padx=(5,5), pady=(1,1), sticky='w')

    ctk.CTkButton(top_panel, text="all sample geno", font=("Helvetica", 12, "bold"),
                  width=child_button_size['width'], height=child_button_size['height'],
                command=lambda:update_geno_tab_all(parent,body_frame.bottom_panel)).grid(row=row, column=2, padx=(5,5), pady=(1,1), sticky='w')
    
    ctk.CTkButton(top_panel, text="sample reads", font=("Helvetica", 12, "bold"),
                  width=child_button_size['width'], height=child_button_size['height'],
                command=lambda:create_reads_panel(parent,body_frame.bottom_panel,'single')).grid(row=row, column=3, padx=(5,5), pady=(1,1), sticky='w')
    
    ctk.CTkButton(top_panel, text="all sample reads", font=("Helvetica", 12, "bold"),
                  width=child_button_size['width'], height=child_button_size['height'],
                command=lambda:create_reads_panel(parent,body_frame.bottom_panel,'all')).grid(row=row, column=4, padx=(5,5), pady=(1,1), sticky='w')
    return top_panel

def update_combox(genoclass, top_panel, type):
    """Update the options in the ComboBox based on the type."""
    top_panel.options = genoclass.get_metadata().get_samples_list() if type == "sample" else genoclass.get_metadata().get_ref_markers_list()
    top_panel.combobox.configure(values=top_panel.options)
    top_panel.combobox.set(top_panel.options[0] if top_panel.options else "")  # Set the default value

def update_combox_from_others(parent):
    """Update the ComboBox options from other components."""
    try:
        genoclass = parent.master.genotype_class
        res_frame = parent.master.pages.get('results', None)
        
        if res_frame is None:
            print("Error: 'results' page is not available.")
            return
        top_panel = res_frame.body_frame.top_panel
        if top_panel is None:
            print("Error: 'top_panel' is not initialized.")
            return
        top_panel.options = genoclass.get_metadata().get_samples_list() if genoclass.get_metadata().get_samples_list() != [] else []
        top_panel.combobox.configure(values=top_panel.options)
        top_panel.combobox.set(top_panel.options[0] if top_panel.options else "")
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

    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next", font=("Helvetica", 12, "bold"),
                                            command=lambda: on_next_button_click(parent))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), pady=(10, 10), sticky="w")
    return footer_frame

def on_previous_button_click(parent):
    parent.master.show_page("run")

def on_next_button_click(parent):
    genoclass = parent.master.genotype_class
    genoclass.generate_all()
    parent.master.show_page("summary")
def create_bottom_panel(parent, body_frame):
    bottom_panel = ctk.CTkFrame(body_frame, fg_color="#3b3b3b")
    bottom_panel.grid(row=1, column=0, sticky="news", padx=(0,0), pady=(0,0))
    bottom_panel.grid_rowconfigure(0, weight=1)
    bottom_panel.grid_rowconfigure(1,weight=0)#for the page flib page
    bottom_panel.grid_columnconfigure(0, weight=1)
    return bottom_panel

def create_geno_fig_tab_panel(parent, bottom_panel):
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
    
    update_geno_figs(parent, fig_tab_bottom_panel)
    ctk.CTkButton(fig_tab_top_panel, text="figure", font=("Helvetica", 10, "bold"),
                  width=child_button_size['width'], height=child_button_size['height'],
                command=lambda: update_geno_figs(parent, fig_tab_bottom_panel)).grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")

    ctk.CTkButton(fig_tab_top_panel, text="table", font=("Helvetica", 10, "bold"),
                  width=child_button_size['width'], height=child_button_size['height'],
                command=lambda: update_geno_tab(parent, fig_tab_bottom_panel)).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
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

def create_reads_panel(parent, bottom_panel, sam_type):
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
    
    reads_top_panel = ctk.CTkFrame(bottom_panel, bg_color="#3b3b3b")
    reads_top_panel.grid(row=0, column=0, sticky='ew')  # Set to expand horizontally

    fig_bottom_panel = ctk.CTkFrame(bottom_panel, bg_color="#3b3b3b")
    fig_bottom_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)  # Set to expand horizontally and vertically

    # Configure grid of fig_bottom_panel to expand
    fig_bottom_panel.grid_rowconfigure(0, weight=1)  # Make row 0 expand vertically
    fig_bottom_panel.grid_rowconfigure(1, weight=0)  # Make row 0 expand vertically
    fig_bottom_panel.grid_columnconfigure(0, weight=1)  # Make column 0 expand horizontally
    
    if sam_type == "single":
        update_reads_qual_distri(parent, fig_bottom_panel, 'qual')
        ctk.CTkButton(reads_top_panel, text="quality", font=("Helvetica", 10, "bold"),
                      width=child_button_size['width'], height=child_button_size['height'],
                    command=lambda: update_reads_qual_distri(parent, fig_bottom_panel, 'qual')).grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
        
        ctk.CTkButton(reads_top_panel, text="distribution", font=("Helvetica", 10, "bold"),
                      width=child_button_size['width'], height=child_button_size['height'],
                    command=lambda: update_reads_qual_distri(parent, fig_bottom_panel, 'distri')).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    elif sam_type == "all":
        update_all_reads_qual_distri(parent, fig_bottom_panel, 'qual')
        ctk.CTkButton(reads_top_panel, text="quality", font=("Helvetica", 10, "bold"),
                      width=child_button_size['width'], height=child_button_size['height'],
                    command=lambda: update_all_reads_qual_distri(parent, fig_bottom_panel, 'qual')).grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
        
        ctk.CTkButton(reads_top_panel, text="distribution", font=("Helvetica", 10, "bold"),
                      width=child_button_size['width'], height=child_button_size['height'],
                    command=lambda: update_all_reads_qual_distri(parent, fig_bottom_panel, 'distri')).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    else:
        return
