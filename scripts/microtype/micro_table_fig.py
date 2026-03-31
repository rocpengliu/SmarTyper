import os

import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter as tk
import pandas as pd
from ..utils.common import micro_microhap_df_columns, micro_micropep_df_columns
from ..utils.utils_common import print_time
from ..utils.utils_func import load_pdf
from ..utils.mouse import _on_mousewheel

def update_com_tab(genoclass, fig_tab_bottom_panel, dna=True):
    print_time(f"starting to update_com_tab")
    for widget in fig_tab_bottom_panel.winfo_children():
        widget.destroy()

    for rid in range(fig_tab_bottom_panel.grid_size()[1]):
        fig_tab_bottom_panel.grid_rowconfigure(rid,weight=0)
    for cid in range(fig_tab_bottom_panel.grid_size()[0]):
        fig_tab_bottom_panel.grid_columnconfigure(cid,weight=0)
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)  # Ensure both horizontal and vertical expansion
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)  # Ensure vertical expansion
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)  # Ensure horizontal expansion

    columns = ['id']+(micro_microhap_df_columns[:-1] if dna else micro_micropep_df_columns[:-1])

    # Create a frame to contain the Treeview and Scrollbars
    frame = tk.Canvas(fig_tab_bottom_panel, bg="white")
    frame.grid(row=0,column=0,sticky="news",padx=5,pady=5)
    # Update the grid weights
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    # Create Treeview
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    tree.grid(row=0,column=0,sticky="news",padx=15,pady=15)
    
    # Create Scrollbars
    v_scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    v_scroll.grid(row=0,column=1,sticky="ns")
    
    h_scroll = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    h_scroll.grid(row=1,column=0,sticky="ew")
    
    # Configure Treeview to use the scrollbars
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    # Define column headings and widths
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, stretch=True)
    populate_geno_com_tab(genoclass, tree, dna)
    
    # Auto-adjust column widths based on content
    for col in columns:
        max_width = len(col) * 10  # Header width
        for item in tree.get_children():
            item_text = str(tree.set(item, col))
            text_width = len(item_text) * 8
            max_width = max(max_width, text_width)
        tree.column(col, width=max_width + 20)
    print_time(f"finished to update_geno_tab")

def populate_geno_com_tab(genoclass, tree, dna=True):
    mar = genoclass.get_post_microhap().get_selected_marker()
    loc_ref_dict = genoclass.get_post_microhap().get_loc_ref_dict().get(mar, None)
    if loc_ref_dict is None:
        return
    if not dna and not loc_ref_dict.get_has_exon():
        return
    mar_mh_com_df = pd.concat(loc_ref_dict.get_final_mar_cur_microhap_nested_dict() if dna else loc_ref_dict.get_final_mar_cur_micropep_nested_dict(), ignore_index = True)
    if mar_mh_com_df.empty:
        return
    for idx,row in mar_mh_com_df.iterrows():
        if dna:
            tree.insert('','end',
                        values=(str(idx),
                        str(row['sample']),
                        str(row['locus']),
                        str(row['allele']),
                        str(row['readt']),
                        str(row['read']),
                        str(row['rprop']),
                        str(row['mprop']),
                        str(row['sprop']),
                        str(row['mut']),
                        str(row['indel']),
                        str(row['zygosity']),
                        str(row['baseChange']),
                        str(row['mh_seq'])
                        ))
        else:
            tree.insert('','end',
                    values=(str(idx),
                    str(row['sample']),
                    str(row['locus']),
                    str(row['allele']),
                    str(row['readt']),
                    str(row['read']),
                    str(row['rprop']),
                    str(row['mprop']),
                    str(row['zygosity']),
                    str(row['baseChange']),
                    str(row['mp_seq'])
                    ))

def update_sim_tab(genoclass, fig_tab_bottom_panel, dna = True):
    print_time(f"starting to update_geno_tab")
    for widget in fig_tab_bottom_panel.winfo_children():
        widget.destroy()
    
    for rid in range(fig_tab_bottom_panel.grid_size()[1]):
        fig_tab_bottom_panel.grid_rowconfigure(rid,weight=0)
    for cid in range(fig_tab_bottom_panel.grid_size()[0]):
        fig_tab_bottom_panel.grid_columnconfigure(cid,weight=0)
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)  # Ensure both horizontal and vertical expansion
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)  # Ensure vertical expansion
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)  # Ensure horizontal expansion
    
    columns = ['id', 'sample', 'locus', 'allele1', 'allele2']
    
    # Create a frame to contain the Treeview and Scrollbars
    frame = tk.Canvas(fig_tab_bottom_panel, bg="white")
    frame.grid(row=0,column=0,sticky="news",padx=5,pady=5)
    # Update the grid weights
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    # Create Treeview
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    tree.grid(row=0,column=0,sticky="news",padx=15,pady=15)
    
    # Create Scrollbars
    v_scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    v_scroll.grid(row=0,column=1,sticky="ns")
    
    h_scroll = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    h_scroll.grid(row=1,column=0,sticky="ew")
    
    # Configure Treeview to use the scrollbars
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    
    # Define column headings and widths
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, stretch=False)

    populate_geno_sim_tab(genoclass, tree, dna)
    
    # Auto-adjust column widths based on content
    for col in columns:
        max_width = len(col) * 10  # Header width
        for item in tree.get_children():
            item_text = str(tree.set(item, col))
            text_width = len(item_text) * 8
            max_width = max(max_width, text_width)
        tree.column(col, width=max_width + 20)

    print_time(f"finished to update_geno_tab")

def populate_geno_sim_tab(genoclass, tree, dna=True):
    mar = genoclass.get_post_microhap().get_selected_marker()
    loc_ref_dict = genoclass.get_post_microhap().get_loc_ref_dict().get(mar, None)
    if loc_ref_dict is None:
        return
    if not dna and not loc_ref_dict.get_has_exon():
        return
    mar_mh_com_df = pd.concat(loc_ref_dict.get_final_mar_cur_sim_microhap_nested_dict() if dna else loc_ref_dict.get_final_mar_cur_sim_micropep_nested_dict(), ignore_index = True)
    if mar_mh_com_df.empty:
        return
    mar_mh_com_df.columns=['sample', 'allele1', 'allele2']
    for idx,row in mar_mh_com_df.iterrows():
        tree.insert('','end',
                    values=(str(idx),
                    str(row['sample']),
                    str(mar),
                    str(row['allele1']),
                    str(row['allele2'])
                    ))

def update_sim_fig(fig_tab_bottom_panel, genoclass, dna=True):
    print_time(f"starting to update_sim_fig")
    for widget in fig_tab_bottom_panel.winfo_children():
        widget.destroy()
    
    for rid in range(fig_tab_bottom_panel.grid_size()[1]):
        fig_tab_bottom_panel.grid_rowconfigure(rid,weight=0)
    for cid in range(fig_tab_bottom_panel.grid_size()[0]):
        fig_tab_bottom_panel.grid_columnconfigure(cid,weight=0)
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)  # Ensure both horizontal and vertical expansion
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)  # Ensure vertical expansion
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)  # Ensure horizontal expansion
    
    # Create a container frame for the canvas
    container = ctk.CTkFrame(fig_tab_bottom_panel, fg_color="transparent")
    container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    
    # Create a canvas widget
    canvas = tk.Canvas(container, bg="white")
    canvas.grid(row=0, column=0, sticky="nsew")

    # Create scrollbars
    v_scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)

    # Place scrollbars
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    # Configure canvas scrollbars
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    # Bind mouse wheel and keyboard events for scrolling (only when mouse is over the canvas)
        # Linux uses Button-4 and Button-5, Windows/Mac use MouseWheel
    canvas.bind('<MouseWheel>', lambda event: _on_mousewheel(canvas, event))  # Windows/Mac
    canvas.bind('<Button-4>', lambda event: _on_mousewheel(canvas, event))    # Linux scroll up
    canvas.bind('<Button-5>', lambda event: _on_mousewheel(canvas, event))    # Linux scroll down

    # Optionally, bind up/down keys
    def _on_arrow(event):
        if hasattr(canvas, 'yview_scroll'):
            if event.keysym == 'Down':
                canvas.yview_scroll(1, "units")
            elif event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
    canvas.bind('<Down>', _on_arrow)
    canvas.bind('<Up>', _on_arrow)

    # Load the PDF into the canvas
    marker = genoclass.get_post_microhap().get_selected_marker()
    pdf_file_path = os.path.join(genoclass.get_parameter().get_post_microhap_output_dir(), f"{marker}_locus_{'microhap' if dna else 'micropep'}_genotype.pdf") 
    if os.path.exists(pdf_file_path):
        load_pdf(pdf_file_path, canvas)
    
    print_time(f"finished to update_sim_fig")
    