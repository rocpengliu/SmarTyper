from tkinter import ttk
import customtkinter as ctk
import tkinter as tk
import matplotlib
import os
from .micro_dna_align import display_dna_seq_align
from .micro_aa_align import display_aa_seq_align
from .micro_table_fig import update_com_tab, update_sim_tab, update_sim_fig
from .micro_all_table_fig import display_all_mh_com_table, display_all_mh_sim_table
from .micro_tree import display_phylotre
from ..utils.common import child_button_size, pnbuttonfont, fig_font, header_font, bmbfont, brfont, bfont
from ..utils.colors import COLORS

matplotlib.use("Agg")


def micro_viewer(parent):
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
    
    highlight_par_buttons(frame.body_frame.top_panel,frame.body_frame.bottom_panel,"micro_align","dna")
    return frame

def create_header(frame):
    header_frame = ctk.CTkFrame(frame, fg_color=COLORS['card'], corner_radius=12)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(15, 10), padx=(15, 15))
    header_frame.grid_columnconfigure(0, weight=1)
    label = ctk.CTkLabel(header_frame, text="◇ Microtype Viewing", font=header_font,
                         fg_color="transparent", text_color=COLORS['accent'])
    label.pack(side=tk.LEFT, pady=(15, 15), padx=(30, 10))
    return header_frame

def create_body(parent, frame):
    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, sticky="nsew")

    body_frame.grid_rowconfigure(0, weight=0)  # Top panel
    body_frame.grid_rowconfigure(1, weight=1)  # Bottom panel
    body_frame.grid_columnconfigure(0, weight=1)  # Center columns
    #body_frame.grid_rowconfigure('all', weight=1)

    body_frame.bottom_panel = create_bottom_panel(parent, body_frame)
    body_frame.top_panel = create_top_panel(parent, body_frame)
    return body_frame

def create_top_panel(parent, body_frame):
    genoclass = parent.master.genotype_class
    top_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    top_panel.grid(row=0, column=0, sticky="ew", padx=body_frame.padx, pady=body_frame.pady)
    top_panel.grid_rowconfigure(0, weight=0)
    top_panel.grid_rowconfigure(1, weight=0)
    top_panel.grid_columnconfigure('all', weight=0)
    top_panel.highlight_fg = COLORS["accent"]
    top_panel.highlight_hover = COLORS["primary"]
    top_panel.dim_fg = COLORS["card"]
    top_panel.dim_hover = COLORS["secondary"]

    row = 0
    ctk.CTkLabel(top_panel, text="Locus:", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(1,3), sticky="e")

    top_panel.options = []
    selected_option = tk.StringVar(value="")
    top_panel.combobox = ttk.Combobox(top_panel, values=top_panel.options, textvariable=selected_option, font=brfont)
    top_panel.combobox.grid(row=row, column=1, padx=(25, 10), pady=(3,3), sticky="w")
    selected_option.trace_add("write", lambda *args: (genoclass.get_post_microhap().set_selected_marker(selected_option.get()),
                                                      highlight_par_buttons(body_frame.top_panel, body_frame.bottom_panel, parent_name="micro_align", child_name="dna"),
                                                      create_microhap_align_panel(body_frame.top_panel, body_frame.bottom_panel, genoclass)))
    row += 1

    # Store button references
    top_panel.button_refs = {}
    align_btn = ctk.CTkButton(top_panel, text="microtype sequence", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
        command=lambda: [highlight_par_buttons(body_frame.top_panel, body_frame.bottom_panel, "micro_align", "dna"),
                         create_microhap_align_panel(body_frame.top_panel, body_frame.bottom_panel, genoclass)])
    align_btn.grid(row=row, column=0, padx=20, pady=(15,1), sticky='w')
    top_panel.button_refs["micro_align"] = align_btn

    # microhap table (parent/child)
    table_btn_hap = ctk.CTkButton(top_panel, text="microhap table (single)", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
        command=lambda: [highlight_par_buttons(body_frame.top_panel, body_frame.bottom_panel, "microhap_table", "sing_compre_hap"),
                         create_microhap_fig_tbl_panel(body_frame.top_panel, body_frame.bottom_panel, genoclass)])
    table_btn_hap.grid(row=row, column=1, padx=20, pady=(15,1), sticky='w')
    top_panel.button_refs["microhap_table"] = table_btn_hap
    
    # micropep table (parent/child)
    table_btn_pep = ctk.CTkButton(top_panel, text="micropep table (single)", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
        command=lambda: [highlight_par_buttons(body_frame.top_panel, body_frame.bottom_panel, "micropep_table", "sing_compre_pep"),
                         create_micropep_fig_tbl_panel(body_frame.top_panel, body_frame.bottom_panel, genoclass)])
    table_btn_pep.grid(row=row, column=2, padx=20, pady=(15,1), sticky='w')
    top_panel.button_refs["micropep_table"] = table_btn_pep
    
    # microhap table (all) (parent/child)
    table_all_btn_hap = ctk.CTkButton(top_panel, text="microhap table (all)", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
        command=lambda: [highlight_par_buttons(body_frame.top_panel, body_frame.bottom_panel, "microhap_table_all", "all_compre_hap"),
                         create_all_microhap_fig_tbl_panel(body_frame.top_panel, body_frame.bottom_panel, genoclass)])
    table_all_btn_hap.grid(row=row, column=3, padx=20, pady=(15,1), sticky='w')
    top_panel.button_refs["microhap_table_all"] = table_all_btn_hap

    # micropep table (all) (parent/child)
    table_all_btn_pep = ctk.CTkButton(top_panel, text="micropep table (all)", font=bmbfont,
        width=child_button_size['width'], height=child_button_size['height'],
        fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
        command=lambda: [highlight_par_buttons(body_frame.top_panel, body_frame.bottom_panel, "micropep_table_all", "all_compre"),
                         create_all_micropep_fig_tbl_panel(body_frame.top_panel, body_frame.bottom_panel, genoclass)])
    table_all_btn_pep.grid(row=row, column=4, padx=20, pady=(15,1), sticky='w')
    top_panel.button_refs["micropep_table_all"] = table_all_btn_pep

    # Highlight the first parent and its child by default
    #top_panel.highlight_par_buttons = lambda top_panel, bottom_panel, parent_name, child_name=None: highlight_par_buttons(top_panel, bottom_panel, parent_name, child_name)
    #top_panel.highlight_par_buttons(top_panel, body_frame.bottom_panel, "micro_align", "dna")

    return top_panel

    # --- Button highlight/dim logic ---
def highlight_par_buttons(top_panel, bottom_panel, parent_name=None, child_name=None):
    if not parent_name:
        return
    for name, btn in top_panel.button_refs.items():
        try:
            if name == parent_name:
                btn.configure(fg_color=top_panel.highlight_fg, hover_color=top_panel.highlight_hover, text_color = "white")
                highlight_children_button(top_panel, bottom_panel, child_name)
            else:
                btn.configure(fg_color=top_panel.dim_fg, hover_color=top_panel.dim_hover, text_color = "white")
        except Exception as e:
            print(f"Error highlighting button {name}: {e}")
    top_panel.update_idletasks()
    
def highlight_children_button(top_panel, bottom_panel, child_name):
    if not child_name:
        return
    for name, btn in bottom_panel.child_btn_refs.items():
        try:
            if name == child_name:
                btn.configure(fg_color=top_panel.highlight_fg, hover_color=top_panel.highlight_hover, text_color = "white")
            else:
                btn.configure(fg_color=top_panel.dim_fg, hover_color=top_panel.dim_hover, text_color = "white")
        except Exception as e:
            print(f"Error highlighting child button {name}: {e}")
    bottom_panel.update_idletasks()
    
def update_combox(genoclass, top_panel, type):
    """Update the options in the ComboBox based on the type."""
    top_panel.options = list(genoclass.get_post_microhap().get_working_markers_set())
    top_panel.combobox.configure(values=top_panel.options)
    top_panel.combobox.set(top_panel.options[0] if top_panel.options else "")  # Set the default value

def update_combox_from_others_micro(parent):
    """Update the ComboBox options from other components."""
    try:
        genoclass = parent.master.genotype_class
        res_frame = parent.master.pages.get('microtype_results', None)

        if res_frame is None:
            print(f"Error: 'microtype_results' page is not available.")
            return
        top_panel = res_frame.body_frame.top_panel
        if top_panel is None:
            print(f"Error: 'top_panel' is not initialized.")
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
    footer_frame = ctk.CTkFrame(frame, fg_color="transparent")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(0, 0), padx=(10, 10), sticky="ew")

    #footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)

    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="← Previous", font=pnbuttonfont,
                                                fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                                                corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                                command=lambda: on_previous_button_click(parent))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), pady=(10, 10), sticky="e")

    footer_frame.next_button = ctk.CTkButton(footer_frame, text="Home →", font=pnbuttonfont, state="normal",
                                            fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                                            corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                            command=lambda: parent.master.show_page("home"))
    footer_frame.next_button.grid(row=0, column=1, padx=(100, 10), pady=(10, 10), sticky="w")
    return footer_frame

def on_previous_button_click(parent):
    parent.master.show_page("microtype_data")

def create_bottom_panel(parent, body_frame):
    bottom_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    bottom_panel.grid(row=1, column=0, sticky="news", padx=(0,0), pady=(0,0))
    bottom_panel.grid_rowconfigure(0, weight=1)
    #bottom_panel.grid_rowconfigure(1,weight=1)#for the page flib page
    bottom_panel.grid_columnconfigure(0, weight=1)
    bottom_panel.child_btn_refs = {}
    return bottom_panel

def create_microhap_fig_tbl_panel(top_panel, bottom_panel, genoclass):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    bottom_panel.child_btn_refs.clear()
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

    sing_compre_btn = ctk.CTkButton(fig_tab_top_panel, text="comprehensive", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "sing_compre_hap"),
                                 update_com_tab(genoclass, fig_tab_bottom_panel, dna = True)])
    sing_compre_btn.grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
    bottom_panel.child_btn_refs["sing_compre_hap"] = sing_compre_btn

    sing_simple_btn = ctk.CTkButton(fig_tab_top_panel, text="simple", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "sing_simple_hap"),
                                update_sim_tab(genoclass, fig_tab_bottom_panel, dna = True)])
    sing_simple_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    bottom_panel.child_btn_refs["sing_simple_hap"] = sing_simple_btn
    
    sing_fig_btn = ctk.CTkButton(fig_tab_top_panel, text="figure", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "sing_fig_hap"),
                                update_sim_fig(fig_tab_bottom_panel, genoclass, dna = True)])
    sing_fig_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    bottom_panel.child_btn_refs["sing_fig_hap"] = sing_fig_btn

    # Add a frame to act as the resize handle
    resize_handle = tk.Frame(fig_tab_bottom_panel, cursor="bottom_right_corner", bg="#3b3b3b")
    resize_handle.grid(row=2, column=1, sticky="se", padx=(0, 5), pady=(0, 5))  # Place in the bottom-right corner

    # Bind mouse events to the resize handle
    state = {'initial_x': 0, 'initial_y': 0}
    resize_handle.bind("<ButtonPress-1>", lambda event: start_resize(event, state))  # Start resizing on mouse press
    resize_handle.bind("<B1-Motion>", lambda event: perform_resize(event, state, fig_tab_bottom_panel))  # Perform resizing during mouse drag
    
        # Highlight the first child by default
    highlight_children_button(top_panel, bottom_panel, "sing_compre_hap")
    update_com_tab(genoclass, fig_tab_bottom_panel, dna = True)
    
def create_micropep_fig_tbl_panel(top_panel, bottom_panel, genoclass):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    bottom_panel.child_btn_refs.clear()
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

    sing_compre_btn = ctk.CTkButton(fig_tab_top_panel, text="comprehensive", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "sing_compre_pep"),
                                 update_com_tab(genoclass, fig_tab_bottom_panel, dna=False)])
    sing_compre_btn.grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
    bottom_panel.child_btn_refs["sing_compre_pep"] = sing_compre_btn

    sing_simple_btn = ctk.CTkButton(fig_tab_top_panel, text="simple", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "sing_simple_pep"),
                                update_sim_tab(genoclass, fig_tab_bottom_panel, dna=False)])
    sing_simple_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    bottom_panel.child_btn_refs["sing_simple_pep"] = sing_simple_btn
    
    sing_fig_btn = ctk.CTkButton(fig_tab_top_panel, text="figure", font=fig_font,
                  width=child_button_size['width'], height=child_button_size['height'],
                  fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "sing_fig_pep"),
                                update_sim_fig(fig_tab_bottom_panel, genoclass, dna=False)])
    sing_fig_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    bottom_panel.child_btn_refs["sing_fig_pep"] = sing_fig_btn

    # Add a frame to act as the resize handle
    resize_handle = tk.Frame(fig_tab_bottom_panel, cursor="bottom_right_corner", bg="#3b3b3b")
    resize_handle.grid(row=2, column=1, sticky="se", padx=(0, 5), pady=(0, 5))  # Place in the bottom-right corner

    # Bind mouse events to the resize handle
    state = {'initial_x': 0, 'initial_y': 0}
    resize_handle.bind("<ButtonPress-1>", lambda event: start_resize(event, state))  # Start resizing on mouse press
    resize_handle.bind("<B1-Motion>", lambda event: perform_resize(event, state, fig_tab_bottom_panel))  # Perform resizing during mouse drag
    
        # Highlight the first child by default
    highlight_children_button(top_panel, bottom_panel, "sing_compre_pep")
    update_com_tab(genoclass, fig_tab_bottom_panel, dna=False)

def create_all_microhap_fig_tbl_panel(top_panel,bottom_panel, genoclass):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    bottom_panel.child_btn_refs.clear()
    for rid in range(bottom_panel.grid_size()[1]):
        bottom_panel.grid_rowconfigure(rid, weight=0)
    for cid in range(bottom_panel.grid_size()[0]):
        bottom_panel.grid_columnconfigure(cid, weight=0)
        
    bottom_panel.grid(row=1, column=0, sticky="news", padx=(2,2), pady=(2,2))
    bottom_panel.grid_rowconfigure(0, weight=0)
    bottom_panel.grid_rowconfigure(1, weight=1)
    bottom_panel.grid_columnconfigure(0, weight=1)
    
    fig_tab_top_panel = ctk.CTkFrame(bottom_panel, fg_color="transparent")
    fig_tab_top_panel.grid(row=0, column=0, sticky='ew')
    
    fig_tab_bottom_panel=ctk.CTkFrame(bottom_panel, fg_color="transparent")
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="news")
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)
    fig_tab_bottom_panel.PAGE_SIZE = 100

    compre_all_btn = ctk.CTkButton(fig_tab_top_panel, text="comprehensive", font=fig_font, width=child_button_size['width'], height=child_button_size['height'],
                fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "all_compre_hap"),
                                 display_all_mh_com_table(fig_tab_bottom_panel, genoclass, dna = True)])
    compre_all_btn.grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
    bottom_panel.child_btn_refs["all_compre_hap"] = compre_all_btn

    sing_all_btn = ctk.CTkButton(fig_tab_top_panel, text="simple", font=fig_font, width=child_button_size['width'], height=child_button_size['height'],
                fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "all_simple_hap"),
                                 display_all_mh_sim_table(fig_tab_bottom_panel, genoclass, dna = True)])
    sing_all_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    bottom_panel.child_btn_refs["all_simple_hap"] = sing_all_btn
    
     # Add a frame to act as the resize handle
    resize_handle = tk.Frame(fig_tab_bottom_panel, cursor="bottom_right_corner", bg="#3b3b3b")
    resize_handle.grid(row=2, column=1, sticky="se", padx=(0, 5), pady=(0, 5))  # Place in the bottom-right corner

    state = {'initial_x': 0, 'initial_y': 0}
    # Bind mouse events to the resize handle
    resize_handle.bind("<ButtonPress-1>", lambda event: start_resize(event, state))  # Start resizing on mouse press
    resize_handle.bind("<B1-Motion>", lambda event: perform_resize(event, state, fig_tab_bottom_panel))  # Perform resizing during mouse drag
    
        # Highlight the first child by default
    highlight_children_button(top_panel, bottom_panel, "all_compre_hap")
    display_all_mh_com_table(fig_tab_bottom_panel, genoclass, dna = True)
    
def create_all_micropep_fig_tbl_panel(top_panel,bottom_panel, genoclass):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    bottom_panel.child_btn_refs.clear()
    for rid in range(bottom_panel.grid_size()[1]):
        bottom_panel.grid_rowconfigure(rid, weight=0)
    for cid in range(bottom_panel.grid_size()[0]):
        bottom_panel.grid_columnconfigure(cid, weight=0)
        
    bottom_panel.grid(row=1, column=0, sticky="news", padx=(2,2), pady=(2,2))
    bottom_panel.grid_rowconfigure(0, weight=0)
    bottom_panel.grid_rowconfigure(1, weight=1)
    bottom_panel.grid_columnconfigure(0, weight=1)
    
    fig_tab_top_panel = ctk.CTkFrame(bottom_panel, fg_color="transparent")
    fig_tab_top_panel.grid(row=0, column=0, sticky='ew')
    
    fig_tab_bottom_panel=ctk.CTkFrame(bottom_panel, fg_color="transparent")
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="news")
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)
    fig_tab_bottom_panel.PAGE_SIZE = 100

    compre_all_btn = ctk.CTkButton(fig_tab_top_panel, text="comprehensive", font=fig_font, width=child_button_size['width'], height=child_button_size['height'],
                fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "all_compre_pep"),
                                 display_all_mh_com_table(fig_tab_bottom_panel, genoclass, dna = False)])
    compre_all_btn.grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
    bottom_panel.child_btn_refs["all_compre_pep"] = compre_all_btn

    sing_all_btn = ctk.CTkButton(fig_tab_top_panel, text="simple", font=fig_font, width=child_button_size['width'], height=child_button_size['height'],
                fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "all_simple_pep"),
                                 display_all_mh_sim_table(fig_tab_bottom_panel, genoclass, dna = False)])
    sing_all_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    bottom_panel.child_btn_refs["all_simple_pep"] = sing_all_btn
    
     # Add a frame to act as the resize handle
    resize_handle = tk.Frame(fig_tab_bottom_panel, cursor="bottom_right_corner", bg="#3b3b3b")
    resize_handle.grid(row=2, column=1, sticky="se", padx=(0, 5), pady=(0, 5))  # Place in the bottom-right corner

    state = {'initial_x': 0, 'initial_y': 0}
    # Bind mouse events to the resize handle
    resize_handle.bind("<ButtonPress-1>", lambda event: start_resize(event, state))  # Start resizing on mouse press
    resize_handle.bind("<B1-Motion>", lambda event: perform_resize(event, state, fig_tab_bottom_panel))  # Perform resizing during mouse drag
    
        # Highlight the first child by default
    highlight_children_button(top_panel, bottom_panel, "all_compre_pep")
    display_all_mh_com_table(fig_tab_bottom_panel, genoclass, dna = False)

def create_microhap_align_panel(top_panel, bottom_panel, genoclass):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    bottom_panel.child_btn_refs.clear()
    for rid in range(bottom_panel.grid_size()[1]):
        bottom_panel.grid_rowconfigure(rid, weight=0)
    for cid in range(bottom_panel.grid_size()[0]):
        bottom_panel.grid_columnconfigure(cid, weight=0)
        
    bottom_panel.grid(row=1, column=0, sticky="news", padx=(2,2), pady=(2,2))
    bottom_panel.grid_rowconfigure(0, weight=0)
    bottom_panel.grid_rowconfigure(1, weight=1)
    bottom_panel.grid_columnconfigure(0, weight=1)
    
    fig_tab_top_panel = ctk.CTkFrame(bottom_panel, fg_color="transparent")
    fig_tab_top_panel.grid(row=0, column=0, sticky="ew")
    fig_tab_top_panel.grid_rowconfigure(0,weight=0)
    
    fig_tab_bottom_panel=ctk.CTkFrame(bottom_panel, fg_color="transparent")
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="news")
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)
    fig_tab_bottom_panel.page_num = 0

    dna_btn = ctk.CTkButton(fig_tab_top_panel, text="DNA", font=fig_font, width=child_button_size['width'], height=child_button_size['height'],
                fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "dna"),
                                 display_align(fig_tab_bottom_panel, genoclass, 'dna')])
    dna_btn.grid(row=0, column=0, padx=(50,5), pady=5, sticky="e")
    bottom_panel.child_btn_refs["dna"] = dna_btn

    pro_btn = ctk.CTkButton(fig_tab_top_panel, text="protien", font=fig_font, width=child_button_size['width'], height=child_button_size['height'],
                fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "protein"),
                                 display_align(fig_tab_bottom_panel, genoclass, 'aa')])
    pro_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    bottom_panel.child_btn_refs["protein"] = pro_btn

    tree_btn = ctk.CTkButton(fig_tab_top_panel, text="phylo tree", font=fig_font, width=child_button_size['width'], height=child_button_size['height'],
                fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                command=lambda: [highlight_children_button(top_panel, bottom_panel, "tree"),
                                 display_phylotre(fig_tab_bottom_panel, genoclass)])
    tree_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    bottom_panel.child_btn_refs["tree"] = tree_btn
 
     # Add a frame to act as the resize handle

    resize_handle = tk.Frame(fig_tab_bottom_panel, cursor="bottom_right_corner", bg="#3b3b3b")
    resize_handle.grid(row=2, column=1, sticky="se", padx=(0, 5), pady=(0, 5))  # Place in the bottom-right corner

    # Bind mouse events to the resize handle
    state = {'initial_x': 0, 'initial_y': 0}
    resize_handle.bind("<ButtonPress-1>", lambda event: start_resize(event, state))  # Start resizing on mouse press
    resize_handle.bind("<B1-Motion>", lambda event: perform_resize(event, state, fig_tab_bottom_panel))  # Perform resizing during mouse drag
    
    highlight_children_button(top_panel, bottom_panel, "dna")
    display_align(fig_tab_bottom_panel, genoclass, 'dna')

def display_align(fig_tab_bottom_panel, genoclass, dna_aa):
    if dna_aa == 'dna':
        genoclass.get_post_microhap().set_dna_or_aa('dna')
        display_dna_seq_align(fig_tab_bottom_panel, genoclass)
    else:
        genoclass.get_post_microhap().set_dna_or_aa('aa')
        display_aa_seq_align(fig_tab_bottom_panel, genoclass)

def start_resize(event, state):
    state['initial_x'], state['initial_y'] = event.x_root, event.y_root

def perform_resize(event, state, panel):
    dx = event.x_root - state['initial_x']
    dy = event.y_root - state['initial_y']
    new_width = panel.winfo_width() + dx
    new_height = panel.winfo_height() + dy
    panel.config(width=new_width, height=new_height)
    state['initial_x'], state['initial_y'] = event.x_root, event.y_root