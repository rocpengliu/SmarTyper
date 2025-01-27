import customtkinter as ctk
import tkinter as tk
import os
from ..utils.utils_func import load_pdf

def update_all_reads_qual_distri(parent,show_panel,type):
    print("starting to update_all_reads_qual_distri")
    for widget in show_panel.winfo_children():
        widget.destroy()
    genoclass=parent.master.genotype_class
    
    container=ctk.CTkFrame(show_panel,fg_color="white")
    container.grid(row=0,column=0,sticky="news",padx=5,pady=5)
    container.grid_rowconfigure(0,weight=1)
    container.grid_columnconfigure(0,weight=1)
    
    canvas=tk.Canvas(container,bg="white")
    canvas.grid(row=0,column=0,sticky="news",padx=5,pady=5)
    
    v_scrollbar=tk.Scrollbar(container,orient="vertical",command=canvas.yview)
    h_scrollbar=tk.Scrollbar(container,orient="horizontal",command=canvas.xview)
    v_scrollbar.grid(row=0,column=1,sticky="ns")
    h_scrollbar.grid(row=1,column=0,sticky="ew")
    
    canvas.configure(yscrollcommand=v_scrollbar.set,xscrollcommand=h_scrollbar.set)
    load_pdf_from_here(genoclass,canvas,type)
    
    def universal_scroll(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", universal_scroll)
    canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
    print("finished to update_all_reads_qual_distri")

def load_pdf_from_here(genoclass,canvas,fig_type):
    suffix=""
    if fig_type =="qual":
        suffix="all_sample_read_quality.pdf"
    elif fig_type=="distri":
        suffix="all_sample_read_distribution.pdf"
    else:
        return
    pdf_file_path=os.path.join(genoclass.get_parameter().get_outputdir(),suffix)
    if not os.path.exists(pdf_file_path):
        return
    load_pdf(pdf_file_path,canvas)