import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd
from ..utils.common import micro_microhap_df_columns
from ..utils.utils_common import print_time

def update_geno_tab(parent, fig_tab_bottom_panel):
    print_time("starting to update_geno_tab")
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

    populate_geno_tab(parent, tree)
        
    frame.bind_all("<Button-4>", lambda event: frame.yview_scroll(-1, "units"))
    frame.bind_all("<Button-5>", lambda event: frame.yview_scroll(1, "units"))
    print_time("finished to update_geno_tab")

def populate_geno_tab(parent, tree):
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
    
    max_widths = [max([len(str(cell)) for cell in sam_mar_df[col]]) for col in sam_mar_df.columns]
    for col, width in zip(tree['columns'], max_widths):
        tree.column(col, anchor=tk.CENTER, stretch=False)
        
    for idx,row in sam_mar_df.iterrows():
        tree.insert('','end',
                    values=(str(idx),
                    str(row['Sample']),
                    str(row['Locus']),
                    str(row['Allele']),
                    row['BaseChange'],
                    str(row['NumReads']),
                    str(row['AlleleReadsPer']),
                    str(row['VarRatio']),
                    str(row['TotalReads']),
                    str(row['ReadsPer']),
                    row['Conclusive'],
                    row['Zygosity'],
                    row['Indel'],
                    row['Sequence']
                    ))