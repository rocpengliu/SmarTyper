import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from ..utils import modern_messagebox
import threading
import matplotlib
from .results_geno_fig import update_geno_figs
from .results_geno_tab import update_geno_tab
from .results_geno_combo import update_genotype_tab, display_page
from .results_geno_tab_all import update_geno_tab_all
from .results_reads import update_reads_qual_distri
from .results_reads_all import update_all_reads_qual_distri
from ..utils.common import parent_button_size, child_button_size, bfont, bmbfont,bmfont, brfont, header_font, confirm_button_font, pnbuttonfont, fig_font
from ..utils.colors import COLORS
from ..utils.utils_common import print_time
from .results_summary import run_thread

matplotlib.use("Agg")

def results_viewer(parent):
    frame = ctk.CTkFrame(parent, fg_color=COLORS['background'])
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
    header_frame = ctk.CTkFrame(frame, fg_color=COLORS['card'], corner_radius=12)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(15, 10), padx=(15, 15))
    header_frame.grid_columnconfigure(0, weight=1)  # Center header content
    label = ctk.CTkLabel(header_frame, text="◘ Result Viewing", font=header_font,
                         fg_color="transparent", text_color=COLORS['primary'])
    label.pack(side=tk.LEFT, pady=(15, 15), padx=(30, 10))
    return header_frame

def create_body(parent, frame):
    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, sticky="nsew")

    body_frame.grid_rowconfigure(0, weight=0)  # Top panel
    body_frame.grid_rowconfigure(1, weight=6)  # Bottom panel
    body_frame.grid_columnconfigure(0, weight=1)  # Center columns
    #body_frame.grid_rowconfigure('all', weight=1)

    body_frame.top_panel = create_top_panel(parent, body_frame)
    body_frame.bottom_panel = create_bottom_panel(parent, body_frame)
    return body_frame

def create_top_panel(parent, body_frame):
    genoclass = parent.master.genotype_class
    top_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    top_panel.grid(row=0, column=0, sticky="ew", padx=body_frame.padx, pady=body_frame.pady)
    top_panel.grid_rowconfigure(0, weight=0)
    top_panel.grid_rowconfigure(1, weight=0)
    top_panel.grid_rowconfigure(2, weight=0)
    top_panel.grid_columnconfigure('all', weight=0)
    top_panel.button_refs = {}
    top_panel.button_child_refs = {}
    
    row = 0
    ctk.CTkLabel(top_panel, text="Sample or Marker:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,3), sticky="e")

    top_panel.res_type = ctk.StringVar(value=genoclass.get_res_param().get_res_type())
    ctk.CTkRadioButton(top_panel, text="sample", variable=top_panel.res_type, value="sample", font=brfont,
        command=lambda: [
            update_combox(genoclass, top_panel, "sample"),
            display_page(body_frame.bottom_panel, genoclass),
            top_panel.highlight_buttons(top_panel, "Geno Combo")
        ]).grid(row=row, column=1, pady=(1,3), padx=(20, 80), sticky="w")
    
    ctk.CTkRadioButton(top_panel, text="marker", variable=top_panel.res_type, value="marker", font=brfont,
        command=lambda: [
            update_combox(genoclass, top_panel, "marker"),
            display_page(body_frame.bottom_panel, genoclass),
            top_panel.highlight_buttons(top_panel, "Geno Combo")
        ]).grid(row=row, column=1, pady=(1,3), padx=(80, 0), sticky="e")

    top_panel.res_type.trace_add("write", lambda *args: genoclass.get_res_param().set_res_type(top_panel.res_type.get()))

    # Initialize ComboBox with an empty list
    top_panel.options = []
    selected_option = tk.StringVar(value="")
    top_panel.combobox = ttk.Combobox(top_panel, values=top_panel.options, textvariable=selected_option, font=brfont)
    top_panel.combobox.grid(row=row, column=2, padx=(25, 10), pady=(3,3), sticky="w")
    selected_option.trace_add("write", lambda *args: (genoclass.get_res_param().set_sample_or_marker(selected_option.get()),
                                                      print(f"Selected sample or marker: {selected_option.get()}"),
                                                      top_panel.highlight_buttons(top_panel, "Geno Combo"),
                                                      update_genotype_tab(parent, body_frame.bottom_panel)))
    row += 1

    geno_combo_btn = ctk.CTkButton(top_panel, text="Geno Combo", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color=COLORS['primary'], hover_color=COLORS['secondary'], corner_radius=8,
        text_color="white",
        command=lambda: [ top_panel.highlight_buttons(top_panel, "Geno Combo"),
                         display_page(body_frame.bottom_panel, genoclass)])
    geno_combo_btn.grid(row=row, column=0, padx=(5,5), pady=(1,1), sticky='w')
    top_panel.button_refs['Geno Combo'] = geno_combo_btn

    geno_fig_tab_btn = ctk.CTkButton(top_panel, text="Geno Fig & Tab", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color="transparent", hover_color=COLORS['secondary'], corner_radius=8,
        text_color="white",
        command=lambda: [top_panel.highlight_buttons(top_panel, "Geno Fig & Tab", "figure"),
                         create_geno_fig_tab_panel(parent,body_frame.bottom_panel)])
    geno_fig_tab_btn.grid(row=row, column=1, padx=(5,5), pady=(1,1), sticky='w')
    top_panel.button_refs["Geno Fig & Tab"] = geno_fig_tab_btn

    all_sample_geno_btn = ctk.CTkButton(top_panel, text="All Sample Geno", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color="transparent", hover_color=COLORS['secondary'], corner_radius=8,
        text_color="white",
        command=lambda: [top_panel.highlight_buttons(top_panel, "All Sample Geno"),
                         update_geno_tab_all(parent,body_frame.bottom_panel)])
    all_sample_geno_btn.grid(row=row, column=2, padx=(5,5), pady=(1,1), sticky='w')
    top_panel.button_refs["All Sample Geno"] = all_sample_geno_btn

    sample_reads_btn = ctk.CTkButton(top_panel, text="Sample Reads", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color="transparent", hover_color=COLORS['secondary'], corner_radius=8,
        text_color="white",
        command=lambda: [top_panel.highlight_buttons(top_panel, "Sample Reads", "s_quality"),
                         create_reads_panel(parent,body_frame.bottom_panel,'single')])
    sample_reads_btn.grid(row=row, column=3, padx=(5,5), pady=(1,1), sticky='w')
    top_panel.button_refs["Sample Reads"] = sample_reads_btn

    all_sample_reads_btn = ctk.CTkButton(top_panel, text="All Sample Reads", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color="transparent", hover_color=COLORS['secondary'], corner_radius=8,
        text_color="white",
        command=lambda: [top_panel.highlight_buttons(top_panel, "All Sample Reads", 'a_quality'),
                         create_reads_panel(parent,body_frame.bottom_panel,'all')])
    all_sample_reads_btn.grid(row=row, column=4, padx=(5,5), pady=(1,1), sticky='w')
    top_panel.button_refs["All Sample Reads"] = all_sample_reads_btn

    top_panel.highlight_buttons = lambda top_panel, clicked_btn_name, child_name=None: highlight_buttons(top_panel, clicked_btn_name, child_name)
    top_panel.highlight_buttons(top_panel, "Geno Combo")
    return top_panel

def highlight_buttons(top_panel, clicked_btn_name, child_name=None):
    if not clicked_btn_name:
        return
    for name, btn in top_panel.button_refs.items():
            try:
                if name == clicked_btn_name:
                    btn.configure(fg_color=COLORS['primary'], hover_color=COLORS['secondary'], text_color="white")
                    highlight_children_button(top_panel, child_name)
                else:
                    btn.configure(fg_color="transparent", hover_color=COLORS['secondary'], text_color="white")
            except Exception:
                print(f"Error highlighting button: {name}")
    top_panel.update_idletasks()
    
def highlight_children_button(top_panel, child_name):
    if not child_name:
        return
    #print_time(f"Highlighting child button: child_name={child_name}")
    for name, btn in top_panel.button_child_refs.items():
            try:
                if name == child_name:
                    btn.configure(fg_color=COLORS['primary'], hover_color=COLORS['secondary'], text_color="white")
                else:
                    btn.configure(fg_color="transparent", hover_color=COLORS['secondary'], text_color="white")
            except Exception:
                print(f"Error highlighting child button: {name}")
    top_panel.update_idletasks()

def update_combox(genoclass, top_panel, type):
    """Update the options in the ComboBox based on the type."""
    top_panel.options = genoclass.get_metadata().get_samples_list() if type == "sample" else genoclass.get_metadata().get_ref_markers_list()
    top_panel.combobox.configure(values=top_panel.options)
    top_panel.combobox.set(top_panel.options[0] if top_panel.options else "")  # Set the default value

def update_combox_from_others(parent):
    try:
        genoclass = parent.master.genotype_class
        res_frame = parent.master.pages.get('results', None)
        if res_frame is None:
            print(f"Error: 'results' page is not available.")
            return
        top_panel = res_frame.body_frame.top_panel
        if top_panel is None:
            print(f"Error: 'top_panel' is not initialized.")
            return
        genoclass.get_res_param().set_res_type("sample")
        top_panel.options = genoclass.get_metadata().get_samples_list() if genoclass.get_metadata().get_samples_list() != [] else []
        top_panel.combobox.configure(values=top_panel.options)
        top_panel.combobox.set(top_panel.options[0] if top_panel.options else "")
    except AttributeError as e:
        print(f"Attribute error: {e}")
        # Handle the error, maybe log it or notify the user

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="transparent")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(10, 10), padx=(15, 15), sticky="ew")

    #footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)

    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="← Previous", font=pnbuttonfont,
                                                fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                                corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                                command=lambda: on_previous_button_click(parent))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), pady=(10, 10), sticky="e")

    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Next →", font=pnbuttonfont, state="disabled",
                                            fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                            corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                            command=lambda: on_next_button_click(parent, footer_frame))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), pady=(10, 10), sticky="w")
    return footer_frame

def on_previous_button_click(parent):
    if parent.master.genotype_class.get_parameter().is_project_genotype_model():
        parent.master.show_page("loader")
    else:
        parent.master.show_page("run")

def on_next_button_click(parent, footer_frame):
    foot_frame = parent.master.pages.get('results', None).footer_frame
    if foot_frame is not None:
        foot_frame.next_button.configure(state = 'disabled')
    parent.master.show_page("summary")
    parent.after(100, lambda:run_thread(parent))
        
def create_bottom_panel(parent, body_frame):
    bottom_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    bottom_panel.grid(row=1, column=0, sticky="news", padx=(0,0), pady=(0,0))
    bottom_panel.grid_rowconfigure(0, weight=1)
    bottom_panel.grid_rowconfigure(1,weight=0)#for the page flib page
    bottom_panel.grid_columnconfigure(0, weight=1)
    return bottom_panel

def create_geno_fig_tab_panel(parent, bottom_panel):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    # Clear child button refs to avoid referencing destroyed widgets
    top_panel = parent.master.pages['results'].body_frame.top_panel
    top_panel.button_child_refs.clear()
    # Configure bottom_panel to expand
    for rid in range(bottom_panel.grid_size()[1]):
        bottom_panel.grid_rowconfigure(rid, weight=0)
    for cid in range(bottom_panel.grid_size()[0]):
        bottom_panel.grid_columnconfigure(cid, weight=0)
    bottom_panel.grid(row=1, column=0, sticky="nsew", padx=(0,0), pady=(0,0))
    bottom_panel.grid_rowconfigure(0, weight=0)
    bottom_panel.grid_rowconfigure(1, weight=1)
    bottom_panel.grid_columnconfigure(0, weight=1)
    
    fig_tab_top_panel = ctk.CTkFrame(bottom_panel, fg_color=COLORS['card'])
    fig_tab_top_panel.grid(row=0, column=0, sticky='ew')

    fig_tab_bottom_panel = ctk.CTkFrame(bottom_panel, fg_color="white")
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=0)
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)

    update_geno_figs(parent, fig_tab_bottom_panel)
    figure_btn = ctk.CTkButton(fig_tab_top_panel, text="figure", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color=COLORS['primary'], hover_color=COLORS['secondary'], text_color="white",
                  command=lambda: [highlight_children_button(top_panel, 'figure'),
                                   update_geno_figs(parent, fig_tab_bottom_panel)])
    figure_btn.grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
    top_panel.button_child_refs['figure'] = figure_btn
    
    table_btn = ctk.CTkButton(fig_tab_top_panel, text="table", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color="transparent", hover_color=COLORS['secondary'], text_color="white",
                  command=lambda: [highlight_children_button(top_panel, 'table'),
                                   update_geno_tab(parent, fig_tab_bottom_panel)])
    table_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    top_panel.button_child_refs['table'] = table_btn

    # Default highlight to 'figure'
    highlight_children_button(top_panel, 'figure')

def create_reads_panel(parent, bottom_panel, sam_type):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    # Clear child button refs to avoid referencing destroyed widgets
    top_panel = parent.master.pages['results'].body_frame.top_panel
    top_panel.button_child_refs.clear()
    # Configure bottom_panel to expand
    for rid in range(bottom_panel.grid_size()[1]):
        bottom_panel.grid_rowconfigure(rid, weight=0)
    for cid in range(bottom_panel.grid_size()[0]):
        bottom_panel.grid_columnconfigure(cid, weight=0)
    bottom_panel.grid(row=1, column=0, sticky="nsew", padx=(0,0), pady=(0,0))
    bottom_panel.grid_rowconfigure(0, weight=0) 
    bottom_panel.grid_rowconfigure(1, weight=1) 
    bottom_panel.grid_columnconfigure(0, weight=1)
    
    reads_top_panel = ctk.CTkFrame(bottom_panel, fg_color=COLORS['card'])
    reads_top_panel.grid(row=0, column=0, sticky='ew')

    fig_bottom_panel = ctk.CTkFrame(bottom_panel, fg_color="white")
    fig_bottom_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
    fig_bottom_panel.grid_rowconfigure(0, weight=1)
    fig_bottom_panel.grid_rowconfigure(1, weight=0)
    fig_bottom_panel.grid_columnconfigure(0, weight=1)

    if sam_type == "single":
        update_reads_qual_distri(parent, fig_bottom_panel, 'qual')
        quality_btn = ctk.CTkButton(reads_top_panel, text="quality", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color=COLORS['primary'], hover_color=COLORS['secondary'], text_color="white",
                  command=lambda: [highlight_children_button(top_panel, 's_quality'),
                                   update_reads_qual_distri(parent, fig_bottom_panel, 'qual')])
        quality_btn.grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
        top_panel.button_child_refs['s_quality'] = quality_btn
        distribution_btn = ctk.CTkButton(reads_top_panel, text="distribution", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color="transparent", hover_color=COLORS['secondary'], text_color="white",
                  command=lambda: [highlight_children_button(top_panel, 's_distribution'),
                                   update_reads_qual_distri(parent, fig_bottom_panel, 'distri')])
        distribution_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        top_panel.button_child_refs['s_distribution'] = distribution_btn
        highlight_children_button(top_panel, 's_quality')
    elif sam_type == "all":
        update_all_reads_qual_distri(parent, fig_bottom_panel, 'qual')
        quality_btn = ctk.CTkButton(reads_top_panel, text="quality", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color=COLORS['primary'], hover_color=COLORS['secondary'], text_color="white",
                  command=lambda: [highlight_children_button(top_panel, 'a_quality'),
                                   update_all_reads_qual_distri(parent, fig_bottom_panel, 'qual')])
        quality_btn.grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
        top_panel.button_child_refs['a_quality'] = quality_btn
        distribution_btn = ctk.CTkButton(reads_top_panel, text="distribution", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color="transparent", hover_color=COLORS['secondary'], text_color="white",
                  command=lambda: [highlight_children_button(top_panel, 'a_distribution'),
                                   update_all_reads_qual_distri(parent, fig_bottom_panel, 'distri')])
        distribution_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        top_panel.button_child_refs['a_distribution'] = distribution_btn
        highlight_children_button(top_panel, 'a_quality')
    else:
        return
