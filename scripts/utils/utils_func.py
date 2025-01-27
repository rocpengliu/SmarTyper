import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from Bio.Seq import Seq
from .utils_common import matplotlib_lock, print_time

def load_pdf(file_path, canvas):
    try:
        doc = fitz.open(file_path)
        y_offset = 0  # Initial y-offset for stacking images vertically
        canvas.image_refs = []  # Store references to avoid garbage collection
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_tk = ImageTk.PhotoImage(img)
            # Add image to canvas
            canvas.create_image(0, y_offset, anchor="nw", image=img_tk)
            canvas.image_refs.append(img_tk)  # Keep a reference to avoid garbage collection
            y_offset += pix.height  # Increment y-offset by the height of the image
        canvas.configure(scrollregion=canvas.bbox("all"))  # Update scroll region after all images are loaded
    except Exception as e:
        messagebox.showerror("Error", f"Error loading PDF from {file_path}: {e}")

def output_all_fig_tab(genoclass,selected_sample,anal_type)->bool:
    print_time(f"starting to output_all_fig_tab for {selected_sample}")
    if genoclass.get_parameter().is_pro_figure():
        produce_fig_sam_mar_pdf(genoclass,selected_sample,anal_type)
    output_geno_table(genoclass,selected_sample,anal_type)
    print_time(f"finished to output_all_fig_tab for {selected_sample}")
    return True

def output_geno_table(genoclass,selected_sample,anal_type)->bool:
    tab_file_path = os.path.join(genoclass.get_parameter().get_outputdir(), f"{selected_sample}_sample_final_genotype.txt")
    geno_df_dict = genoclass.get_microhap().get_sam_microhaps_dir().get(selected_sample)
    geno_df = pd.concat(geno_df_dict.values(), ignore_index=True)
    geno_df.to_csv(tab_file_path, sep="\t", index=False)
    return True

def output_all_geno_table(genoclass):
    tab_file_path = os.path.join(genoclass.get_parameter().get_outputdir(), f"all_sample_final_genotype.txt")
    for idx, (sam, sam_dict) in enumerate(genoclass.get_microhap().get_sam_microhaps_dir().items()):
        geno_df = pd.concat(sam_dict.values(), ignore_index=True)
        if idx == 0:
            geno_df.to_csv(tab_file_path, sep="\t", index=False, header=True)
        else:
            geno_df.to_csv(tab_file_path, sep="\t", index=False, header=False, mode='a')
    
def produce_fig_sam_mar_pdf(genoclass,selected_sample,anal_type)->bool:
    print(f"Thread {threading.current_thread().name}: Starting to process sample: {selected_sample}")
    markers = genoclass.get_metadata().get_ref_markers_list()
    pdf_file_path = os.path.join(genoclass.get_parameter().get_outputdir(), f"{selected_sample}_sample_genotype.pdf")
    with matplotlib_lock:
        with PdfPages(pdf_file_path) as pdf:
            nrows, ncols = 8, 5
            fig, axes = None, None
            tot_pages = 0
            for i, loc in enumerate(markers):
                #print(f"Thread {threading.current_thread().name}: start to process sample: {selected_sample} in index: {i} for marker: {loc}")
                if i % (nrows * ncols) == 0:
                    if fig is not None:
                        fig.text(0.5, 0.01, f'Page {tot_pages + 1}', ha='center', fontsize=8)
                        pdf.savefig(fig)
                        plt.close(fig)
                        tot_pages += 1
                    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 10))
                ax = axes[i // ncols % nrows, i % ncols]
                colors = ['lightgray', 'lightgray']
                subset = genoclass.get_microhap().get_sam_microhaps_dir().get(selected_sample).get(loc)
                if len(subset) == 0:
                    subset = pd.DataFrame({
                        'id': [f'{loc}_0', f'{loc}_1'],
                        'NumReads': [0, 0],
                        'Allele': [1, 2],
                        'Zygosity': ['nan', 'nan']
                    })
                zygo = subset['Zygosity'].iloc[0]
                if zygo == "heter":
                    colors[0:2] = ('darkgreen', 'orange')
                elif zygo == "homo":
                    colors[0] = 'darkgreen'
                ax.bar(x=subset['id'],
                    height=subset['NumReads'],
                    color=colors)
                ax.set_xticks(range(len(subset)))
                ax.set_xticklabels(subset['Allele'].astype(str))
                ax.set_title(f'{loc} ({zygo})', fontsize=8)
                ax.tick_params(axis='x', labelsize=6)
                ax.tick_params(axis='y', labelsize=6)
                fig.subplots_adjust(hspace=0.8)
                fig.suptitle(f"Genotypes of sample {selected_sample}")
                fig.text(0.08, 0.5, 'Number of reads', va='center', rotation='vertical')
                print(f"Thread {threading.current_thread().name}: Finished to process sample: {selected_sample} in index: {i} for marker: {loc}")

            if fig is not None:
                fig.text(0.08, 0.5, 'Number of reads', va='center', rotation='vertical')
                fig.text(0.5, 0.01, f'Page {tot_pages + 1}', ha='center', fontsize=8)
                pdf.savefig(fig)
                plt.close(fig)
            print(f"Thread {threading.current_thread().name}: Finished to process sample: {selected_sample}")
            return True
    return True

def produce_fig_mar_sam_pdf(genoclass,selected_marker, anal_type)->bool:
    print(f"Thread {threading.current_thread().name}: Starting to process marker: {selected_marker}")
    samples = genoclass.get_metadata().get_samples_list()
    pdf_file_path = os.path.join(genoclass.get_parameter().get_outputdir(), f"{selected_marker}_marker_genotype.pdf")
    with matplotlib_lock:
        with PdfPages(pdf_file_path) as pdf:
            nrows, ncols = 8, 5
            fig, axes = None, None
            tot_pages = 0
            for i, sam in enumerate(samples):
                #print(f"Thread {threading.current_thread().name}: start to process marker: {selected_marker} in index: {i} for sample: {sam}")
                if i % (nrows * ncols) == 0:
                    if fig is not None:
                        fig.text(0.5, 0.01, f'Page {tot_pages + 1}', ha='center', fontsize=8)
                        pdf.savefig(fig)
                        plt.close(fig)
                        tot_pages += 1
                    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 10))
                ax = axes[i // ncols % nrows, i % ncols]
                colors = ['lightgray', 'lightgray']
                subset = genoclass.get_microhap().get_sam_microhaps_dir().get(sam).get(selected_marker)
                if len(subset) == 0:
                    subset = pd.DataFrame({
                        'id': [f'{selected_marker}_0', f'{selected_marker}_1'],
                        'NumReads': [0, 0],
                        'Allele': [1, 2],
                        'Zygosity': ['nan', 'nan']
                    })
                zygo = subset['Zygosity'].iloc[0]
                if zygo == "heter":
                    colors[0:2] = ('darkgreen', 'orange')
                elif zygo == "homo":
                    colors[0] = 'darkgreen'
                ax.bar(x=subset['id'],
                    height=subset['NumReads'],
                    color=colors)
                ax.set_xticks(range(len(subset)))
                ax.set_xticklabels(subset['Allele'].astype(str))
                ax.set_title(f'{sam} ({zygo})', fontsize=8)
                ax.tick_params(axis='x', labelsize=6)
                ax.tick_params(axis='y', labelsize=6)
                fig.subplots_adjust(hspace=0.8)
                fig.suptitle(f"Genotypes of marker {selected_marker}")
                fig.text(0.08, 0.5, 'Number of reads', va='center', rotation='vertical')
                #print(f"Thread {threading.current_thread().name}: Finished to process marker: {selected_marker} in index: {i} for sample: {sam}")

            if fig is not None:
                fig.text(0.08, 0.5, 'Number of reads', va='center', rotation='vertical')
                fig.text(0.5, 0.01, f'Page {tot_pages + 1}', ha='center', fontsize=8)
                pdf.savefig(fig)
                plt.close(fig)
            print(f"Thread {threading.current_thread().name}: Finished to process marker: {selected_marker}")
            return True
    return True

def trans_dna(dna:str, exon_pos_list:list)->list:
    if len(dna)==0 or dna is None or len(exon_pos_list)==0:
        return[]
    return [trans_single_dna(dna, plst) for plst in exon_pos_list]

def trans_single_dna(dna:str, exon_pos:list):
    cds=""
    if len(exon_pos) == 0:
        return cds
    exon_list=[]
    for start, end in exon_pos:
        exon=dna[start:end]
        exon_list.append(exon)
    cds=''.join(exon_list)
    # print(f"dna is {dna}")
    # print(f"exon_pos is {exon_pos}")
    # print(f"cds is {cds}")
    cds_dna=Seq(cds)
    aa_seq = cds_dna.translate()
    return str(cds_dna), str(aa_seq)

def split_codingpos(pos_str:str)->list:
    if len(pos_str.replace(" ", "")) == 0 or pos_str.replace(' ', '') == '0':
        return None
    nested_list  = [[tuple(map(int, p2.split(':'))) for p2 in p1.split(',')] for p1 in pos_str.replace(' ', '').split('|')]
    nested_list = [[(x, y+1) for x, y in inter_tuple] for inter_tuple in nested_list]
    print(f"splitted coding positions is {nested_list}")
    try:
        if all(isinstance(item, tuple) and all(isinstance(i, int) for i in item) for sublist in nested_list for item in sublist):
            return nested_list
        else:
            raise ValueError(f"Invalid coding positions string: {pos_str}")
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))
        return None

def check_overlapping_gene(nested_list):
    len_list = [len(pos_list) for pos_list in nested_list]
    max_idx = len_list.index(max(len_list))
    max_elem = []
    if max_idx != 0:
        max_elem = nested_list.pop(max_idx)
        nested_list.insert(0, max_elem)
    else:
        max_elem = nested_list[0]

    go = True
    for tuple_lst in nested_list[1:]:
        go = (go and all(tup in max_elem for tup in tuple_lst))
        if not go:
            break
    return go

def get_splicer_exon_list_map(nested_list):
    super_ref_list = nested_list[0]
    splicer_exon_list_dic = {}
    for idx, tup in enumerate(super_ref_list):
        splicer_exon_list_dic[tup] = idx
    
    splicer_exon_map = {'splicer_0' : list(range(len(super_ref_list)))}
    for idx, tuple_list in enumerate(nested_list):
        if idx != 0:
            exon_list = []
            for tup in tuple_list:
                exon_list.append(splicer_exon_list_dic[tup])
            splicer_exon_map[f'splicer_{idx}'] = exon_list
    
    return splicer_exon_map