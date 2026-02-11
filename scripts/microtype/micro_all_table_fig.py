import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, font
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
    
    columns = ['Id']+[str(col) for col in micro_microhap_df_columns[:-1]]
    
    frame = tk.Frame(genotab, bg="white")
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
    
    tree_font = font.nametofont("TkHeadingFont")
    for col in columns:
        text_width = tree_font.measure(col) + 20
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, stretch = False, width=text_width)
    tree.column(columns[-1], stretch=True)
    tree['displaycolumns'] = columns  # Ensure all columns are displayed
    tree.update_idletasks()  # Update to get correct column widths
    populate_all_mh_com_tab(genoclass,tree)
    
    # Auto-adjust column widths based on content
    # for col in columns:
    #     max_width = len(col) * 10  # Header width
    #     for item in tree.get_children():
    #         item_text = str(tree.set(item, col))
    #         text_width = tree_font.measure(item_text) + 20
    #         max_width = max(max_width, text_width)
    #     tree.column(col, width=min(max_width + 20, 400))

def populate_all_mh_com_tab(genoclass,tree):
    mar_mh = genoclass.get_post_microhap().get_final_microhap_df()
    if mar_mh.shape[0]==0:
        return
    for idx,row in mar_mh.iterrows():
        values_tuple=[idx] + [str(row.iloc[i]) for i in range(len(row))]
        tree.insert('','end', values=tuple(str(value) for value in values_tuple))


def display_all_mh_sim_table(genotab, genoclass, start_col=0):
    for widget in genotab.winfo_children():
        widget.destroy()

    mh_df = genoclass.get_post_microhap().get_final_microhap_df_simple()

    all_columns = ['Id'] + [str(col) for col in mh_df.columns]
    data_columns = all_columns[1:]


    # Ensure PAGE_SIZE is never zero
    raw_page_size = getattr(genotab, 'PAGE_SIZE', 100) if hasattr(genotab, 'PAGE_SIZE') else 100
    PAGE_SIZE = raw_page_size if raw_page_size else 100
    if PAGE_SIZE == 0:
        PAGE_SIZE = 100

    total_pages = max(1, (len(data_columns) - 1) // PAGE_SIZE + 1)
    max_start = max(0, len(data_columns) - PAGE_SIZE)

    start_col = max(0, min(start_col, max_start))
    end_col = start_col + PAGE_SIZE

    visible_data_cols = data_columns[start_col:end_col]
    visible_columns = ['Id'] + visible_data_cols

    frame = ttk.Frame(genotab)
    frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    if total_pages > 1:
        number_of_steps = total_pages - 1
        slider = ctk.CTkSlider(
            frame,
            from_=0,
            to=total_pages - 1,
            number_of_steps=number_of_steps,
            command=lambda v: display_all_mh_sim_table(genotab, genoclass, int(v) * PAGE_SIZE)
        )
        slider.set(start_col // PAGE_SIZE)
        slider.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
    else:
        # Only one page, no need for slider
        pass

    tree_frame = ttk.Frame(frame)
    tree_frame.grid(row=1, column=0, sticky="news")
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(tree_frame, columns=visible_columns, show='headings')
    tree.grid(row=0, column=0, sticky="news")

    v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    v_scroll.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=v_scroll.set)

    h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    h_scroll.grid(row=1, column=0, sticky="ew")
    tree.configure(xscrollcommand=h_scroll.set)

    for col in visible_columns:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER, width=160, stretch=False)

    for idx, row in mh_df.iterrows():
        values = [idx] + [str(row[col]) for col in visible_data_cols]
        tree.insert('', 'end', values=values)

    page = start_col // PAGE_SIZE + 1

    ttk.Label(
        frame,
        text=f"Markers {start_col + 1}–{min(end_col, len(data_columns))} "
             f"of {len(data_columns)} (Page {page}/{total_pages})"
    ).grid(row=2, column=0, pady=5)


    # tree=ttk.Treeview(frame,columns=columns,show='headings')
    # tree.grid(row=0,column=0,sticky="news",padx=15,pady=15)
    # v_scroll=ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
    # v_scroll.grid(row=0,column=1,sticky="ns")
    # h_scroll=ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
    # h_scroll.grid(row=1,column=0,sticky="ew")
    
    # tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    # tree_font = font.nametofont("TkHeadingFont")
    # MAX_COL_WIDTH = 200
    # for col in columns:
    #     text_width = min(tree_font.measure(col) + 20, MAX_COL_WIDTH)
    #     tree.heading(col, text=col)
    #     tree.column(col, anchor=tk.CENTER, stretch = False, width=text_width)
    # tree.column(columns[-1], stretch=True)
    # tree['displaycolumns'] = columns  # Ensure all columns are displayed
    # tree.update_idletasks()  # Update to get correct column widths

    #populate_all_mh_sim_tab(mh_df,tree)
 
    # Set column width based on max header/content length
    # for col in columns:
    #     max_width = len(col) * 10  # Header width
    #     for item in tree.get_children():
    #         item_text = str(tree.set(item, col))
    #         text_width = len(item_text) * 8
    #         max_width = max(max_width, text_width)
    #     # Cap width to avoid excessive size
    #     tree.column(col, width=min(max_width + 20, 300), minwidth=60, stretch=False)
    #tree.update_idletasks()
    
# def populate_all_mh_sim_tab(mh_df,tree):
#     if mh_df.shape[0]==0:
#         return
#     for idx,row in mh_df.iterrows():
#         values_tuple=[idx] + [str(row.iloc[i]) for i in range(len(row))]
#         tree.insert('','end', values=tuple(str(value) for value in values_tuple))