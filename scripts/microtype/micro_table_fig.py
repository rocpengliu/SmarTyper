import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter as tk
import pandas as pd
from ..utils.common import micro_microhap_df_columns
from ..utils.utils_common import print_time

def update_com_tab(genoclass, fig_tab_bottom_panel):
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
        tree.column(col, anchor=tk.CENTER, stretch=False)
    populate_geno_com_tab(genoclass, tree)
    
    # Auto-adjust column widths based on content
    for col in columns:
        max_width = len(col) * 10  # Header width
        for item in tree.get_children():
            item_text = str(tree.set(item, col))
            text_width = len(item_text) * 8
            max_width = max(max_width, text_width)
        tree.column(col, width=min(max_width + 20, 400))
    print_time(f"finished to update_geno_tab")

def populate_geno_com_tab(genoclass, tree):
    mar = genoclass.get_post_microhap().get_selected_marker()
    loc_ref_dict = genoclass.get_post_microhap().get_loc_ref_dict().get(mar, None)
    if loc_ref_dict is None:
        return
    mar_mh_com_df = pd.concat(loc_ref_dict.get_final_mar_cur_microhap_nested_dict(), ignore_index = True)
    for idx,row in mar_mh_com_df.iterrows():
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

def update_sim_tab(genoclass, fig_tab_bottom_panel):
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
    
    columns = ['Id', 'Sample', 'Marker', 'Allele1', 'Allele2']
    
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

    populate_geno_sim_tab(genoclass, tree)
    
    # Auto-adjust column widths based on content
    for col in columns:
        max_width = len(col) * 10  # Header width
        for item in tree.get_children():
            item_text = str(tree.set(item, col))
            text_width = len(item_text) * 8
            max_width = max(max_width, text_width)
        tree.column(col, width=min(max_width + 20, 400))

    print_time(f"finished to update_geno_tab")

def populate_geno_sim_tab(genoclass, tree):
    mar = genoclass.get_post_microhap().get_selected_marker()
    loc_ref_dict = genoclass.get_post_microhap().get_loc_ref_dict().get(mar, None)
    if loc_ref_dict is None:
        return
    mar_mh_com_df = pd.concat(loc_ref_dict.get_final_mar_cur_sim_microhap_nested_dict(), ignore_index = True)
    mar_mh_com_df.columns=['Sample', 'Allele1', 'Allele2']
    for idx,row in mar_mh_com_df.iterrows():
        tree.insert('','end',
                    values=(str(idx),
                    str(row['Sample']),
                    str(mar),
                    str(row['Allele1']),
                    str(row['Allele2'])
                    ))