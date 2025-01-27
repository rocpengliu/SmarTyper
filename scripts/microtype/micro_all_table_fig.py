import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd
from ..utils.common import micro_microhap_df_columns
from ..utils.utils_common import print_time

def display_all_mh_com_table(genotab, genoclass):
    for widget in genotab.winfo_children():
        widget.destroy()
    for rid in range(genotab.grid_size()[1]):
        genotab.grid_rowconfigure(rid,weight=0)
    for cid in range(genotab.grid_size()[0]):
        genotab.grid_columnconfigure(cid,weight=0)
    # Make genotab expand with the root window
    genotab.grid_rowconfigure(0, weight=1)
    genotab.grid_columnconfigure(0, weight=1)
    genotab.grid(row=1,column=0,sticky="news",padx=5,pady=5)
    
    columns = ['Id']+micro_microhap_df_columns[:-1]
    
    frame = tk.Canvas(genotab, bg="white")
    frame.grid(row=0,column=0,sticky="news",padx=5,pady=5)
    frame.grid_rowconfigure(0,weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    tree=ttk.Treeview(frame,columns=columns,show='headings')
    tree.grid(row=0,column=0,sticky="news",padx=15,pady=15)
    v_scroll=ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
    v_scroll.grid(row=0,column=1,sticky="ns")
    h_scroll=ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
    h_scroll.grid(row=1,column=0,sticky="ew")
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, stretch = False)
    populate_all_mh_com_tab(genoclass,tree)
    frame.bind_all("<Button-4>", lambda event: frame.yview_scroll(-1, "units"))
    frame.bind_all("<Button-5>", lambda event: frame.yview_scroll(1, "units"))

def populate_all_mh_com_tab(genoclass,tree):
    mar_mh = genoclass.get_post_microhap().get_final_microhap_df()
    if mar_mh.shape[0]==0:
        return
    for idx,row in mar_mh.iterrows():
        values_tuple=[idx] + [row.iloc[i] for i in range(len(row))]
        tree.insert('','end', values=tuple(str(value) for value in values_tuple))
def display_all_mh_sim_table(genotab, genoclass):
    for widget in genotab.winfo_children():
        widget.destroy()
    for rid in range(genotab.grid_size()[1]):
        genotab.grid_rowconfigure(rid,weight=0)
    for cid in range(genotab.grid_size()[0]):
        genotab.grid_columnconfigure(cid,weight=0)
    # Make genotab expand with the root window
    genotab.grid_rowconfigure(0, weight=1)
    genotab.grid_columnconfigure(0, weight=1)
    genotab.grid(row=1,column=0,sticky="news",padx=5,pady=5)
    
    columns=['Id'] + genoclass.get_post_microhap().get_final_microhap_df_simple().columns.tolist()
    
    frame = tk.Canvas(genotab, bg="white")
    frame.grid(row=0,column=0,sticky="news",padx=5,pady=5)
    frame.grid_rowconfigure(0,weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    tree=ttk.Treeview(frame,columns=columns,show='headings')
    tree.grid(row=0,column=0,sticky="news",padx=15,pady=15)
    v_scroll=ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
    v_scroll.grid(row=0,column=1,sticky="ns")
    h_scroll=ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
    h_scroll.grid(row=1,column=0,sticky="ew")
    
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, stretch = False)
    populate_all_mh_sim_tab(genoclass,tree)
    frame.bind_all("<Button-4>", lambda event: frame.yview_scroll(-1, "units"))
    frame.bind_all("<Button-5>", lambda event: frame.yview_scroll(1, "units"))
    
def populate_all_mh_sim_tab(genoclass,tree):
    mar_mh = genoclass.get_post_microhap().get_final_microhap_df_simple()
    if mar_mh.shape[0]==0:
        return
    for idx,row in mar_mh.iterrows():
        values_tuple=[idx] + [row.iloc[i] for i in range(len(row))]
        tree.insert('','end', values=tuple(str(value) for value in values_tuple))