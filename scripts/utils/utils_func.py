import customtkinter as ctk
from tkinter import filedialog

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
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
from .modern_messagebox import ModernMessageBox
from scripts.class_modules.microtype_class import ComboMicroType

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
        ModernMessageBox.showerror(canvas.master, "Error", f"Error loading PDF from {file_path}: {e}")

def output_all_fig_tab(is_pro_fig,output_folder_path, markers,selected_sample,sam_microhap_dict_sam, sam_ml_dict_sam, sam_mar_snp_dict_sam, anal_type)->bool:
    #print(f"starting to output_all_fig_tab for {selected_sample}")
    if is_pro_fig:
        produce_fig_sam_mar_pdf(output_folder_path, markers, sam_microhap_dict_sam, selected_sample, anal_type)
    output_geno_table(output_folder_path,selected_sample, sam_microhap_dict_sam, anal_type)
    #ml_df_dict = prod_ml_tbl(sam_microhap_dict_sam, sam_ml_dict_sam, selected_sample, anal_type)
    output_ml_table(output_folder_path,selected_sample, sam_ml_dict_sam, anal_type)
    output_snp_table(output_folder_path, selected_sample, sam_mar_snp_dict_sam, sam_ml_dict_sam, anal_type)
    #print(f"finished to output_all_fig_tab for {selected_sample}")
    return True

def output_snp_table(output_folder_path, selected_sample, sam_mar_snp_dict_sam, sam_ml_dict_sam, anal_type) -> bool:
    for mar, snp_df in sam_mar_snp_dict_sam.items():
        if snp_df is None or snp_df.empty:
            continue
        snp_df['conclusive'] = 'N'
        if mar in sam_ml_dict_sam.keys():
            if sam_ml_dict_sam[mar] is None or sam_ml_dict_sam[mar].empty:
                continue
            zygo = sam_ml_dict_sam[mar].iloc[0]['zygosity']
            if zygo == 1:
                snp_df['conclusive'] = 'Y'
                snp_df['allele2'] = snp_df['allele1']
            elif zygo == 2:
                snp_df['conclusive'] = 'Y'
                snp_df['allele2'] = snp_df['allele3']

    tab_file_path = os.path.join(output_folder_path, f"{selected_sample}_sample_final_snp.txt")
    snp_df = pd.concat(sam_mar_snp_dict_sam.values(), ignore_index=True)
    snp_df.to_csv(tab_file_path, sep="\t", index=False)
    return True

def output_geno_table(output_folder_path,selected_sample, sam_microhap_dict_sam, anal_type)->bool:
    #print(f"starting to output_geno_table for {selected_sample}")
    tab_file_path = os.path.join(output_folder_path, f"{selected_sample}_sample_final_haplotype.txt")
    geno_df = pd.concat(sam_microhap_dict_sam.values(), ignore_index=True)
    geno_df.to_csv(tab_file_path, sep="\t", index=False)
    #print(f"finished to output_geno_table for {selected_sample}")
    return True

def output_ml_table(output_folder_path,selected_sample, sam_ml_dict_sam, anal_type)->bool:
    tab_file_path = os.path.join(output_folder_path, f"{selected_sample}_sample_final_ml.txt")
    ml_df = pd.concat(sam_ml_dict_sam.values(), ignore_index=True)
    ml_df.to_csv(tab_file_path, sep="\t", index=False)
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
                zygo = microh_df.at[0, 'zygosity']
                if zygo == 'heter':
                    ml_df_dict[mar].at[0, 'zygosity'] = 2
                elif zygo == 'homo':
                    ml_df_dict[mar].at[0, 'zygosity'] = 1
                else:
                    ml_df_dict[mar].at[0, 'zygosity'] = 0
    #print(f"finished to prod_ml_tbl for {selected_sample}")
    return ml_df_dict

def output_all_geno_table(genoclass, anal_type):
    tab_file_path = os.path.join(genoclass.get_parameter().get_outputdir(), f"All_sample_final_haplotype.txt")
    for idx, (sam, sam_dict) in enumerate(genoclass.get_microhap().get_sam_microhaps_dir().items()):
        geno_df = pd.concat(sam_dict.values(), ignore_index=True)
        if idx == 0:
            geno_df.to_csv(tab_file_path, sep="\t", index=False, header=True)
        else:
            geno_df.to_csv(tab_file_path, sep="\t", index=False, header=False, mode='a')
    
    tab_file_path2 = os.path.join(genoclass.get_parameter().get_outputdir(), "All_sample_final_ml.txt")
    ml_df = pd.concat(
                    [df for od in genoclass.get_microhap().get_sam_mar_ml_dict().values() for df in od.values() if df is not None],
                    axis = 0, ignore_index = True)
    ml_df = ml_df.sort_values(by=['locus']).reset_index(drop=True)
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
                            "read": [0, 0],
                            "allele": [1, 2],
                            "zygosity": ["nan", "nan"],
                        }
                    )
                zygo = subset["zygosity"].iloc[0]
                if zygo == "heter":
                    colors[0:2] = ("darkgreen", "orange")
                elif zygo == "homo":
                    colors[0] = "darkgreen"
                ax.bar(x=subset["id"], height=subset["read"], color=colors)
                ax.set_xticks(range(len(subset)))
                ax.set_xticklabels(subset["allele"].astype(str))
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
    pdf_file_path = os.path.join(output_folder_path, f"{selected_marker}_locus_genotype.pdf")
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
                                "read": [0, 0],
                                "allele": [1, 2],
                                "zygosity": ["nan", "nan"],
                            }
                        )
                    zygo = subset["zygosity"].iloc[0]
                    if zygo == "heter":
                        colors[0:2] = ("darkgreen", "orange")
                    elif zygo == "homo":
                        colors[0] = "darkgreen"
                    try:
                        ax.bar(x=subset["id"], height=subset["read"], color=colors)
                        ax.set_xticks(range(len(subset)))
                        ax.set_xticklabels(subset["allele"].astype(str))
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
                    fig.suptitle(f"Genotypes of locus {selected_marker}")
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

def produce_micro_fig_mar_sam_pdf_pool(output_folder_path, samples, sam_microhap_dict, selected_marker, micotype = 'microhap', anal_type = 'snp') -> bool:
    #print(f"Starting to process marker: {selected_marker}")
    pdf_file_path = os.path.join(output_folder_path, f"{selected_marker}_locus_{micotype}_genotype.pdf")
    nrows, ncols = 8, 5
    max_plots_per_page = nrows * ncols
    # with matplotlib_lock:
    mt_label = "mh" if micotype == 'microhap' else "mp"
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
                                "id": [f"{mt_label}_-9", f"{mt_label}_-99"],
                                "read": [0, 0],
                                "allele": [f"{mt_label}_-9", f"{mt_label}_-99"],
                                "zygosity": ["nan", "nan"],
                            }
                        )
                    zygo = subset["zygosity"].iloc[0]
                    if zygo == "heter":
                        colors[0:2] = ("darkgreen", "orange")
                    elif zygo == "homo":
                        colors[0] = "darkgreen"
                    try:
                        ax.bar(x=subset["allele"], height=subset["read"], color=colors)
                        ax.set_xticks(range(len(subset)))
                        ax.set_xticklabels(subset["allele"].astype(str))
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
                    fig.suptitle(f"{micotype} of locus {selected_marker}")
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

def produce_micro_fig_sam_mar_pdf_pool(output_folder_path, mars, mar_microhap_dict, selected_sample, microtype = "microhap", anal_type = 'snp') -> bool:
    #print(f"Starting to process marker: {selected_marker}")
    pdf_file_path = os.path.join(output_folder_path, f"{selected_sample}_sample_{microtype}_genotype.pdf")
    nrows, ncols = 8, 5
    max_plots_per_page = nrows * ncols
    # with matplotlib_lock:
    mt = "mh" if microtype == "microhap" else "mp"
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
                                "id": [f"{mt}_-9", f"{mt}_-99"],
                                "read": [0, 0],
                                "allele": [f"{mt}_-9", f"{mt}_-99"],
                                "zygosity": ["nan", "nan"],
                            }
                        )
                    zygo = subset["zygosity"].iloc[0]
                    if zygo == "heter":
                        colors[0:2] = ("darkgreen", "orange")
                    elif zygo == "homo":
                        colors[0] = "darkgreen"
                    try:
                        ax.bar(x=subset["allele"], height=subset["read"], color=colors)
                        ax.set_xticks(range(len(subset)))
                        ax.set_xticklabels(subset["allele"].astype(str))
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
        print(f"Thread {threading.current_thread().name}: Error for sample {selected_sample}: {e}")
        traceback.print_exc()
        return False
    #print(f"finished to output genotype plots for {selected_marker}")
    return True

def produce_fig_mar_sam_pdf(output_folder_path, samples, sam_microhap_dict, selected_marker, anal_type) -> bool:
    #print(f"Starting to process marker: {selected_marker}")
    pdf_file_path = os.path.join(output_folder_path, f"{selected_marker}_locus_genotype.pdf")
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
                                "read": [0, 0],
                                "allele": [1, 2],
                                "zygosity": ["nan", "nan"],
                            }
                        )
                    zygo = subset["zygosity"].iloc[0]
                    if zygo == "heter":
                        colors[0:2] = ("darkgreen", "orange")
                    elif zygo == "homo":
                        colors[0] = "darkgreen"
                    try:
                        ax.bar(x=subset["id"], height=subset["read"], color=colors)
                        ax.set_xticks(range(len(subset)))
                        ax.set_xticklabels(subset["allele"].astype(str))
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
                    fig.suptitle(f"Genotypes of locus {selected_marker}")
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
    pdf_file_path = os.path.join(genoclass.get_parameter().get_outputdir(), f"{selected_marker}_locus_genotype.pdf")
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
                    fig.suptitle(f"Genotypes of locus {selected_marker}")
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

def get_exon_start_end_pos_from_dna_exon_pos(exon_pos_list:list)->list:
    if exon_pos_list is None or len(exon_pos_list)==0:
        return []
    exon_start_end_pos_list=[]
    start_pos = 0
    end_pos = 0
    for start, end in exon_pos_list:
        exon_len = (end - start) // 3
        end_pos += exon_len
        start_pos = end_pos - exon_len
        exon_start_end_pos_list.append((start_pos, end_pos))
    return exon_start_end_pos_list

def trans_dna(dna:str, exon_pos_list:list)->list:
    if dna is None or len(dna)==0 or exon_pos_list is None or len(exon_pos_list)==0:
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
    nested_list = [tuple(map(int, p.split(':'))) for p in pos_str.replace(' ', '').split('|')]
    nested_list = [(x, y) for x, y in nested_list]
    for x, y in nested_list:
        exon_len  = y - x
        if exon_len < 3:
            ModernMessageBox.showerror(None, "Invalid Input", f"Exon length must be at least 3: {x}:{y}")
            raise ValueError(f"Exon length must be at least 3: {x}:{y}")
        elif exon_len % 3 != 0:
            ModernMessageBox.showerror(None, "Invalid Input", f"Exon length must be a multiple of 3: {x}:{y}")
            raise ValueError(f"Exon length must be a multiple of 3: {x}:{y}")
    print(f"splitted coding positions is {nested_list}")
    try:
        if all(isinstance(item, tuple) and all(isinstance(i, int) for i in item) for item in nested_list):
            return nested_list
        else:
            ModernMessageBox.showerror(None, "Invalid Input", f"Invalid coding positions string: {pos_str}")
            raise ValueError(f"Invalid coding positions string: {pos_str}")
    except ValueError as e:
        ModernMessageBox.showerror(None, "Invalid Input", str(e))
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

def get_trimmed_codingpos(codingpos, triml, trimr, dnalen):
    new_codingpos = []
    if triml == 0 and trimr == 0:
        return codingpos
    if trimr != 0:
        trimrpos = dnalen - trimr
        for exon_pos in codingpos:
            if trimrpos >= exon_pos[1]:
                new_codingpos.append(exon_pos)
            elif trimrpos >= exon_pos[0] and trimrpos < exon_pos[1]:
                cut_len = exon_pos[1] - trimrpos
                if cut_len % 3 == 0:
                    if exon_pos[0] + 2 < trimrpos:
                        new_codingpos.append((exon_pos[0], trimrpos))
                elif cut_len % 3 == 1:
                    if exon_pos[0] + 3 <= trimrpos - 2:
                        new_codingpos.append((exon_pos[0], trimrpos - 2))
                elif cut_len % 3 == 2:
                    if exon_pos[0] + 3 <= trimrpos - 1:
                        new_codingpos.append((exon_pos[0], trimrpos - 1))
                break
        codingpos = new_codingpos
    if triml != 0:
        new_codingpos = []
        trimlpos = triml
        for exon_pos in codingpos:
            if trimlpos >= exon_pos[1]:
                pass
            elif trimlpos >= exon_pos[0] and trimlpos < exon_pos[1]:
                cut_len = triml - exon_pos[0]
                new_start = 0
                if cut_len % 3 == 0:
                    new_start = triml
                    if new_start + 2 < exon_pos[1]:
                        new_codingpos.append((new_start, exon_pos[1]))
                    else:
                        pass
                elif cut_len % 3 == 1:
                    new_start = triml + 2
                    if new_start + 2 < exon_pos[1]:
                        new_codingpos.append((new_start, exon_pos[1]))
                    else:
                        pass
                elif cut_len % 3 == 2:
                    new_start = triml + 1
                    if new_start + 2 < exon_pos[1]:
                        new_codingpos.append((new_start, exon_pos[1]))
                    else:
                        pass
            else:
                new_codingpos.append(exon_pos)
        new_codingpos = [(exon_pos[0] - triml, exon_pos[1] - triml) for exon_pos in new_codingpos]
    return new_codingpos
        
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

def extract_sap_pos_from_snp_pos_list(snp_pos_list, exon_pos_list):
    ori_snp_pos_in_exon = []
    for snp_pos in snp_pos_list:
        for exon_pos in exon_pos_list:
            if exon_pos[0] <= snp_pos < exon_pos[1]:
                ori_snp_pos_in_exon.append(snp_pos)
                break
    intron_len = 0
    cur_snp_pos_list = []
    for idx, exon_pos in enumerate(exon_pos_list):
        if idx == 0:
            intron_len = exon_pos[0]
        else:
            prev_exon_pos = exon_pos_list[idx - 1]
            intron_len += exon_pos[0] - prev_exon_pos[1]
        for snp_pos in ori_snp_pos_in_exon:
            if exon_pos[0] <= snp_pos < exon_pos[1]:
                cur_snp_pos_list.append(snp_pos - intron_len)
    
    cur_sap_pos_list = [pos // 3 for pos in cur_snp_pos_list]        
    return sorted(set(cur_sap_pos_list))

def process_sample_for_pool(args):
    sam, vdic = args
    # No output_queue here! Only return results.
    return sam, pd.concat([df.dropna(axis=1, how='all') for df in vdic.values()], axis=0, ignore_index=True)

def populate_mar_sam_microhap(mar, samples, mar_mh_df, ref_mt, cur = True)->pd.DataFrame:
    tmp_df = pd.DataFrame(columns=['locus','mh_label','mh_seq', 'mh_id', 'mp_label', 'mp_seq', 'mp_id'])
    try:
        if cur:
            mar_sam_microhap=set()#microhap seqs
            for sam in samples:
                mar_sam_microhap_df = mar_mh_df.loc[mar_mh_df['sample'] == sam]
                zygo= mar_sam_microhap_df['zygosity'].iloc[0]
                if zygo == "homo":
                    mar_sam_microhap.add(mar_sam_microhap_df['mh_seq'].iloc[0])
                elif zygo == "heter":
                    mar_sam_microhap.add(mar_sam_microhap_df['mh_seq'].iloc[0])
                    mar_sam_microhap.add(mar_sam_microhap_df['mh_seq'].iloc[1])
            if mar_sam_microhap is not None and len(mar_sam_microhap) != 0:
                mar_sam_microhap = sorted(mar_sam_microhap)
            
            mar_sam_micropep = []
            mar_sam_micropep_label = []
            mar_sam_micropep_id = []
            if len(mar_sam_microhap) !=0:
                if ref_mt is not None and ref_mt.get_has_exon():
                    for nt_seq in mar_sam_microhap:
                        _, aa_seq = trans_single_dna(nt_seq, ref_mt.get_cur_exon_pos())
                        mar_sam_micropep.append(aa_seq)
                    uniq_peps = sorted(list(set(mar_sam_micropep)))
                    for pep in mar_sam_micropep:
                        mar_sam_micropep_id.append(uniq_peps.index(pep))
                    mar_sam_micropep_label = [f'mp_{i}' for i in mar_sam_micropep_id]
                else:
                    mar_sam_micropep = [""] * len(mar_sam_microhap)
                    mar_sam_micropep_label = [""] * len(mar_sam_microhap)
                    mar_sam_micropep_id = [""] * len(mar_sam_microhap)
                tmp_df=pd.DataFrame({
                                'locus':[mar]*len(mar_sam_microhap),
                                'mh_label':[f'mh_{i}' for i in range(len(mar_sam_microhap))],
                                'mh_seq':mar_sam_microhap,
                                'mh_id': [i for i in range(len(mar_sam_microhap))],
                                'mp_label':mar_sam_micropep_label,
                                'mp_seq':mar_sam_micropep,
                                'mp_id':mar_sam_micropep_id})
        else:
            if mar_mh_df is None :
                return tmp_df
            tmp_df = mar_mh_df.reset_index(drop=True)
            tmp_df = tmp_df.drop_duplicates(subset='mh_seq')
            tmp_df.columns = ['locus','mh_label','mh_seq', 'mh_id', 'mp_label', 'mp_seq', 'mp_id']
        if tmp_df is None or len(tmp_df) == 0:
            return tmp_df
        tmp_df = tmp_df.sort_values(by="mh_id").reset_index(drop=True)
    except Exception as e:
        print(f"Error in populate_mar_sam_microhap for marker {mar}: {e}", flush=True)
        traceback.print_exc()
        raise(e)
    return tmp_df
def populate_each_mar_mp_dict(mar, records, mar_combo_mt) -> tuple:
    final_sam_cur_mp_dict = {}
    final_sam_cur_mp_sim_dict = {}
    cur_mar_mp_df = pd.DataFrame.from_records(records)
    if cur_mar_mp_df.empty:
        return final_sam_cur_mp_dict, final_sam_cur_mp_sim_dict
    for sam in sorted(cur_mar_mp_df['sample'].unique()):
        tmp_df = cur_mar_mp_df[cur_mar_mp_df['sample'] == sam].reset_index(drop=True)
        zygo = tmp_df['zygosity'].iloc[0]
        if zygo == 'homo':
            tmp_df.loc[0, 'baseChange'] = ""
            if tmp_df.shape[0] > 1:
                tmp_df.loc[1, 'mprop'] = 0
                tmp_df.loc[1, 'baseChange'] = ""
        else:
            mh_seq1 = tmp_df['mh_seq'].iloc[0]
            mh_seq2 = tmp_df['mh_seq'].iloc[1] if tmp_df.shape[0] > 1 else None

            combo1 = mar_combo_mt.get(mh_seq1, None)
            mp1 = combo1.get_micropep() if combo1 is not None else None
            sap_str1 = mp1.get_var_nm_str() if mp1 is not None else ""

            combo2 = mar_combo_mt.get(mh_seq2, None) if mh_seq2 is not None else None
            mp2 = combo2.get_micropep() if combo2 is not None else None
            sap_str2 = mp2.get_var_nm_str() if mp2 is not None else ""

            if tmp_df.shape[0] > 1:
                tmp_df['baseChange'] = [sap_str1, sap_str2]
            else:
                tmp_df['baseChange'] = [sap_str1]
            if zygo == 'heter':
                mp_seq1 = tmp_df['mp_seq'].iloc[0]
                mp_seq2 = tmp_df['mp_seq'].iloc[1] if tmp_df.shape[0] > 1 else None
                if mp_seq1 not in ("", None):
                    read1 = tmp_df['read'].iloc[0]
                    read2 = tmp_df['read'].iloc[1]
                    rprop = round((read1 + read2) / tmp_df['readt'].iloc[0], 4)
                    if mp_seq1 == mp_seq2:
                        tmp_df['zygosity'] = ['homo', 'homo']
                        tmp_df['read'] = [read1 + read2, 0]
                        tmp_df['rprop'] = [rprop, 0]
                        tmp_df['mprop'] = [1, 0]
                    else:
                        tmp_df.loc[1, 'mprop'] = 0
                else:
                    tmp_df['zygosity'] = ['inconclusive', 'inconclusive']
        tmp_df.drop(columns=['mh_seq'], inplace=True)
        final_sam_cur_mp_dict[sam] = tmp_df
        tmp_sim_df = tmp_df[['sample', 'allele', 'zygosity']].copy()
        sim_df = pd.DataFrame(columns=['sample', f'{mar}_allele1', f'{mar}_allele2'])
        zygo = tmp_sim_df['zygosity'].iloc[0]
        if zygo == 'homo':
            sim_df = pd.concat([sim_df, pd.DataFrame([[sam, tmp_sim_df['allele'].iloc[0], tmp_sim_df['allele'].iloc[0]]], columns=sim_df.columns)], ignore_index=True)
        elif zygo == 'heter':
            sim_df = pd.concat([sim_df, pd.DataFrame([[sam, tmp_sim_df['allele'].iloc[0], tmp_sim_df['allele'].iloc[1]]], columns=sim_df.columns)], ignore_index=True)
        else:
            sim_df = pd.concat([sim_df, pd.DataFrame([[sam, '-9', '-9']], columns=sim_df.columns)], ignore_index=True)
        final_sam_cur_mp_sim_dict[sam] = sim_df
    return final_sam_cur_mp_dict, final_sam_cur_mp_sim_dict

def populate_each_mar_mh_dict(mar, records) -> tuple:
    final_sam_cur_mh_dict = {}
    final_sam_cur_mh_sim_dict = {}
    cur_mar_mh_df = pd.DataFrame.from_records(records)
    if cur_mar_mh_df.empty:
        return final_sam_cur_mh_dict, final_sam_cur_mh_sim_dict
    for sam in sorted(cur_mar_mh_df['sample'].unique()):
        tmp_df = cur_mar_mh_df[cur_mar_mh_df['sample'] == sam].reset_index(drop=True)
        final_sam_cur_mh_dict[sam] = tmp_df
        tmp_sim_df = tmp_df[['sample', 'allele', 'zygosity']].copy()
        zygo = tmp_sim_df['zygosity'].iloc[0]
        if zygo == 'homo':
            if tmp_sim_df.shape[0] == 1:
                tmp_sim_df = pd.concat([tmp_sim_df, tmp_sim_df], ignore_index=True)
            else:
                tmp_sim_df.iloc[1, tmp_sim_df.columns.get_loc('allele')] = tmp_sim_df.iloc[0]['allele']
        elif zygo == 'heter':
            tmp_sim_df = tmp_sim_df.sort_values(by='allele')
        else:
            tmp_sim_df.loc[:, 'allele'] = '-9'
        tmp_sim_df = tmp_sim_df.drop(columns='zygosity')
        tmp_sim_df = tmp_sim_df.pivot_table(
            index='sample',
            columns=tmp_sim_df.groupby('sample').cumcount(),
            values='allele',
            aggfunc='first'
        ).reset_index()
        tmp_sim_df.columns = ['sample', f'{mar}_allele1', f'{mar}_allele2']
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

def training_each_model_clf(df, micro_type):
    if micro_type == "snp":
        X_tot = df.drop(['locus', 'zygosity'], axis = 1)
        y = df['zygosity']
        X_train,X_test, y_train, y_test = train_test_split(X_tot, y, test_size = 0.2, random_state = 42, stratify=y)
        clf = GradientBoostingClassifier(random_state = 42)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        return [clf, accuracy]
    elif micro_type == "sat":
        pass
