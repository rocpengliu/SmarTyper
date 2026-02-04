import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import re
import pandas as pd
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ..utils import modern_messagebox
from itertools import repeat
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import traceback
from ..utils.common import color_bars, child_button_size, bmbfont, fig_font, seq_font
from ..utils.utils_common import matplotlib_lock, print_time
from ..utils.colors import COLORS

matplotlib.use("Agg")

def update_genotype_tab(parent, genotab):
    print_time(f"Starting genotype tab update...")
    genoclass = parent.master.genotype_class
    if len(genoclass.get_microhap().get_assigned_reads_dict())==0:
        print_time(f"No assigned reads found, skipping genotype tab update.")
        return
    genotab.n_rows=5
    figures = []
    seq_tables = []
    hap_tables = []
    genotab.s_table_list = {}
    genotab.sam_mar_option=genoclass.get_res_param().get_res_type()
    print_time(f'Result type: {genotab.sam_mar_option}')
    if genoclass.get_res_param().get_res_type() == "sample":
        markers = genoclass.get_metadata().get_ref_markers_list()
        selected_sample = genoclass.get_res_param().get_sample()
        print_time(f"selected sample: {selected_sample}, markers: {len(markers)}")
        if not selected_sample or len(markers)==0:
            return
        print_time(f'selected sample: {selected_sample}')
        for mar in markers:
            try:
                amplicon_df = genoclass.get_microhap().get_sam_amplicons_dir().get(f'{selected_sample}').get(f'{mar}')
                hap_df = genoclass.get_microhap().get_sam_microhaps_dir().get(f'{selected_sample}').get(f'{mar}')
                if amplicon_df is not None and not amplicon_df.empty:
                    fig = create_figure(selected_sample, mar, amplicon_df, hap_df, genotab, genoclass)
                    figures.append(fig)
                    seq_tables.append(amplicon_df.head(genotab.n_rows))
                    if hap_df.empty:
                        hap_tables.append(None)
                    else:
                        hap_tables.append(hap_df)
            except ValueError as e:
                modern_messagebox.showerror(None, "Invalid Input", str(e))
    elif genoclass.get_res_param().get_res_type() == "marker":
        selected_marker=genoclass.get_res_param().get_marker()
        samples = genoclass.get_metadata().get_samples_list()
        if not selected_marker or len(samples)==0:
            return
        print_time(f'selected marker: {selected_marker}')
        for sam in samples:
            try:
                amplicon_df = genoclass.get_microhap().get_sam_amplicons_dir().get(f'{sam}').get(f'{selected_marker}')
                hap_df = genoclass.get_microhap().get_sam_microhaps_dir().get(f'{sam}').get(f'{selected_marker}')
                if amplicon_df is not None and not amplicon_df.empty:
                    fig = create_figure(sam, selected_marker, amplicon_df, hap_df, genotab, genoclass)
                    figures.append(fig)
                    seq_tables.append(amplicon_df.head(genotab.n_rows))
                    if hap_df.empty:
                        hap_tables.append(None)
                    else:
                        hap_tables.append(hap_df)
            except ValueError as e:
                modern_messagebox.showerror(None, "Invalid Input", str(e))
    else:
        return
    print_time(f"Figures length: {len(figures)}")
    genotab.figures = figures
    genotab.current_page = 0
    genotab.fig_per_page = 10
    genotab.tot_pages=int(len(genotab.figures) / genotab.fig_per_page) if (len(genotab.figures) % genotab.fig_per_page == 0) else (int(len(genotab.figures) / genotab.fig_per_page) + 1)
    genotab.seq_tables = seq_tables
    genotab.hap_tables = hap_tables
    if len(genotab.seq_tables) != len(genotab.hap_tables):
        print_time(f"Sequence tables and haplotype tables length mismatch, cannot update genotype tab.")
        return
    print_time(f'Finished processing all figures and tables, displaying genotype tab page...')
    display_page(genotab, genoclass)   
    
def display_page(genotab, genoclass):
    loci_table = genoclass.get_metadata().get_loc_df()
    if loci_table.shape[0] == 0:
        return
    # Clear existing widgets
    for widget in genotab.winfo_children():
        widget.destroy()
    
    for rid in range(genotab.grid_size()[1]):
        genotab.grid_rowconfigure(rid,weight=0)
    for cid in range(genotab.grid_size()[0]):
        genotab.grid_columnconfigure(cid,weight=0)
    # Configure grid weights for genotab
    genotab.grid(row=1, column=0, sticky="nsew", padx=(5,5), pady=(5,5))
    genotab.grid_rowconfigure(0, weight=1)
    genotab.grid_rowconfigure(1, weight=0)
    genotab.grid_columnconfigure(0, weight=1)
    
    # Set up the container with grid layout for better control
    container = ctk.CTkFrame(genotab, fg_color="transparent")
    container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    container.grid_rowconfigure(0, weight=1)  # Canvas row (body) should expand
    container.grid_columnconfigure(0, weight=1)  # Canvas column should expand
    
    # Create canvas and scrollbars
    canvas = tk.Canvas(container, bg="white")
    v_scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)

    # Place the canvas and scrollbars in the grid
    canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    # Create a frame inside the canvas to hold the figures
    figures_frame = ctk.CTkFrame(canvas, fg_color="white")
    canvas.create_window((0, 0), window=figures_frame, anchor='nw')

    # Ensure canvas updates scrollregion when figures_frame size changes
    figures_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    # Configure figures_frame layout
    figures_frame.grid_columnconfigure(0, weight=1)  # Column for figure expands
    #figures_frame.grid_columnconfigure(1, weight=1)  # Column for table
    #figures_frame.grid_columnconfigure(2, weight=1)  # Column for table
    figures_frame.grid_rowconfigure(0, weight=1)  # Row for figure expands
    figures_frame.grid_rowconfigure(1, weight=1)  # Row for table
    figures_frame.grid_rowconfigure(2, weight=1)  # Row for sequence widget

    # Add figures and tables to the figures_frame
    
    start_index = genotab.current_page * genotab.fig_per_page
    end_index = min(start_index + genotab.fig_per_page, len(genotab.figures))
    
    create_fig_tab_combo(canvas, genotab, start_index, end_index, figures_frame, loci_table, genoclass)
    # Update the scroll region of the canvas to fit the figures_frame
    canvas.configure(scrollregion=canvas.bbox("all"))

    # Create page navigation buttons at the bottom
    page_flip_frame = ctk.CTkFrame(genotab, fg_color="transparent")
    page_flip_frame.grid(row=1, column=0, pady=(5, 5), sticky="ew")
    page_flip_frame.grid_columnconfigure(0, weight=1)
    page_flip_frame.grid_columnconfigure(1, weight=0)
    page_flip_frame.grid_columnconfigure(2, weight=0)
    page_flip_frame.grid_columnconfigure(3, weight=0)
    page_flip_frame.grid_columnconfigure(4, weight=1)

    previous_page_button = ctk.CTkButton(page_flip_frame, text="← Previous", font=fig_font,
                                             width=child_button_size['width'], height=child_button_size['height'],
                                             fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                             corner_radius=10,
                                             command=lambda: on_previous_page_button_click(genotab, genoclass))
    previous_page_button.grid(row=0, column=0, sticky="e", padx=(10, 10), pady=(5, 5))
    
    # Page number display and input
    page_info_label = ctk.CTkLabel(page_flip_frame, 
                                   text=f"Page {genotab.current_page + 1} of {genotab.tot_pages}", 
                                   font=fig_font,
                                   text_color=COLORS['text_primary'])
    page_info_label.grid(row=0, column=1, padx=(10, 10), pady=(5, 5))
    
    # Page input entry
    page_var = tk.StringVar(value=str(genotab.current_page + 1))
    page_entry = ctk.CTkEntry(page_flip_frame, width=60, height=22,
                              textvariable=page_var, justify="center",
                              font=bmbfont)
    page_entry.grid(row=0, column=2, padx=(10, 10), pady=(5, 5))
    
    def go_to_page(event=None):
        try:
            page_num = int(page_var.get())
            if 1 <= page_num <= genotab.tot_pages:
                genotab.current_page = page_num - 1
                display_page(genotab, genoclass)
            else:
                page_var.set(str(genotab.current_page + 1))
        except ValueError:
            page_var.set(str(genotab.current_page + 1))
    
    page_entry.bind("<Return>", go_to_page)

    go_button = ctk.CTkButton(page_flip_frame, text="Go", font=fig_font,
                              width=50, height=child_button_size['height'],
                              fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                              corner_radius=10,
                              command=go_to_page)
    go_button.grid(row=0, column=3, padx=(10, 10), pady=(5, 5))

    next_page_button = ctk.CTkButton(page_flip_frame, text="Next →", font=fig_font,
                                     width=child_button_size['width'], height=child_button_size['height'],
                                     fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                     corner_radius=10,
                                     command=lambda: on_next_page_button_click(genotab, genoclass))
    next_page_button.grid(row=0, column=4, sticky='w', padx=(10, 10), pady=(5, 5))

    # Conditionally display navigation buttons
    if genotab.current_page == 0:
        previous_page_button.configure(state='disabled')
    elif end_index >= len(genotab.figures):
        next_page_button.configure(state='disabled')
    if genotab.tot_pages == 1:
        previous_page_button.configure(state='disabled')
        next_page_button.configure(state='disabled')
            
    # Continuous scrolling for canvas area with proper scroll units
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"  # Prevent event propagation
    
    def on_shift_mousewheel(event):
        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"  # Prevent event propagation

    # Bind mouse wheel to container frame to capture all scroll events
    def bind_mousewheel_recursive(widget):
        widget.bind("<MouseWheel>", on_mousewheel, add="+")
        widget.bind("<Button-4>", lambda event: canvas.yview_scroll(-3, "units"), add="+")
        widget.bind("<Button-5>", lambda event: canvas.yview_scroll(3, "units"), add="+")
        widget.bind("<Shift-MouseWheel>", on_shift_mousewheel, add="+")
        widget.bind("<Shift-Button-4>", lambda event: canvas.xview_scroll(-3, "units"), add="+")
        widget.bind("<Shift-Button-5>", lambda event: canvas.xview_scroll(3, "units"), add="+")
        for child in widget.winfo_children():
            bind_mousewheel_recursive(child)
    
    # Bind to container and all its children
    container.bind("<MouseWheel>", on_mousewheel)
    container.bind("<Button-4>", lambda event: canvas.yview_scroll(-3, "units"))
    container.bind("<Button-5>", lambda event: canvas.yview_scroll(3, "units"))
    container.bind("<Shift-MouseWheel>", on_shift_mousewheel)
    container.bind("<Shift-Button-4>", lambda event: canvas.xview_scroll(-3, "units"))
    container.bind("<Shift-Button-5>", lambda event: canvas.xview_scroll(3, "units"))
    
    bind_mousewheel_recursive(figures_frame)

def process_fig_table(sample, marker, genoclass, genotab):
    try:
        print(f"Starting to process fig table for {sample}_{marker}")
        amplicon_df = genoclass.get_microhap().get_sam_amplicons_dir().get(f'{sample}').get(f'{marker}')
        hap_df = genoclass.get_microhap().get_sam_microhaps_dir().get(f'{sample}').get(f'{marker}')
        sam_mar = f"{sample}_{marker}"
        if amplicon_df is not None and not amplicon_df.empty:
            fig = create_figure(sample, marker, amplicon_df, hap_df, genotab, genoclass)
            tmp_df1=amplicon_df.head(genotab.n_rows)
            tmp_df2=hap_df if (hap_df is not None and not hap_df.empty) else None
            return fig, tmp_df1, tmp_df2
        else:
            return None,None,None
    except Exception as e:
        print(f"5 Exception in {sam_mar}: {e}")
        traceback.print_exc()
        return None,None,None
    
# def process_fig_table3(sample, marker, genoclass, genotab)->bool:
#     try:
#         print(f"Thread {threading.current_thread().name}: 0 Starting to process fig table for {sample}_{marker}")
#         # Ensure the dictionaries return valid data before accessing it
#         amplicon_df = genoclass.get_microhap().get_sam_amplicons_dir().get(f'{sample}').get(f'{marker}')
#         hap_df = genoclass.get_microhap().get_sam_microhaps_dir().get(f'{sample}').get(f'{marker}')
#         sam_mar = f"{sample}_{marker}"
#         if amplicon_df is not None and not amplicon_df.empty:
#             fig = create_figure(sample, marker, amplicon_df, hap_df, genotab, genoclass)
#             tmp_df1=amplicon_df.head(genotab.n_rows)
#             tmp_df2=hap_df if (hap_df is not None and not hap_df.empty) else None
#             with genotab.figures_lock:
#                 genotab.figures[sam_mar]=fig
#                 genotab.seq_tables[sam_mar]=tmp_df1
#                 genotab.hap_tables[sam_mar]=tmp_df2
#                 return True
#             print(f"Thread {threading.current_thread().name}: 3 Finished to create figure and table for {sam_mar}")
#         print(f"Thread {threading.current_thread().name}: 4 Finished to process fig table for {sam_mar}")
#         return True
#     except Exception as e:
#         # Capture all exceptions for diagnostic information
#         print(f"5 Exception in {sam_mar}: {e}")
#         traceback.print_exc()
#         return True
#     finally:
#         # Add diagnostic to indicate the thread reached the end of the function
#         print(f"Thread {threading.current_thread().name}: 6 finished processing {sam_mar}")
#         return True

# def process_fig_table2(sample, marker, genoclass, genotab):
#     try:
#         print(f"Thread {threading.current_thread().name}: Starting to process fig table for {sample}_{marker}")
#         amplicon_df = genoclass.get_microhap().get_sam_amplicons_dir().get(f'{sample}').get(f'{marker}')
#         hap_df = genoclass.get_microhap().get_sam_microhaps_dir().get(f'{sample}').get(f'{marker}')
#         sam_mar = f"{sample}_{marker}"
#         #print(f"starting to process figure table for {sam_mar}")
#         if amplicon_df is not None and not amplicon_df.empty:
#             with genotab.figures_lock:
#                 genotab.figures[sam_mar]= create_figure(sample, marker, amplicon_df, hap_df, genotab, genoclass)
#             with genotab.tables_lock:
#                 genotab.seq_tables[sam_mar]=amplicon_df.head(genotab.n_rows)
#                 genotab.hap_tables[sam_mar]=(hap_df if not hap_df.empty else None) 
#         #print(f"finished to process figure table for {sam_mar}")
#         print(f"Thread {threading.current_thread().name}: Finished to process fig table for {sample}_{marker}")             
#     except ValueError as e:
#          print(f"Exception in {sample}_{marker}: {e}\n{traceback.format_exc()}")
#     finally:
#         print(f"Thread {threading.current_thread().name} finished processing {sample}_{marker}")

def create_fig_tab_combo(canvas,genotab,start_index,end_index,figures_frame, loci_table, genoclass):
    if len(genotab.figures) == 0:
        return
    # Configure figures_frame to expand columns to full width
    figures_frame.grid_columnconfigure(0, weight=1)
    row_index=0
    for fig, tbl, hap in zip(genotab.figures[start_index:end_index],
                        genotab.seq_tables[start_index:end_index],
                        genotab.hap_tables[start_index:end_index]):
        fig_canvas = FigureCanvasTkAgg(fig, master=figures_frame)
        fig_canvas.draw()
        widget = fig_canvas.get_tk_widget()
        widget.grid(row=row_index, column=0, sticky="wn", padx=5, pady=5)  # Place figure in the left column

        # Create table frame
        table_frame = ctk.CTkFrame(figures_frame, fg_color="white")
        table_frame.grid(row=row_index + 1, column=0, sticky="nsew", padx=5, pady=5)  # Place table below the figure
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        s_table, marker_tmp = create_table(table_frame, hap, tbl)
        if hap is not None:
            if hap['Zygosity'].iloc[0] == "heter":
                toggle_row_background(s_table, 0, 'bg_red')
                toggle_row_background(s_table, 1, 'bg_red')
            elif hap['Zygosity'].iloc[0] == "homo":
                toggle_row_background(s_table, 0, 'bg_red')
        # Create scrollbars for the table
        v_table_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=s_table.yview)
        h_table_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=s_table.xview)

        s_table.configure(yscrollcommand=v_table_scrollbar.set, xscrollcommand=h_table_scrollbar.set)
        marker_tmp = marker_tmp[:(marker_tmp.rfind('_'))]
        genotab.s_table_list[marker_tmp]=s_table
        # Place table and scrollbars
        #s_table.grid(row=0, column=0, sticky="nsew")
        v_table_scrollbar.grid(row=0, column=1, sticky="ns")
        h_table_scrollbar.grid(row=1, column=0, sticky="ew")
        # Reduced sequence widget height from 10 to 6 for more compact display
        seq_widget = tk.Text(figures_frame, wrap="none", bg="white", fg="black", font=seq_font, height=6)
        figures_frame.grid_columnconfigure(0, weight=1)  # Ensure column expands
        seq_widget.grid(row=row_index + 2, column=0, sticky="nsew", padx=5, pady=5)
        seq_widget.tag_configure("red_highlight", background="red", foreground="white")
        seq_widget.tag_configure("green_highlight", background='green', foreground='white')
        seq_widget.tag_configure("blue_highlight", background='blue', foreground='white')
        seq_widget.tag_configure('orange_highlight', background='orange', foreground='white')
        seq_widget.tag_configure('gray_highlight', background='gray', foreground='white')
        seq_widget.tag_configure('blue_text', foreground='blue')
        
        poset=set()
        poslst=[]
        for _, row in tbl.iterrows():
            pos=extract_pos_basechange(row['BaseChange'])
            poslst.append(pos)
            if pos:
                poset.update(pos)
        
        marker=hap['Locus'].iloc[0]
        ref=loci_table.loc[loci_table['locus']==marker, 'ref'].values[0]
        seq_widget.insert("1.0", "**: " + ref + "\n")
        
        poset=sorted(poset)
        start_idx_of_line = 0
        for char_idx in poset:
            # Add the 'blue_text' tag up to the character before this index if it is not adjacent to the previous one.
            if start_idx_of_line < char_idx:
                seq_widget.tag_add('blue_text', f'1.{start_idx_of_line}', f'1.{char_idx}')
            start_idx_of_line = char_idx + 1  # Move past this character's index for the next range.

        # Apply 'blue_text' to the remaining part of the line after the last index in 'poset'.
        if start_idx_of_line < len(ref) + 4:  # 4 is the offset to start counting from after your initial "**: " prefix.
            seq_widget.tag_add('blue_text', f'1.{start_idx_of_line}', '1.end')

        # Apply 'green_highlight' to the specific positions within 'poset'
        for char_idx in poset:
            seq_widget.tag_add('green_highlight', f'1.{char_idx}', f'1.{char_idx + 1}')
        
        #seq_widget.tag_add('blue_text', '1.0', f'1.{min(poset)}' if poset else '2.0')
        for line_num, (index, row) in enumerate(tbl.iterrows(), start=2):
            padded_index = f"{index:02}"
            padded_seq = ("*" * genoclass.get_post_microhap().get_loc_ref_dict().get(marker).get_triml() \
                            + row['Sequence'] \
                            + "*" * genoclass.get_post_microhap().get_loc_ref_dict().get(marker).get_trimr())
            
            seq_widget.insert(f"{line_num}.0", padded_index + ": " + padded_seq + "\n")
            pos=poslst[index]
            if pos:
                if pos[-1] < len(padded_seq):
                    for i in reversed(pos):
                        start_pos=f'{line_num}.{i}'
                        end_pos=f'{line_num}.{i+1}'
                        if line_num - 2 < 2:
                            seq_widget.tag_add('red_highlight', start_pos, end_pos)
                        else:
                            seq_widget.tag_add('orange_highlight', start_pos, end_pos)
        # Ensure seq_widget allows scrolling
        seq_widget.configure(state=tk.DISABLED)  # Prevent user modification while adjusting size
        seq_widget.configure(state=tk.NORMAL)
        row_index += 3  # Increment by 3 to separate figure, table, and sequence widget rows
        def table_scroll(event, s_table):
            if s_table.yview()[0] == 0 and event.delta > 0:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif s_table.yview()[1] == 1 and event.delta < 0:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                s_table.yview_scroll(int(-1 * (event.delta / 120)), "units")

    if 's_table' in locals():
        s_table.bind("<MouseWheel>", lambda event, st=s_table: table_scroll(event, st))

def extract_pos_basechange(base_str):
    pos=[]
    if pd.isna(base_str):
        return pos
    pos=re.split(r'\(.*?\)', base_str)
    pos=[(int(i)+4) for i in pos if i.isdigit()]
    return pos
def create_table(table_frame, hap, tbl):
    # Create Treeview widget
    s_table = ttk.Treeview(
        table_frame,
        columns=(
            'id','sample', 'allele', 'base change', 't. reads', 'n. reads', 'percentage',
            'hap prop', 'allele prop', 'conclusive', 'zygosity', 'indel', 'len'
        ),
        show='headings',
        height=6  # 1 header + 5 data rows
    )
    s_table.grid(row=0, column=0, sticky="nsew")
    
    # Configure tag styles
    s_table.tag_configure('bg_red', background='lightgray')
    s_table.tag_configure('bg_white', background='white')
    
    # Define column headings
    s_table.heading('id', text='id')
    s_table.heading('sample', text='sample')
    s_table.heading('allele', text='allele')
    s_table.heading('base change', text='base change')
    s_table.heading('t. reads', text='t. reads')
    s_table.heading('n. reads', text='n. reads')
    s_table.heading('percentage', text='percentage')
    s_table.heading('hap prop', text='hap prop')
    s_table.heading('allele prop', text='allele prop')
    s_table.heading('conclusive', text='conclusive')
    s_table.heading('zygosity', text='zygosity')
    s_table.heading('indel', text='indel')
    s_table.heading('len', text='len')
    
    # Insert data into the table
    marker_tmp = ""
    if hap is None:
        for index, row in tbl.iterrows():
                if index == 0:
                    marker_tmp = str(row['Sample'])+"_"+row['id']
                if index < 5:  # Limit to 5 rows
                    s_table.insert('', 'end',
                        values=(
                            str(index),
                            str(row['Sample']),
                            row['id'],
                            row['BaseChange'],
                            str(row['TotalReads']),
                            str(row['NumReads']),
                            str(row['ReadRatio']),
                            "nan",
                            "nan",
                            "nan",
                            "nan",
                            "nan",
                            str(row['Length'])
                        )
                    )
    else:
        for index, row in tbl.iterrows():
                if index == 0:
                    marker_tmp = str(row['Sample'])+"_"+row['id']
                if index < 5:  # Limit to 5 rows
                    if index <= (len(hap) - 1):
                        s_table.insert('', 'end',
                            values=(
                                str(index),
                                str(row['Sample']),
                                str(row['id']),
                                hap.iloc[index]['BaseChange'],
                                str(row['TotalReads']),
                                str(row['NumReads']),
                                str(row['ReadRatio']),
                                str(hap.iloc[index]['AlleleReadsPer']),
                                str(hap.iloc[index]['VarRatio']),
                                hap.iloc[index]['Conclusive'],
                                hap.iloc[index]['Zygosity'],
                                hap.iloc[index]['Indel'],
                                str(row['Length'])
                            )
                        )
                    else:
                        s_table.insert('', 'end',
                            values=(
                                str(index),
                                str(row['Sample']),
                                str(row['id']),
                                row['BaseChange'],
                                str(row['TotalReads']),
                                str(row['NumReads']),
                                str(row['ReadRatio']),
                                "nan",
                                "nan",
                                "nan",
                                "nan",
                                "nan",
                                str(row['Length'])
                            )
                        )
    # Configure columns to auto-adjust based on content
    # Calculate max width for each column based on content
    for col in s_table['columns']:
        # Get column heading text length
        heading_width = len(str(s_table.heading(col)['text'])) * 8
        
        # Get max content width
        max_content_width = heading_width
        for item in s_table.get_children():
            values = s_table.item(item)['values']
            col_index = s_table['columns'].index(col)
            if col_index < len(values):
                content_width = len(str(values[col_index])) * 8
                max_content_width = max(max_content_width, content_width)
        
        # Set column width with minimum and stretch
        s_table.column(col, anchor=tk.CENTER, width=max_content_width, minwidth=50, stretch=True)
    
    return s_table, marker_tmp

def on_bar_click(event, ax, bars, fig, sample, mar, genotab, genoclass):
    if event.inaxes == ax:
        micro_df = genoclass.get_microhap().get_sam_microhaps_dir().get(sample).get(mar)
        print(f"sample: {sample} and marker: {mar} are selected")
        sam_mar_id=sample+"_"+mar
        if bars[0].contains(event)[0]:
            cur_fir_bar_col = bars[0].get_facecolor()
            new_fir_bar_col = color_bars['lgray'] if cur_fir_bar_col == color_bars['dgreen'] else color_bars['dgreen']
            s_table = genotab.s_table_list.get(sam_mar_id)
            if new_fir_bar_col == color_bars['lgray']:
                toggle_row_background(s_table, 0, 'bg_white', 'inconclusive')
                bars[0].set_facecolor(color_bars['lgray'])
                micro_df.at[0, 'Zygosity'] = 'inconclusive'
                micro_df.at[0, 'Conclusive'] = 'N'
                if len(bars) > 1:
                    toggle_row_background(s_table, 1, 'bg_white', 'inconclusive')
                    bars[1].set_facecolor(color_bars['lgray'])
                    micro_df.at[1, 'Zygosity'] = 'inconclusive'
                    micro_df.at[1, 'Conclusive'] = 'N'
            else:
                toggle_row_background(s_table, 0, 'bg_red', 'homo')
                bars[0].set_facecolor(color_bars['dgreen'])
                micro_df.at[0, 'Zygosity'] = 'homo'
                micro_df.at[0, 'Conclusive'] = 'Y'
                if len(bars) > 1:
                    toggle_row_background(s_table, 1, 'bg_white', 'homo')
                    bars[1].set_facecolor(color_bars['lgray'])
                    micro_df.at[1, 'Zygosity'] = 'homo'
                    micro_df.at[1, 'Conclusive'] = 'Y'
            fig.canvas.draw_idle()
            genoclass.get_microhap().get_sam_microhaps_dir().get(sample)[mar] = micro_df
        elif bars[1].contains(event)[0]:
            cur_sec_bar_col = bars[1].get_facecolor()
            new_sec_bar_col = color_bars['lgray'] if cur_sec_bar_col == color_bars['orange'] else color_bars['orange']
            s_table = genotab.s_table_list.get(sam_mar_id)
            if new_sec_bar_col == color_bars['lgray']:
                toggle_row_background(s_table, 1, 'bg_white', 'homo')
                bars[1].set_facecolor(color_bars['lgray'])
                toggle_row_background(s_table, 0, 'bg_red', 'homo')
                bars[0].set_facecolor(color_bars['dgreen'])
                micro_df.at[0:1, 'Zygosity'] = ['homo', 'homo']
                micro_df.at[0:1, 'Conclusive'] = ['Y','Y']
            else:
                toggle_row_background(s_table, 1, 'bg_red', 'heter')
                bars[1].set_facecolor(color_bars['orange'])
                toggle_row_background(s_table, 0, 'bg_red', 'heter')
                bars[0].set_facecolor(color_bars['dgreen'])
                micro_df.at[0:1, 'Zygosity'] = ['heter', 'heter']
                micro_df.at[0:1, 'Conclusive'] = ['Y','Y']
            fig.canvas.draw_idle()
            genoclass.get_microhap().get_sam_microhaps_dir().get(sample)[mar] = micro_df
            
def create_figure(sample, mar, amplicon_df, hap_df, genotab, genoclass):
    df = amplicon_df.head(5)
    colors=list(repeat(color_bars['lgray'], 5))
    if not hap_df.empty:
        if hap_df['Zygosity'].iloc[0] == "heter":
            colors[0:2]=(color_bars['dgreen'], color_bars['orange'])
        elif hap_df['Zygosity'].iloc[0] == "homo":
            colors[0]=color_bars['dgreen']
    else:
        print(f"fig generation is none")
        return None

    #with matplotlib_lock:
        # Reduced figure size for better fit - was (4,1.5), now (3,1)
    fig = Figure(figsize=(3, 1), dpi=200)  # Reduced dpi from 300 to 200
    ax = fig.add_subplot(111)
    #bars = ax.bar(df['id'], df['NumReads'], tick_label=[str(x) for x in df['id']], color=colors)
    bars = ax.bar(df.index,
                    df['NumReads'],
                    tick_label=[str(x) for x in df.index],
                    color = colors)
    ax.set_title(f"Sample: {sample}, Marker: {mar}", fontdict={'fontsize': 5, 'fontweight': 'bold'})
        #ax.set_xticks(df['id'])
    ax.set_xticks(df.index)
        #ax.set_xticklabels(df['id'], rotation=45, fontsize=8)
    ax.set_xticklabels(df.index, fontsize=3)
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels([str(int(i)) for i in ax.get_yticks()], fontsize=3)
    fig.tight_layout(pad=1)  # Reduced padding from 2 to 1
    fig.canvas.mpl_connect("button_press_event", lambda event: on_bar_click(event, ax, bars, fig, sample, mar, genotab, genoclass))
    return fig
def toggle_row_background(treeview, idx, tag_to_set=None, zygosity=None):
    #print(f"change the background of indx:{idx}, tag_to_set:{tag_to_set}, zygosity:{zygosity}")
    background_tags = {'bg_red', 'bg_white'}
    try:
        row_id = treeview.get_children()[idx]
    except IndexError:
        print(f"No item exists at index {idx} in the Treeview.")
        return  # Or handle the error as necessary
    # for child in treeview.get_children():
    #     item = treeview.item(child)
    #     values = item['values']
    #     print(item['text'], values)
    current_tags = set(treeview.item(row_id, 'tags'))
    new_tags = (current_tags - background_tags)
    if tag_to_set:
        new_tags.add(tag_to_set)
    treeview.item(row_id, tags=list(new_tags))
    if zygosity is not None:
        zygosity_column_index = treeview['columns'].index('zygosity')
        values = list(treeview.item(row_id, 'values'))
        values[zygosity_column_index] = zygosity
        con_column_index = treeview['columns'].index('conclusive')
        values[con_column_index] = "N" if (zygosity == "inconclusive" or zygosity == 'nan') else "Y"
        treeview.item(row_id, values=values)
    
def on_previous_page_button_click(tab, genoclass):
    #update_navigation_button(tab, previous_page_button,next_page_button)
    if tab.current_page > 0:
        tab.current_page -= 1
        display_page(tab, genoclass)
    
def on_next_page_button_click(tab, genoclass):
    #update_navigation_button(tab, previous_page_button,next_page_button)      
    if tab.current_page < (tab.tot_pages -1):
        tab.current_page += 1
        display_page(tab, genoclass)

def update_navigation_button(tab, previous_page_button,next_page_button):
    if tab.tot_pages == 1:
        previous_page_button.configure(state="disabled")
        next_page_button.configure(state="disabled")
    else:
        if tab.current_page == 0:
            previous_page_button.configure(state="disabled")
            next_page_button.configure(state="normal")
        elif tab.current_page == (tab.tot_pages-1):
            previous_page_button.configure(state="normal")
            next_page_button.configure(state='disabled')
        else:
            previous_page_button.configure(state="normal")
            next_page_button.configure(state="normal")