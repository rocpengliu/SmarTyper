import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import logomaker
from ..utils.utils_common import print_time
from ..utils.common import child_button_size, bmbfont
from ..utils.colors import COLORS
import pdb
import copy
import os
import pandas as pd
from Bio import Phylo

matplotlib.use("TkAgg")

def display_phylotre(genotab, genoclass):
    mar = genoclass.get_post_microhap().get_selected_marker()
    if mar == "":
        return
    ref_mar_refmt = genoclass.get_post_microhap().get_loc_ref_dict().get(mar, None)
    if ref_mar_refmt is None:
        return

    genotab.tot_pages = len(ref_mar_refmt.get_children_microtype_dict())
    if 'splicer' in ref_mar_refmt.get_children_microtype_dict():
        genotab.tot_pages -= 1 # must remove the splicer page,
    if genotab.page_num < 0:
        genotab.page_num = 0
        return
    elif genotab.page_num >= genotab.tot_pages:
        genotab.page_num = genotab.tot_pages -1
        return
    
    cur_compre_mt = ref_mar_refmt.get_children_microtype_dict().get(f"splicer_{genotab.page_num}", None)#CompreMicrotypeClass
    if cur_compre_mt is None:
        return
    title_label = cur_compre_mt.get_label(False)
    if ref_mar_refmt.get_has_splicer():
        dna_working_splicer_ref_compre = ref_mar_refmt.get_children_microtype_dict().get("splicer", None)
        if dna_working_splicer_ref_compre is None:
            return
        if ref_mar_refmt.is_overlapped_gene():
            aa_working_splicer_ref_compre = ref_mar_refmt.get_children_microtype_dict().get(f"splicer_{genotab.page_num}", None)
        else:
            aa_working_splicer_ref_compre = ref_mar_refmt.get_children_microtype_dict().get("splicer_0", None)
        if aa_working_splicer_ref_compre is None:
            return
    else:
        dna_working_splicer_ref_compre = ref_mar_refmt.get_children_microtype_dict().get("splicer_0", None)
        aa_working_splicer_ref_compre = None
        if dna_working_splicer_ref_compre is None:
            return

    for widget in genotab.winfo_children():
        widget.destroy()
    for rid in range(genotab.grid_size()[1]):
        genotab.grid_rowconfigure(rid,weight=0)
    for cid in range(genotab.grid_size()[0]):
        genotab.grid_columnconfigure(cid,weight=0)
    # Make genotab expand with the root window
    genotab.grid_rowconfigure(0, weight=1)
    genotab.grid_rowconfigure(1,weight=0)
    genotab.grid_columnconfigure(0, weight=1)

    # Canvas
    canvas = tk.Canvas(genotab, bg='white')
    canvas.grid(row=0, column=0, sticky="news")

    # Scrollbars
    v_scrollbar = ttk.Scrollbar(genotab, orient="vertical", command=canvas.yview)
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=v_scrollbar.set)

    h_scrollbar = ttk.Scrollbar(genotab, orient="horizontal", command=canvas.xview)
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    canvas.configure(xscrollcommand=h_scrollbar.set)

    # Scrollable frame
    scroll_frame = ctk.CTkFrame(canvas, fg_color="white")  # Initial size
    scroll_frame.grid(row=0, column=0, sticky="news", padx = 2, pady= 2)
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="inner_frame")

    # Configure weights for the scroll_frame's grid to make contents expand
    scroll_frame.grid_rowconfigure(0, weight=1)
    scroll_frame.grid_rowconfigure(1, weight=1)
    scroll_frame.grid_columnconfigure(0, weight=1)

    fig_frame = ctk.CTkFrame(scroll_frame, fg_color='white')
    fig_frame.grid_rowconfigure(0,weight=1)
    fig_frame.grid_columnconfigure(0,weight=1)
    fig_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(2,2))
    create_phy_fig(title_label, ref_mar_refmt, dna_working_splicer_ref_compre, aa_working_splicer_ref_compre, fig_frame, genoclass)
    
    page_flip_frame=ctk.CTkFrame(genotab, fg_color='transparent')
    page_flip_frame.grid(row=2,column=0, pady=(5,5), sticky='ew')
    
    genotab.previous_page_button = ctk.CTkButton(page_flip_frame, text="← Previous", font=bmbfont,
                                         width=child_button_size['width'], height=child_button_size['height'],
                                         fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                                         corner_radius=10,
                                         command=lambda:change_page(-1, genotab, genoclass))
    genotab.previous_page_button.grid(row=0,column=0,sticky="e",padx=(100,0), pady=(5,5))
    #previous_page_button.pack(side="left", padx=(10, 50), pady=(5,5))
    genotab.next_page_button = ctk.CTkButton(page_flip_frame, text="Next →", font=bmbfont,
                                     width=child_button_size['width'], height=child_button_size['height'],
                                     fg_color=COLORS['accent'], hover_color=COLORS['secondary'],
                                     corner_radius=10,
                                     command=lambda:change_page(1, genotab, genoclass))
    genotab.next_page_button.grid(row=0,column=1, sticky='e', padx=(200, 0), pady=(2,2))
    
    # Ensure scroll_frame expands and fills the canvas upon resize
    canvas.bind("<Configure>", lambda event: on_canvas_configure(canvas, event))
    canvas.bind_all("<MouseWheel>", lambda event: on_mouse_wheel(event, canvas))
    canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

def on_canvas_configure(canvas, event):
    """Reset the scroll region to encompass the inner frame and resize inner frame"""
    canvas_width = event.width
    canvas_height = event.height
    canvas.itemconfig('inner_frame', width=canvas_width, height=canvas_height)
    canvas.configure(scrollregion=canvas.bbox("all"))

def on_mouse_wheel(event, canvas):
    """Scroll the canvas based on mouse wheel movement."""
    if event.delta > 0:
        canvas.yview_scroll(-1, "units")
    else:
        canvas.yview_scroll(1, "units")

def change_page(page, genotab, genoclass, change = True):
    genotab.page_num += page
    if genotab.page_num <= 0:
        genotab.previous_page_button.configure(state='disabled')
        if genotab.tot_pages == 1:
            genotab.next_page_button.configure(state='disabled')
        else:
            genotab.next_page_button.configure(state='normal')
    elif genotab.page_num >= (genotab.tot_pages -1):
        genotab.next_page_button.configure(state='disabled')
        if genotab.tot_pages == 1:
            genotab.previous_page_button.configure(state='disabled')
        else:
            genotab.previous_page_button.configure(state='normal')
    else:
        genotab.previous_page_button.configure(state='normal')
        genotab.next_page_button.configure(state='normal')
    if change:
        display_phylotre(genotab, genoclass)

def create_phy_fig(title_label, ref_mar_refmt, dna_working_splicer_ref_compre, aa_working_splicer_ref_compre, fig_frame, genoclass):
    if ref_mar_refmt.get_has_splicer():
        fig, (ax1, ax2)=plt.subplots(1, 2, figsize=(20, 10))
        Phylo.draw(dna_working_splicer_ref_compre.get_dna_tre(), do_show=False, axes = ax1)
        ax1.set_title("DNA tree")
        ax1.set_ylabel("microtype")
        Phylo.draw(aa_working_splicer_ref_compre.get_aa_tre(), do_show=False, axes = ax2)
        ax2.set_title("AA tree")
        ax2.set_ylabel("microtype")
        fig.suptitle(f"Phylogenetic Trees {title_label}", fontsize=16)
    else:
        fig, (ax1)=plt.subplots(1,figsize=(15, 10))
        Phylo.draw(dna_working_splicer_ref_compre.get_dna_tre(), do_show=False, axes = ax1)
        ax1.set_title("DNA tree")
        ax1.set_ylabel("microtype")
        fig.suptitle(f"Phylogenetic Tree {title_label}", fontsize=16)
    plt.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1)
    fig_canvas = FigureCanvasTkAgg(fig, master=fig_frame)
    fig_canvas.draw()
    fig_widget = fig_canvas.get_tk_widget()
    fig_widget.grid(row=0, column=0, sticky="nsew", padx=(10,10), pady=(10,10))  # Ensure full expansion with padding
    plt.close(fig)