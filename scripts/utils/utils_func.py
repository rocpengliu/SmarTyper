import customtkinter as ctk
from tkinter import filedialog
from . import modern_messagebox
import os, sys
import threading
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from Bio.Seq import Seq
from .utils_common import matplotlib_lock, print_time, thread_lock
from .common import *
import traceback
import numpy as np
import pdb
import copy
from ..utils import modern_messagebox

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
        modern_messagebox.showerror(canvas.master, "Error", f"Error loading PDF from {file_path}: {e}")

def output_all_fig_tab(is_pro_fig,output_folder_path, markers,selected_sample,sam_microhap_dict_sam, sam_ml_dict_sam, anal_type)->bool:
    #print(f"starting to output_all_fig_tab for {selected_sample}")
    if is_pro_fig:
        produce_fig_sam_mar_pdf(output_folder_path, markers, sam_microhap_dict_sam, selected_sample, anal_type)
    output_geno_table(output_folder_path,selected_sample, sam_microhap_dict_sam, anal_type)
    ml_df_dict = prod_ml_tbl(sam_microhap_dict_sam,sam_ml_dict_sam, selected_sample, anal_type)
    #print(f"finished to output_all_fig_tab for {selected_sample}")
    return ml_df_dict

def output_geno_table(output_folder_path,selected_sample, sam_microhap_dict_sam, anal_type)->bool:
    #print(f"starting to output_geno_table for {selected_sample}")
    tab_file_path = os.path.join(output_folder_path, f"{selected_sample}_sample_final_genotype.txt")
    geno_df = pd.concat(sam_microhap_dict_sam.values(), ignore_index=True)
    geno_df.to_csv(tab_file_path, sep="\t", index=False)
    #print(f"finished to output_geno_table for {selected_sample}")
    return True

def prod_ml_tbl(sam_microhap_dict_sam, sam_ml_dict_sam, selected_sample, anal_type):
    # geno_df_dict = sam_microhap_dict.get(selected_sample)
    #print(f"starting to prod_ml_tbl for {selected_sample}")
    if sam_microhap_dict_sam is None:
        print(f"sample {selected_sample} not found!")
        return None
    else:
        ml_df_dict = copy.deepcopy(sam_ml_dict_sam)
    if ml_df_dict is not None:
        for mar, microh_df in sam_microhap_dict_sam.items():
            if mar in ml_df_dict.keys():
                zygo = microh_df.at[0, 'Zygosity']
                if zygo == 'heter':
                    ml_df_dict[mar].at[0, 'Zygosity'] = 2
                elif zygo == 'homo':
                    ml_df_dict[mar].at[0, 'Zygosity'] = 1
    #print(f"finished to prod_ml_tbl for {selected_sample}")
    return ml_df_dict

def output_all_geno_table(genoclass, anal_type):
    tab_file_path = os.path.join(genoclass.get_parameter().get_outputdir(), f"All_sample_final_genotype.txt")
    for idx, (sam, sam_dict) in enumerate(genoclass.get_microhap().get_sam_microhaps_dir().items()):
        geno_df = pd.concat(sam_dict.values(), ignore_index=True)
        if idx == 0:
            geno_df.to_csv(tab_file_path, sep="\t", index=False, header=True)
        else:
            geno_df.to_csv(tab_file_path, sep="\t", index=False, header=False, mode='a')
    
    tab_file_path2 = os.path.join(genoclass.get_parameter().get_outputdir(), "All_ml_table.txt")
    ml_df = pd.concat(
                    [df for od in genoclass.get_microhap().get_sam_mar_ml_dir().values() for df in od.values() if df is not None],
                    axis = 0, ignore_index = True)
    ml_df = ml_df.sort_values(by=['Locus']).reset_index(drop=True)
    ml_df.to_csv(tab_file_path2, sep = "\t", index = False)

def produce_fig_sam_mar_pdf(output_folder_path, markers, sam_microhap_dict_sam, selected_sample, anal_type)->bool:
    print(f"Starting to process sample: {selected_sample}")
    pdf_file_path = os.path.join(output_folder_path, f"{selected_sample}_sample_genotype.pdf")
    # with matplotlib_lock:
    try:
        with PdfPages(pdf_file_path) as pdf:
            nrows, ncols = 8, 5
            fig, axes = None, None
            tot_pages = 0
            for i, loc in enumerate(markers):
                # print(f"Thread {threading.current_thread().name}: start to process sample: {selected_sample} in index: {i} for marker: {loc}")
                if i % (nrows * ncols) == 0:
                    if fig is not None:
                        fig.text(
                            0.5, 0.01, f"Page {tot_pages + 1}", ha="center", fontsize=8
                        )
                        pdf.savefig(fig)
                        plt.close(fig)
                        tot_pages += 1
                    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 10))
                    axes = np.atleast_2d(axes)
                if (i // ncols % nrows) >= nrows or (i % ncols) >= ncols:
                    continue
                ax = axes[i // ncols % nrows, i % ncols]
                colors = ["lightgray", "lightgray"]
                subset = sam_microhap_dict_sam.get(loc)
                if len(subset) == 0:
                    subset = pd.DataFrame(
                        {
                            "id": [f"{loc}_0", f"{loc}_1"],
                            "NumReads": [0, 0],
                            "Allele": [1, 2],
                            "Zygosity": ["nan", "nan"],
                        }
                    )
                zygo = subset["Zygosity"].iloc[0]
                if zygo == "heter":
                    colors[0:2] = ("darkgreen", "orange")
                elif zygo == "homo":
                    colors[0] = "darkgreen"
                ax.bar(x=subset["id"], height=subset["NumReads"], color=colors)
                ax.set_xticks(range(len(subset)))
                ax.set_xticklabels(subset["Allele"].astype(str))
                ax.set_title(
                    f"marker: {loc} ({zygo})",
                    fontsize=8,
                    color="red" if zygo == "inconclusive" else "black",
                )
                ax.tick_params(axis="x", labelsize=6)
                ax.tick_params(axis="y", labelsize=6)
                fig.subplots_adjust(hspace=0.8)
                fig.suptitle(f"Genotypes of sample {selected_sample}")
                fig.text(0.08, 0.5, "Number of reads", va="center", rotation="vertical")
                # print(f"Thread {threading.current_thread().name}: Finished to process sample: {selected_sample} in index: {i} for marker: {loc}")

            if fig is not None:
                fig.text(0.08, 0.5, "Number of reads", va="center", rotation="vertical")
                fig.text(0.5, 0.01, f"Page {tot_pages + 1}", ha="center", fontsize=8)
                pdf.savefig(fig)
                plt.close(fig)
    except Exception as e:
        print(f"Thread {threading.current_thread().name}: Error for sample {selected_sample}: {e}")
        traceback.print_exc()
        return False
    print(f"finished to output genotype plots for {selected_sample}")
    return True

def produce_fig_mar_sam_pdf_pool(output_folder_path, samples, sam_microhap_dict, selected_marker, anal_type) -> bool:
    #print(f"Starting to process marker: {selected_marker}")
    pdf_file_path = os.path.join(output_folder_path, f"{selected_marker}_marker_genotype.pdf")
    nrows, ncols = 8, 5
    max_plots_per_page = nrows * ncols
    # with matplotlib_lock:
    try:
        with PdfPages(pdf_file_path) as pdf:
            tot_pages = 0
            num_samples = len(samples)
            for page_start in range(0, num_samples, max_plots_per_page):
                fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 10))
                # Normalize axes to always be 2D
                axes = np.atleast_2d(axes)
                # For a single subplot, axes is a scalar
                if axes.shape == ():
                    axes = np.array([[axes]])
                page_samples = samples[page_start : page_start + max_plots_per_page]
                for j, sam in enumerate(page_samples):
                    # Compute grid position
                    row = j // ncols
                    col = j % ncols
                    ax = axes[row, col]
                    colors = ["lightgray", "lightgray"]
                    subset = sam_microhap_dict.get(sam, {})
                    if subset is None or len(subset) == 0:
                        subset = pd.DataFrame(
                            {
                                "id": [f"{selected_marker}_0", f"{selected_marker}_1"],
                                "NumReads": [0, 0],
                                "Allele": [1, 2],
                                "Zygosity": ["nan", "nan"],
                            }
                        )
                    zygo = subset["Zygosity"].iloc[0]
                    if zygo == "heter":
                        colors[0:2] = ("darkgreen", "orange")
                    elif zygo == "homo":
                        colors[0] = "darkgreen"
                    try:
                        ax.bar(x=subset["id"], height=subset["NumReads"], color=colors)
                        ax.set_xticks(range(len(subset)))
                        ax.set_xticklabels(subset["Allele"].astype(str))
                        ax.set_title(
                            f"sample: {sam} ({zygo})",
                            fontsize=8,
                            color="red" if zygo == "inconclusive" else "black",
                        )
                        ax.tick_params(axis="x", labelsize=6)
                        ax.tick_params(axis="y", labelsize=6)
                    except Exception as plot_err:
                        print(f"{sam} / {selected_marker}: plotting error: {plot_err}")
                        traceback.print_exc()
                    fig.subplots_adjust(hspace=0.8)
                    fig.suptitle(f"Genotypes of marker {selected_marker}")
                    fig.text(0.08, 0.5, "Number of reads", va="center", rotation="vertical")
                # Blank remaining axes (if any)
                total_plots = len(page_samples)
                for blank_j in range(total_plots, max_plots_per_page):
                    row = blank_j // ncols
                    col = blank_j % ncols
                    axes[row, col].axis("off")
                fig.text(0.5, 0.01, f"Page {tot_pages + 1}", ha="center", fontsize=8)
                pdf.savefig(fig)
                plt.close(fig)
                tot_pages += 1
    except Exception as e:
        print(f"Thread {threading.current_thread().name}: Error for marker {selected_marker}: {e}")
        traceback.print_exc()
        return False
    #print(f"finished to output genotype plots for {selected_marker}")
    return True

def produce_micro_fig_mar_sam_pdf_pool(output_folder_path, samples, sam_microhap_dict, selected_marker, anal_type = 'snp') -> bool:
    #print(f"Starting to process marker: {selected_marker}")
    pdf_file_path = os.path.join(output_folder_path, f"{selected_marker}_marker_microhap_genotype.pdf")
    nrows, ncols = 8, 5
    max_plots_per_page = nrows * ncols
    # with matplotlib_lock:
    try:
        with PdfPages(pdf_file_path) as pdf:
            tot_pages = 0
            num_samples = len(samples)
            for page_start in range(0, num_samples, max_plots_per_page):
                fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 10))
                # Normalize axes to always be 2D
                axes = np.atleast_2d(axes)
                # For a single subplot, axes is a scalar
                if axes.shape == ():
                    axes = np.array([[axes]])
                page_samples = samples[page_start : page_start + max_plots_per_page]
                for j, sam in enumerate(page_samples):
                    # Compute grid position
                    row = j // ncols
                    col = j % ncols
                    ax = axes[row, col]
                    colors = ["lightgray", "lightgray"]
                    subset = sam_microhap_dict.get(sam, {})
                    if subset is None or len(subset) == 0:
                        subset = pd.DataFrame(
                            {
                                "id": [f"mh_0", f"mh_1"],
                                "NumReads": [0, 0],
                                "Allele": [1, 2],
                                "Zygosity": ["nan", "nan"],
                            }
                        )
                    zygo = subset["Zygosity"].iloc[0]
                    if zygo == "heter":
                        colors[0:2] = ("darkgreen", "orange")
                    elif zygo == "homo":
                        colors[0] = "darkgreen"
                    try:
                        ax.bar(x=subset["id"], height=subset["NumReads"], color=colors)
                        ax.set_xticks(range(len(subset)))
                        ax.set_xticklabels(subset["Allele"].astype(str))
                        ax.set_title(
                            f"sample: {sam} ({zygo})",
                            fontsize=8,
                            color="red" if zygo == "inconclusive" else "black",
                        )
                        ax.tick_params(axis="x", labelsize=6)
                        ax.tick_params(axis="y", labelsize=6)
                    except Exception as plot_err:
                        print(f"{sam} / {selected_marker}: plotting error: {plot_err}")
                        traceback.print_exc()
                    fig.subplots_adjust(hspace=0.8)
                    fig.suptitle(f"Genotypes of marker {selected_marker}")
                    fig.text(0.08, 0.5, "Number of reads", va="center", rotation="vertical")
                # Blank remaining axes (if any)
                total_plots = len(page_samples)
                for blank_j in range(total_plots, max_plots_per_page):
                    row = blank_j // ncols
                    col = blank_j % ncols
                    axes[row, col].axis("off")
                fig.text(0.5, 0.01, f"Page {tot_pages + 1}", ha="center", fontsize=8)
                pdf.savefig(fig)
                plt.close(fig)
                tot_pages += 1
    except Exception as e:
        print(f"Thread {threading.current_thread().name}: Error for marker {selected_marker}: {e}")
        traceback.print_exc()
        return False
    #print(f"finished to output genotype plots for {selected_marker}")
    return True

def produce_micro_fig_sam_mar_pdf_pool(output_folder_path, mars, mar_microhap_dict, selected_sample, anal_type = 'snp') -> bool:
    #print(f"Starting to process marker: {selected_marker}")
    pdf_file_path = os.path.join(output_folder_path, f"{selected_sample}_sample_microhap_genotype.pdf")
    nrows, ncols = 8, 5
    max_plots_per_page = nrows * ncols
    # with matplotlib_lock:
    try:
        with PdfPages(pdf_file_path) as pdf:
            tot_pages = 0
            num_mars = len(mars)
            for page_start in range(0, num_mars, max_plots_per_page):
                fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 10))
                # Normalize axes to always be 2D
                axes = np.atleast_2d(axes)
                # For a single subplot, axes is a scalar
                if axes.shape == ():
                    axes = np.array([[axes]])
                page_mars = mars[page_start : page_start + max_plots_per_page]
                for j, mar in enumerate(page_mars):
                    # Compute grid position
                    row = j // ncols
                    col = j % ncols
                    ax = axes[row, col]
                    colors = ["lightgray", "lightgray"]
                    subset = mar_microhap_dict.get(mar, {})
                    if subset is None or len(subset) == 0:
                        subset = pd.DataFrame(
                            {
                                "id": [f"mh_0", f"mh_1"],
                                "NumReads": [0, 0],
                                "Allele": [1, 2],
                                "Zygosity": ["nan", "nan"],
                            }
                        )
                    zygo = subset["Zygosity"].iloc[0]
                    if zygo == "heter":
                        colors[0:2] = ("darkgreen", "orange")
                    elif zygo == "homo":
                        colors[0] = "darkgreen"
                    try:
                        ax.bar(x=subset["id"], height=subset["NumReads"], color=colors)
                        ax.set_xticks(range(len(subset)))
                        ax.set_xticklabels(subset["Allele"].astype(str))
                        ax.set_title(
                            f"marker: {mar} ({zygo})",
                            fontsize=8,
                            color="red" if zygo == "inconclusive" else "black",
                        )
                        ax.tick_params(axis="x", labelsize=6)
                        ax.tick_params(axis="y", labelsize=6)
                    except Exception as plot_err:
                        print(f"{mar} / {selected_sample}: plotting error: {plot_err}")
                        traceback.print_exc()
                    fig.subplots_adjust(hspace=0.8)
                    fig.suptitle(f"Genotypes of sample {selected_sample}")
                    fig.text(0.08, 0.5, "Number of reads", va="center", rotation="vertical")
                # Blank remaining axes (if any)
                total_plots = len(page_mars)
                for blank_j in range(total_plots, max_plots_per_page):
                    row = blank_j // ncols
                    col = blank_j % ncols
                    axes[row, col].axis("off")
                fig.text(0.5, 0.01, f"Page {tot_pages + 1}", ha="center", fontsize=8)
                pdf.savefig(fig)
                plt.close(fig)
                tot_pages += 1
    except Exception as e:
        print(f"Thread {threading.current_thread().name}: Error for marker {selected_marker}: {e}")
        traceback.print_exc()
        return False
    #print(f"finished to output genotype plots for {selected_marker}")
    return True

def produce_fig_mar_sam_pdf(output_folder_path, samples, sam_microhap_dict, selected_marker, anal_type) -> bool:
    #print(f"Starting to process marker: {selected_marker}")
    pdf_file_path = os.path.join(output_folder_path, f"{selected_marker}_marker_genotype.pdf")
    nrows, ncols = 8, 5
    max_plots_per_page = nrows * ncols
    # with matplotlib_lock:
    try:
        with PdfPages(pdf_file_path) as pdf:
            tot_pages = 0
            num_samples = len(samples)
            for page_start in range(0, num_samples, max_plots_per_page):
                fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 10))
                # Normalize axes to always be 2D
                axes = np.atleast_2d(axes)
                # For a single subplot, axes is a scalar
                if axes.shape == ():
                    axes = np.array([[axes]])
                page_samples = samples[page_start : page_start + max_plots_per_page]
                for j, sam in enumerate(page_samples):
                    # Compute grid position
                    row = j // ncols
                    col = j % ncols
                    ax = axes[row, col]
                    colors = ["lightgray", "lightgray"]
                    subset = sam_microhap_dict.get(sam, {}).get(selected_marker)
                    if subset is None or len(subset) == 0:
                        subset = pd.DataFrame(
                            {
                                "id": [f"{selected_marker}_0", f"{selected_marker}_1"],
                                "NumReads": [0, 0],
                                "Allele": [1, 2],
                                "Zygosity": ["nan", "nan"],
                            }
                        )
                    zygo = subset["Zygosity"].iloc[0]
                    if zygo == "heter":
                        colors[0:2] = ("darkgreen", "orange")
                    elif zygo == "homo":
                        colors[0] = "darkgreen"
                    try:
                        ax.bar(x=subset["id"], height=subset["NumReads"], color=colors)
                        ax.set_xticks(range(len(subset)))
                        ax.set_xticklabels(subset["Allele"].astype(str))
                        ax.set_title(
                            f"sample: {sam} ({zygo})",
                            fontsize=8,
                            color="red" if zygo == "inconclusive" else "black",
                        )
                        ax.tick_params(axis="x", labelsize=6)
                        ax.tick_params(axis="y", labelsize=6)
                    except Exception as plot_err:
                        print(f"{sam} / {selected_marker}: plotting error: {plot_err}")
                        traceback.print_exc()
                    fig.subplots_adjust(hspace=0.8)
                    fig.suptitle(f"Genotypes of marker {selected_marker}")
                    fig.text(
                        0.08, 0.5, "Number of reads", va="center", rotation="vertical"
                    )
                # Blank remaining axes (if any)
                total_plots = len(page_samples)
                for blank_j in range(total_plots, max_plots_per_page):
                    row = blank_j // ncols
                    col = blank_j % ncols
                    axes[row, col].axis("off")
                fig.text(0.5, 0.01, f"Page {tot_pages + 1}", ha="center", fontsize=8)
                pdf.savefig(fig)
                plt.close(fig)
                tot_pages += 1
    except Exception as e:
        print(f"Thread {threading.current_thread().name}: Error for marker {selected_marker}: {e}")
        traceback.print_exc()
        return False
    #print(f"finished to genotype plots for {selected_marker}")
    return True

def produce_fig_mar_sam_pdf1(genoclass,selected_marker, anal_type)->bool:
    #print(f"Thread {threading.current_thread().name}: Starting to process marker: {selected_marker}")
    samples = genoclass.get_metadata().get_samples_list()
    pdf_file_path = os.path.join(genoclass.get_parameter().get_outputdir(), f"{selected_marker}_marker_genotype.pdf")
    nrows, ncols = 8, 5
    max_plots_per_page = nrows * ncols
    with matplotlib_lock:
        try:
            with PdfPages(pdf_file_path) as pdf:
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
                        axes = np.atleast_2d(axes)
                    if (i // ncols % nrows) >= nrows or (i % ncols) >= ncols:
                        continue
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
                #print(f"Thread {threading.current_thread().name}: Finished to process marker: {selected_marker}")
                return True
        except Exception as e:
            print(f"Thread {threading.current_thread().name}: Error for sample {selected_marker}: {e}")
            traceback.print_exc()
            return False
    return True

def produce_reads_dis_fig(i,num_pages,sorted_data,bars_per_page,bars_per_subplot,num_subplots_per_page):
        if i == num_pages:
            x_list=list(sorted_data.keys())[i*bars_per_page:len(sorted_data)]
            y_list=list(sorted_data.values())[i*bars_per_page:len(sorted_data)]
            num_subplots_per_page=len(x_list)/bars_per_subplot
            if num_subplots_per_page % 1 ==0:
                num_subplots_per_page=int(num_subplots_per_page)
            else:
                num_subplots_per_page=int(num_subplots_per_page)+1
        else:
            x_list=list(sorted_data.keys())[i*bars_per_page:(i+1)*bars_per_page]
            y_list=list(sorted_data.values())[i*bars_per_page:(i+1)*bars_per_page]
        fig,axs=plt.subplots(nrows=num_subplots_per_page,ncols=1,figsize=(16,9))
        
        for j in range(num_subplots_per_page):
            x=x_list[j*bars_per_subplot:(j+1)*bars_per_subplot]
            y=y_list[j*bars_per_subplot:(j+1)*bars_per_subplot]
            if len(x)==0:
                break
            ax=axs[j]
            ax.bar(x,y)
            ax.tick_params(axis='x',labelsize=6)
            ax.tick_params(axis='y',labelsize=6)
        return fig,axs

def generate_page(i, num_pages, sorted_data, bars_per_page, bars_per_subplot, num_subplots_per_page):
        fig, axs = produce_reads_dis_fig(i, num_pages, sorted_data, bars_per_page, bars_per_subplot, num_subplots_per_page)
        if fig is not None:
            fig.suptitle(f"Reads distribution of all samples",fontsize=16,x=0.5,y=0.95,horizontalalignment='center')
            fig.text(0.08,0.5,'n. of reads',va='center',rotation='vertical')
            fig.text(0.5,0.01,f'page{i+1}',ha='center',fontsize=8)
        return i, fig

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
            modern_messagebox.showerror(None, "Invalid Input", f"Invalid coding positions string: {pos_str}")
            raise ValueError(f"Invalid coding positions string: {pos_str}")
    except ValueError as e:
        modern_messagebox.showerror(None, "Invalid Input", str(e))
        return None

def get_triml_pos(out_lst, trimlpos):
    new_pos = []
    new_start = None
    if trimlpos < out_lst[0][0]:
        new_pos = [(posl - trimlpos -1 , posr - trimlpos - 1) for (posl, posr) in out_lst]
        return new_pos
    else:
        for in_lst in out_lst:
            pos_lst = []
            for pos in list(range(in_lst[0], in_lst[1])):
                pos_lst.append(pos)
                if pos == trimlpos:
                    if len(pos_lst) == 1:
                        new_start = 2
                    elif len(pos_lst) == 2:
                        new_start = 1
                    else:
                        new_start = 0
                    break
                if len(pos_lst) == 3:
                    pos_lst = []
    if new_start is None:
        return new_pos
    else:
        tmp_pos = [(posl - trimlpos -1, posr - trimlpos -1) for (posl, posr) in out_lst]
        for in_lst in tmp_pos:
            if in_lst[1] <= 0:
                pass
            elif in_lst[0] < 0 and in_lst[1] > 0:
                new_pos.append((new_start, in_lst[1]))
            else:
                new_pos.append(in_lst)
    return new_pos

def get_trimr_pos(out_lst, trimrpos):
    new_pos = []
    new_end = None
    for in_lst in out_lst[::-1]:
        pos_lst = []
        for pos in list(range(in_lst[0], in_lst[1])):
            pos_lst.append(pos)
            if pos == trimrpos:
                if len(pos_lst) == 1:
                    new_end = pos
                elif len(pos_lst) == 2:
                    new_end = pos -1
                else:
                    new_end = pos - 2
                break
            if len(pos_lst) == 3:
                pos_lst = []
    if new_end is None:
        return new_pos
    for in_lst in out_lst:
        if trimrpos >= in_lst[1]:
            new_pos.append(in_lst)
        elif trimrpos <= in_lst[0]:
            pass
        else:
            new_pos.append((in_lst[0], new_end))
    return new_pos

def get_new_codingpos(codingpos, triml, trimr, dnalen):
    new_codingpos = []
    if triml == 0 and trimr == 0:
        return new_codingpos
    elif triml != 0 and trimr == 0:
        trimlpos = triml - 1
        for out_lst in codingpos:
            if trimlpos < out_lst[-1][-1] - 3:
                tmps = get_triml_pos(out_lst, trimlpos)
                if len(tmps) != 0:
                    new_codingpos.append(tmps)
    elif triml == 0 and trimr != 0:
        trimrpos = dnalen - trimr -1
        for out_lst in codingpos:
            if (trimrpos + 1) >= out_lst[-1][1]:
                new_codingpos.append(out_lst)
            else:
                tmps = get_trimr_pos(out_lst, trimrpos)
                if len(tmps) != 0:
                    new_codingpos.append(tmps)
    else:
        trimrpos = dnalen - trimr -1
        for out_lst in codingpos:
            if (trimrpos + 1) >= out_lst[-1][1]:
                new_codingpos.append(out_lst)
            else:
                tmps = get_trimr_pos(out_lst, trimrpos)
                if len(tmps) != 0:
                    new_codingpos.append(tmps)
        if len(new_codingpos) != 0:
            trimlpos = triml - 1
            new_new_codingpos = []
            for out_lst in new_codingpos:
                if trimlpos < out_lst[-1][-1] - 3:
                    tmps = get_triml_pos(out_lst, trimlpos)
                    if len(tmps) != 0:
                        new_new_codingpos.append(tmps)
            new_codingpos = new_new_codingpos
    return new_codingpos

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

def process_sample_for_pool(args):
    sam, vdic = args
    # No output_queue here! Only return results.
    return sam, pd.concat([df.dropna(axis=1, how='all') for df in vdic.values()], axis=0, ignore_index=True)

def populate_mar_sam_microhap(mar, samples, mar_mh_df, cur = True)->pd.DataFrame:
    tmp_df = pd.DataFrame(columns=['Locus','Label','Seq', 'ID'])
    try:
        if cur:
            mar_sam_microhap=set()#microhap seqs
            for sam in samples:
                mar_sam_microhap_df = mar_mh_df.loc[mar_mh_df['Sample'] == sam]
                zygo= mar_sam_microhap_df['Zygosity'].iloc[0]
                if zygo == "homo":
                    mar_sam_microhap.add(mar_sam_microhap_df['Sequence'].iloc[0])
                elif zygo == "heter":
                    mar_sam_microhap.add(mar_sam_microhap_df['Sequence'].iloc[0])
                    mar_sam_microhap.add(mar_sam_microhap_df['Sequence'].iloc[1])
            if mar_sam_microhap:
                mar_sam_microhap = sorted(mar_sam_microhap)
            if len(mar_sam_microhap) !=0:
                tmp_df=pd.DataFrame({
                                'Locus':[mar]*len(mar_sam_microhap),
                                'Label':[f'mh_{i}' for i in range(len(mar_sam_microhap))],
                                'Seq':mar_sam_microhap, 
                                'ID': [i for i in range(len(mar_sam_microhap))]})
            else:
                return tmp_df
        else:
            if mar_mh_df is None :
                return tmp_df
            tmp_df = mar_mh_df.reset_index(drop=True)
            tmp_df = tmp_df.drop_duplicates(subset='Seq')
            tmp_df.columns = ['Locus','Label','Seq', 'ID']
        if tmp_df is None or len(tmp_df) == 0:
            return tmp_df
        tmp_df = tmp_df.sort_values(by="ID").reset_index(drop=True)
    except Exception as e:
        print(f"Error in populate_mar_sam_microhap for marker {mar}: {e}", flush=True)
        traceback.print_exc()
        raise(e)
    return tmp_df

def populate_each_mar_mh_dict(mar, records) -> tuple:
    final_sam_cur_mh_dict = {}
    final_sam_cur_mh_sim_dict = {}
    cur_mar_mh_df = pd.DataFrame.from_records(records)
    if cur_mar_mh_df.empty:
        return final_sam_cur_mh_dict, final_sam_cur_mh_sim_dict
    for sam in sorted(cur_mar_mh_df['Sample'].unique()):
        tmp_df = cur_mar_mh_df[cur_mar_mh_df['Sample'] == sam].reset_index(drop=True)
        final_sam_cur_mh_dict[sam] = tmp_df
        tmp_sim_df = tmp_df[['Sample', 'Allele', 'Zygosity']].copy()
        zygo = tmp_sim_df['Zygosity'].iloc[0]
        if zygo == 'homo':
            if tmp_sim_df.shape[0] == 1:
                tmp_sim_df = pd.concat([tmp_sim_df, tmp_sim_df], ignore_index=True)
            else:
                tmp_sim_df.iloc[1, tmp_sim_df.columns.get_loc('Allele')] = \
                    tmp_sim_df.iloc[0]['Allele']
        elif zygo == 'heter':
            tmp_sim_df = tmp_sim_df.sort_values(by='Allele')
        else:
            tmp_sim_df.loc[:, 'Allele'] = '-9'
        tmp_sim_df = tmp_sim_df.drop(columns='Zygosity')
        tmp_sim_df = tmp_sim_df.pivot_table(
            index='Sample',
            columns=tmp_sim_df.groupby('Sample').cumcount(),
            values='Allele',
            aggfunc='first'
        ).reset_index()
        tmp_sim_df.columns = ['Sample', f'{mar}_allele1', f'{mar}_allele2']
        final_sam_cur_mh_sim_dict[sam] = tmp_sim_df
    return final_sam_cur_mh_dict, final_sam_cur_mh_sim_dict

def init_assigned_reads(mars, samples):
    sam_mar_reads_dict = {sam : {mar : 0 for mar in mars} for sam in samples}
    return sam_mar_reads_dict

def init_sam_microhaps(mars, samples):
    sam_micro_dict = {sam : {mar : pd.DataFrame(columns=micro_microhap_df_columns) for mar in mars} for sam in samples}
    return sam_micro_dict

def init_sam_amplicons(mars, samples):
    sam_amp_dict = {sam : {mar : pd.DataFrame(columns=micro_amplicon_df_columns) for mar in mars} for sam in samples}
    return sam_amp_dict

def init_sam_mar_ml(mars, samples):
    sam_mar_ml_dict = {sam : {mar : pd.DataFrame(columns=ml_mh_df_columns) for mar in mars} for sam in samples}
    return sam_mar_ml_dict
