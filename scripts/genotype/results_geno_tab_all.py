import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd
from ..utils.common import micro_microhap_df_columns

def update_geno_tab_all(parent, bottom_panel):
    for widget in bottom_panel.winfo_children():
        widget.destroy()
    
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
    frame = tk.Canvas(bottom_panel)
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
    frame.bind_all("<Button-4>", lambda event: frame.yview_scroll(-1, "units"))
    frame.bind_all("<Button-5>", lambda event: frame.yview_scroll(1, "units"))

def populate_geno_tab(parent, tree):
    genoclass = parent.master.genotype_class
    samples=genoclass.get_metadata().get_samples_list()
    markers=genoclass.get_metadata().get_ref_markers_list()
    if len(samples) == len(markers) == 0:
        return
    dfs=[]
    if genoclass.get_res_param().get_res_type() == "sample":
        dfs=[pd.concat(genoclass.get_microhap().get_sam_microhaps_dir().get(sample).values(), ignore_index=True) for sample in genoclass.get_microhap().get_sam_microhaps_dir()]
    elif genoclass.get_res_param().get_res_type() == "marker":
        for mar in markers:
            for sam in samples:
                dfs.append(genoclass.get_microhap().get_sam_microhaps_dir().get(sam).get(mar))
    else:
        return

    sam_df = pd.concat(dfs, ignore_index=True)
        # Calculate the maximum content width for each column
    max_widths = [max([len(str(cell)) for cell in sam_df[col]]) for col in sam_df.columns]
    for col, width in zip(tree['columns'], max_widths):
        tree.column(col, anchor=tk.CENTER, stretch=False)

    for idx,row in sam_df.iterrows():
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