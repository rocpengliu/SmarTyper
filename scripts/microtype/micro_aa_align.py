import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import logomaker
from ..utils.utils_common import print_time
from ..utils.common import child_button_size
import pdb
import copy
import os
import pandas as pd

matplotlib.use("TkAgg")

def display_aa_seq_align(genotab, genoclass):
    mar = genoclass.get_post_microhap().get_selected_marker()
    if mar == "":
        return
    ref_mar_refmt = genoclass.get_post_microhap().get_loc_ref_dict().get(mar, None)
    if ref_mar_refmt is None:
        return
    
    if genoclass.get_post_microhap().get_dna_or_aa() != 'aa':
        return
    else:
        if not ref_mar_refmt.get_has_splicer():
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

    splicer=f'splicer_{genotab.page_num}'
    ref_compre_mt = ref_mar_refmt.get_ref_microtype_dict().get(splicer, None)
    if ref_compre_mt is None:
        return
    cur_compre_mt = ref_mar_refmt.get_children_microtype_dict().get(splicer, None)#CompreMicrotypeClass
    if cur_compre_mt is None:
        return

    working_splicer_cur_compre = cur_compre_mt if ref_mar_refmt.is_overlapped_gene() else ref_mar_refmt.get_children_microtype_dict().get('splicer_0', None)
    if working_splicer_cur_compre is None:
        return
    working_splicer_ref_compre = ref_compre_mt if ref_mar_refmt.is_overlapped_gene() else ref_mar_refmt.get_ref_microtype_dict().get('splicer_0', None)
    if working_splicer_ref_compre is None:
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
    fig_frame.grid(row=0, column=0, sticky="nws", padx=5, pady=(2,2))
    create_fig(working_splicer_cur_compre, ref_compre_mt, cur_compre_mt, fig_frame, genoclass)

    # Frames for content
    tbl_frame = ctk.CTkFrame(scroll_frame, fg_color='white')
    tbl_frame.grid_rowconfigure(0, weight=1)  # Configure the tbl_frame to expand vertically
    tbl_frame.grid_columnconfigure(0, weight=1)
    tbl_frame.grid(row=1, column=0, sticky="news", padx=5, pady=(2,2))
    create_align_tbl(working_splicer_ref_compre, working_splicer_cur_compre, ref_mar_refmt, ref_compre_mt, cur_compre_mt, tbl_frame)
    
    page_flip_frame=ctk.CTkFrame(genotab, fg_color='#3b3b3b')
    page_flip_frame.grid(row=2,column=0, pady=(5,5), sticky='ew')
    
    genotab.previous_page_button = ctk.CTkButton(page_flip_frame, text="Previous", font=("Helvetica", 12, "bold"),
                                         width=child_button_size['width'], height=child_button_size['height'],
                                         command=lambda:change_page(-1, genotab, genoclass))
    genotab.previous_page_button.grid(row=0,column=0,sticky="e",padx=(100,0), pady=(5,5))
    #previous_page_button.pack(side="left", padx=(10, 50), pady=(5,5))
    genotab.next_page_button = ctk.CTkButton(page_flip_frame, text="Next", font=("Helvetica", 12, "bold"),
                                     width=child_button_size['width'], height=child_button_size['height'],
                                     command=lambda:change_page(1, genotab, genoclass))
    genotab.next_page_button.grid(row=0,column=1, sticky='e', padx=(200, 0), pady=(2,2))

    # Ensure scroll_frame expands and fills the canvas upon resize
    canvas.bind("<Configure>", lambda event: on_canvas_configure(canvas, event))
    canvas.bind_all("<MouseWheel>", lambda event: on_mouse_wheel(event, canvas))
    canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

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
        display_aa_seq_align(genotab, genoclass)

def on_canvas_configure(canvas, event):
    """Reset the scroll region to encompass the inner frame and resize inner frame"""
    canvas_width = event.width
    canvas_height = event.height
    canvas.itemconfig('inner_frame', width=canvas_width, height=canvas_height)
    canvas.configure(scrollregion=canvas.bbox("all"))
    
def create_fig(working_splicer_cur_compre, ref_compre_mt, cur_compre_mt, fig_frame, genoclass):
    #pdb.set_trace()
    base_freq_df = working_splicer_cur_compre.get_aa_base_freq_df()
    if base_freq_df.shape[0] == 0:
        return
    index_list = sorted(set(working_splicer_cur_compre.get_target_aa_snp_pos_list() + working_splicer_cur_compre.get_tot_aa_snp_pos_list()))
    base_freq_df.reset_index(drop=True, inplace=True)

    #base_freq_df = base_freq_df[~base_freq_df.isin([1.0]).any(axis=1)]
    base_freq_df=base_freq_df.iloc[index_list]
    if base_freq_df.shape[0] == 0:
        return
    
    # print_time(f'index_list is {index_list}')
    # ori_index_list = ref_compre_mt.convert_pos_cur_2_ori(index_list)
    # print_time(f'convert index list is {ori_index_list}')
    tick_labels = list(map(str, index_list))
    #tick_labels = list(map(str, ori_index_list))
    
    base_freq_df.reset_index(drop=True, inplace=True)
    
    base_width_per_datapoint=1
    num_datapoints=base_freq_df.shape[0]
    tot_fig_width=base_width_per_datapoint*num_datapoints
    fig_height=3
    fig=plt.Figure(figsize=(tot_fig_width, fig_height))
    ax=fig.add_subplot(111)

    logo = logomaker.Logo(base_freq_df, ax=ax)

     # Set x-ticks to match the positions of the DataFrame rows
    tick_positions = range(len(base_freq_df))
    logo.ax.set_xticks(tick_positions)
    # Now set the new tick labels
    logo.ax.set_xticklabels(tick_labels)
    
    logo.ax.set_xlim(-0.5, base_freq_df.shape[0] - 0.5)  # Adjust x-axis limits
    logo.ax.set_ylim(0, logo.ax.get_ylim()[1] * 1.2)  # Increase y-axis limit
    #logo.fig.set_size_inches(50, 10)  # Width, Height in inches
    logo.ax.set_ylabel('Base freq', labelpad=10)
    logo.ax.set_title(f'{cur_compre_mt.get_label(False)}')
    # Optionally adjust layout for more space
    plt.subplots_adjust(left=0.2, right=0.9, top=0.8, bottom=0.2)
    fig_canvas = FigureCanvasTkAgg(logo.fig, master=fig_frame)
    fig_canvas.draw()
    fig_widget = fig_canvas.get_tk_widget()
    fig_widget.grid(row=0, column=0, sticky="nsew", padx=(30,0))  # Ensure full expansion
    
    output_path = os.path.join(genoclass.get_parameter().get_post_microhap_output_dir(), f'{cur_compre_mt.get_label(False)}_aa_seq_logo.pdf')
    print_time(f"saving seq logo fig for {cur_compre_mt.get_mar()}")
    try:
        logo.fig.savefig(output_path, bbox_inches='tight', transparent=True)
    except Exception as e:
            print(f"Error saving seq logo fig for {cur_compre_mt.get_mar()}: {e}")
    plt.close(logo.fig)
    
def create_align_tbl(working_splicer_ref_compre, working_splicer_cur_compre, ref_mar_refmt, ref_compre_mt, cur_compre_mt, tbl_frame):
    #pdb.set_trace()
    v_scrollbar_seq=ttk.Scrollbar(tbl_frame, orient="vertical")
    v_scrollbar_seq.grid(row=0, column=1, sticky="ns")
    h_scrollbar_seq=ttk.Scrollbar(tbl_frame, orient="horizontal")
    h_scrollbar_seq.grid(row=1, column=0, sticky="ew")
    seq_widget = tk.Text(tbl_frame, wrap="none", bg="white", fg="black", font=("Courier New", 11), yscrollcommand=v_scrollbar_seq.set)
    seq_widget.grid(row=0, column=0, sticky="nsew")  # Ensure full expansion
    seq_widget.configure(state='normal')
    v_scrollbar_seq.configure(command=seq_widget.yview)
    h_scrollbar_seq.configure(command=seq_widget.xview)
    seq_widget.tag_configure("gray_highlight", background="gray", foreground="white")
    seq_widget.tag_configure("red_highlight", background="red", foreground="white")
    seq_widget.tag_configure("green_highlight", background='green', foreground='white')
    seq_widget.tag_configure("blue_highlight", background='blue', foreground='white')
    seq_widget.tag_configure('orange_highlight', background='orange', foreground='white')
    seq_widget.tag_configure('olive_highlight', background='olive', foreground='white')
    seq_widget.tag_configure('teal_highlight', background='teal', foreground='white')
    seq_widget.tag_configure('blue_text', foreground='blue')
    seq_widget.tag_configure('purple_text', foreground='purple')

    exon_list = []
    if not ref_mar_refmt.is_overlapped_gene():
        exon_list = ref_mar_refmt.get_splicer_exon_list_dict().get(ref_compre_mt.get_splicer())
        if (exon_list is None) or (not exon_list):
            raise ValueError(f'No exon list for splicer {ref_compre_mt.get_splicer()}')
    print_time(f'exon_list is {exon_list}')
    refseq = working_splicer_cur_compre.get_ref_aa_seq() if ref_mar_refmt.is_overlapped_gene() else ref_mar_refmt.get_aa_ref()
    target_snppos = working_splicer_cur_compre.get_target_aa_snp_pos_list()
    ref_label = working_splicer_cur_compre.get_label()
    max_label_len = max(len(ref_label), working_splicer_cur_compre.cal_longest_compre_var_label())
    seq_len = len(refseq)
    line_num = 1

    break_padding = '+' * (max_label_len + 2)
    break_padding += ('+' * seq_len)
    seq_widget.insert(f'{line_num}.0', break_padding + '\n')

    cur_exon_start_end_pos_list = working_splicer_ref_compre.extract_aa_exon_start_end_pos_list_in_splicer()
    if exon_list:
        cur_exon_start_end_pos_list = [cur_exon_start_end_pos_list[i] for i in exon_list]
    print_time(f'cur_exon_start_end_pos_list is {cur_exon_start_end_pos_list}')
    for idx, pos_tuple in enumerate(cur_exon_start_end_pos_list):
        start, end = pos_tuple
        start += (max_label_len + 2)
        end += (max_label_len + 2)
        exon_len = end - start
        
        exon = str(exon_list[idx]) if exon_list else str(idx)
        if exon_len < len(exon):
            exon = 'E'
        elif exon_len < (len(exon) + 1):
            exon = exon
        elif exon_len < (len(exon) + 2):
            exon = f'E{exon}'
        elif exon_len < (len(exon) + 3):
            exon = f'<E{exon}'
        else:
            exon = f'<E{exon}>'
        mid = (start + end )//2
        if len(exon) % 2 == 0:
            new_start = mid - len(exon) // 2
            new_end = mid + len(exon) // 2
        else:
            new_start = mid - len(exon) // 2 -1
            new_end = mid + len(exon) // 2
        seq_widget.replace(f'{line_num}.{new_start}', f'{line_num}.{new_end}', exon)
        seq_widget.tag_add(('orange_highlight' if idx % 2 == 0 else 'olive_highlight'), f'{line_num}.{start}', f'{line_num}.{end}')

    line_num += 1

    star_padding = '|' * (max_label_len+2)
    num_pos = [0] + [p for p in range(9, seq_len, 10)]
    ii = 0
    while ii < seq_len:
        if ii in num_pos:
            star_padding += str(ii)
            ii += len(str(ii))
        else:
            star_padding += '|'
            ii += 1
    seq_widget.insert(f'{line_num}.0', star_padding + '\n')
    line_num += 1
    
    padding = '*' * (max_label_len - len(ref_label))
    seq_widget.insert(f'{line_num}.0', f'{padding}{ref_label}: ' + refseq + '\n')

    snp_pos = working_splicer_cur_compre.get_tot_aa_snp_pos_list()
    uniq_snp_pos = [elem for elem in target_snppos if elem not in snp_pos]#for green
    union_snp_pos = uniq_snp_pos + snp_pos
    union_snp_pos = sorted(union_snp_pos)
    if len(union_snp_pos) != 0:
        union_snp_pos = [n + max_label_len + 2 for n in union_snp_pos]
        uniq_snp_pos = [n + max_label_len + 2 for n in uniq_snp_pos]
        start_idx_of_line = 0
        for char_idx in union_snp_pos:
            if start_idx_of_line < char_idx:
                seq_widget.tag_add('blue_text', f'{line_num}.{start_idx_of_line}', f'{line_num}.{char_idx}')
            start_idx_of_line = char_idx + 1
        if start_idx_of_line < seq_len + 2 + max_label_len:
            seq_widget.tag_add('blue_text', f'{line_num}.{start_idx_of_line}', f'{line_num}.end')
        for char_idx in union_snp_pos:
            if char_idx in uniq_snp_pos:
                seq_widget.tag_add('green_highlight', f'{line_num}.{char_idx}', f'{line_num}.{char_idx + 1}')
            else:
                seq_widget.tag_add('red_highlight', f'{line_num}.{char_idx}', f'{line_num}.{char_idx + 1}')
    else:
        seq_widget.tag_add('blue_text', f'{line_num}.0', f'{line_num}.end')
    line_num += 1
    for idx, compre_var in enumerate(working_splicer_cur_compre.get_aa_mp_dict().values()):
        #pdb.set_trace()
        label_len = len(compre_var.get_id())
        padding = '*' * (max_label_len - label_len)
        seq_widget.insert(f'{idx+line_num}.0', padding + f'{compre_var.get_id()}: ' + f'{compre_var.get_seq()}' + '\n')
        if len(compre_var.get_indel_pos_list()) == 0:
            pos_list = copy.copy(sorted(compre_var.get_snp_pos_list()))
            if len(pos_list) != 0:
                pos_list = [n + max_label_len + 2 for n in pos_list]
                union2 = sorted(uniq_snp_pos + [n for n in pos_list if n not in uniq_snp_pos])
                if len(union2) > 0:
                    for pos in union2:
                        if pos in uniq_snp_pos:
                            seq_widget.tag_add('green_highlight', f'{idx+line_num}.{pos}', f'{idx+line_num}.{pos+1}')
                        else:
                            seq_widget.tag_add('red_highlight', f'{idx+line_num}.{pos}', f'{idx+line_num}.{pos+1}')
            else:
                pos_list = [n + max_label_len + 2 for n in target_snppos]
                for pos in pos_list:
                    seq_widget.tag_add('green_highlight', f'{idx+line_num}.{pos}', f'{idx+line_num}.{pos+1}')
        else:
            seq_widget.tag_add('gray_highlight', f'{idx+line_num}.0', f'{idx+line_num}.{max_label_len}')
    seq_widget.configure(state='disabled')

def on_mouse_wheel(event, canvas):
    """Scroll the canvas based on mouse wheel movement."""
    if event.delta > 0:
        canvas.yview_scroll(-1, "units")
    else:
        canvas.yview_scroll(1, "units")
