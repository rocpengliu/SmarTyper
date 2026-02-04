import customtkinter as ctk
import tkinter as tk
import os
from ..utils.utils_func import load_pdf
from ..utils.mouse import _on_mousewheel

def update_all_reads_qual_distri(parent,show_panel,type):
    print(f"starting to update_all_reads_qual_distri")
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

    # Bind mouse wheel and keyboard events for scrolling (only when mouse is over the canvas)
    canvas.bind('<MouseWheel>', lambda event: _on_mousewheel(canvas, event))
    canvas.bind('<Button-4>', lambda event: _on_mousewheel(canvas, event))
    canvas.bind('<Button-5>', lambda event: _on_mousewheel(canvas, event))

    def _on_arrow(event):
        if hasattr(canvas, 'yview_scroll'):
            if event.keysym == 'Down':
                canvas.yview_scroll(1, "units")
            elif event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
    canvas.bind('<Down>', _on_arrow)
    canvas.bind('<Up>', _on_arrow)
    load_pdf_from_here(genoclass,canvas,type)
    print(f"finished to update_all_reads_qual_distri")

def load_pdf_from_here(genoclass,canvas,fig_type):
    suffix=""
    if fig_type =="qual":
        suffix="All_sample_read_quality.pdf"
    elif fig_type=="distri":
        suffix="All_sample_read_distribution.pdf"
    else:
        return
    pdf_file_path=os.path.join(genoclass.get_parameter().get_outputdir(),suffix)
    if not os.path.exists(pdf_file_path):
        return
    load_pdf(pdf_file_path,canvas)