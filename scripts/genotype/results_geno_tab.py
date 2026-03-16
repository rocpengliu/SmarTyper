import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd
from ..utils.common import micro_microhap_df_columns
from ..utils.utils_common import print_time

def update_geno_tab(parent, fig_tab_bottom_panel):
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
    
    columns = ['Id']+micro_microhap_df_columns[:-1]
    
    # Create a frame to contain the Treeview and Scrollbars
    frame = ctk.CTkFrame(fig_tab_bottom_panel, fg_color="white", height=144)
    frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=10)  # Expand in all directions
    frame.grid_propagate(False)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    # Create Treeview
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=5)
    tree.grid(row=0, column=0, sticky="nsew", padx=0, pady=10)  # Expand in all directions
    
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

    populate_geno_tab(parent, tree)
    print_time(f"finished to update_geno_tab")

def populate_geno_tab(parent, tree):
    # Clear existing items first
    for item in tree.get_children():
        tree.delete(item)
    
    genoclass = parent.master.genotype_class
    sam_mar_df = pd.DataFrame()
    if genoclass.get_res_param().get_res_type() == "sample":
        sample = genoclass.get_res_param().get_sample()
        if not sample:
            return
        sam_mar_df = pd.concat(genoclass.get_microhap().get_sam_microhaps_dir().get(sample).values(), ignore_index=True)
    elif genoclass.get_res_param().get_res_type() == "marker":
        marker = genoclass.get_res_param().get_marker()
        if not marker:
            return
        samples = genoclass.get_metadata().get_samples_list()
        mar_dict={}
        for sam in samples:
            mar_dict[sam]=genoclass.get_microhap().get_sam_microhaps_dir().get(sam).get(marker)
        sam_mar_df = pd.concat(mar_dict.values(), ignore_index=True)
    else:
        return
    
    # First insert all data
    for idx,row in sam_mar_df.iterrows():
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
                    str(row['seq'])))
    
    # Then calculate and set column widths based on all inserted data
    for col in tree['columns']:
        # Calculate header width with generous padding
        header_width = len(str(col)) * 12 + 50  # Extra space for header
        
        # Get max content width from all rows
        max_content_width = 0
        for item in tree.get_children():
            item_text = str(tree.set(item, col))
            text_width = len(item_text) * 8 + 20
            max_content_width = max(max_content_width, text_width)
        
        # Use the larger of header width or content width, capped at 1400px for a much wider table
        final_width = min(max(header_width, max_content_width), 1400)
        tree.column(col, anchor=tk.CENTER, width=final_width, minwidth=header_width, stretch=False)
    
    # Force update to apply column widths
    tree.update_idletasks()