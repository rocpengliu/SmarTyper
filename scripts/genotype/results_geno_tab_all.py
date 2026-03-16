import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd
from ..utils.common import micro_microhap_df_columns

def update_geno_tab_all(parent, bottom_panel):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    
    top_panel = parent.master.pages['results'].body_frame.top_panel
    top_panel.button_child_refs.clear()
    # Configure bottom_panel to expand
    for rid in range(bottom_panel.grid_size()[1]):
        bottom_panel.grid_rowconfigure(rid,weight=0)
    for cid in range(bottom_panel.grid_size()[0]):
        bottom_panel.grid_columnconfigure(cid,weight=0)
    
    bottom_panel.grid(row=1, column=0, sticky="nsew", padx=(0,0), pady=(0,0))
    bottom_panel.grid_rowconfigure(0, weight=1)
    bottom_panel.grid_columnconfigure(0, weight=1)
    
    columns = ['Id']+micro_microhap_df_columns[:-1]
    
    # Create a frame to contain the Treeview and Scrollbars
    frame = ctk.CTkFrame(bottom_panel, fg_color="white")
    frame.grid(row=0,column=0,sticky="news",padx=10,pady=10)
    # Update the grid weights
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    # Create Treeview
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    tree.grid(row=0,column=0,sticky="news",padx=10,pady=10)
    
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

def populate_geno_tab(parent, tree):
    # Clear existing items first
    for item in tree.get_children():
        tree.delete(item)
    
    genoclass = parent.master.genotype_class
    samples=genoclass.get_metadata().get_samples_list()
    markers=genoclass.get_metadata().get_ref_markers_list()
    if len(samples) == 0 or len(markers) == 0:
        return
    
    # For "All Sample Geno", show ALL samples and ALL markers regardless of filter
    dfs=[]
    for sam in samples:
        for mar in markers:
            df = genoclass.get_microhap().get_sam_microhaps_dir().get(sam).get(mar)
            if df is not None and not df.empty:
                dfs.append(df)
    
    if len(dfs) == 0:
        return
    
    sam_df = pd.concat(dfs, ignore_index=True)
    
    # First insert all data
    for idx,row in sam_df.iterrows():
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
        header_width = len(str(col)) * 12 + 40  # Extra space for header
        
        # Get max content width from all rows
        max_content_width = 0
        for item in tree.get_children():
            item_text = str(tree.set(item, col))
            text_width = len(item_text) * 8 + 20
            max_content_width = max(max_content_width, text_width)
        
        # Use the larger of header width or content width, capped at 500px
        final_width = min(max(header_width, max_content_width), 500)
        tree.column(col, anchor=tk.CENTER, width=final_width, minwidth=header_width, stretch=False)