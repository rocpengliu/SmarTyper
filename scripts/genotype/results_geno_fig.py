import customtkinter as ctk
import tkinter as tk
import os
import matplotlib
matplotlib.use("Agg") 
from ..utils.utils_func import load_pdf, produce_fig_sam_mar_pdf, produce_fig_mar_sam_pdf
from ..utils.mouse import _on_mousewheel


def update_geno_figs(parent, fig_tab_bottom_panel):
    """Update the genotype figures in the given panel."""
    print("starting to update_geno_figs")
    genoclass = parent.master.genotype_class
    
    # Clear existing widgets
    for widget in fig_tab_bottom_panel.winfo_children():
        widget.destroy()
    for rid in range(fig_tab_bottom_panel.grid_size()[1]):
        fig_tab_bottom_panel.grid_rowconfigure(rid,weight=0)
    for cid in range(fig_tab_bottom_panel.grid_size()[0]):
        fig_tab_bottom_panel.grid_columnconfigure(cid,weight=0)
    fig_tab_bottom_panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)  # Ensure both horizontal and vertical expansion
    fig_tab_bottom_panel.grid_rowconfigure(0, weight=1)  # Ensure vertical expansion
    fig_tab_bottom_panel.grid_columnconfigure(0, weight=1)  # Ensure horizontal expansion
    
    if not produce_fig_pdf(genoclass):
        return
    
    # Create a container frame for the canvas
    container = ctk.CTkFrame(fig_tab_bottom_panel, fg_color="transparent")
    container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    
    # Create a canvas widget
    canvas = tk.Canvas(container, bg="white")
    canvas.grid(row=0, column=0, sticky="nsew")

    # Create scrollbars
    v_scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)

    # Place scrollbars
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    # Configure canvas scrollbars
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    # Bind mouse wheel and keyboard events for scrolling (only when mouse is over the canvas)
        # Linux uses Button-4 and Button-5, Windows/Mac use MouseWheel
    canvas.bind('<MouseWheel>', lambda event: _on_mousewheel(canvas, event))  # Windows/Mac
    canvas.bind('<Button-4>', lambda event: _on_mousewheel(canvas, event))    # Linux scroll up
    canvas.bind('<Button-5>', lambda event: _on_mousewheel(canvas, event))    # Linux scroll down

    # Optionally, bind up/down keys
    def _on_arrow(event):
        if hasattr(canvas, 'yview_scroll'):
            if event.keysym == 'Down':
                canvas.yview_scroll(1, "units")
            elif event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
    canvas.bind('<Down>', _on_arrow)
    canvas.bind('<Up>', _on_arrow)

    # Load the PDF into the canvas
    load_pdf_from_here(genoclass, canvas)

    print("finished to update_geno_figs")

def load_pdf_from_here(genoclass,canvas):
    sam_mar = ""
    if genoclass.get_res_param().get_res_type() == "sample":
        sam_mar = genoclass.get_res_param().get_sample()+"_sample"
    elif genoclass.get_res_param().get_res_type() == "marker":
        sam_mar = genoclass.get_res_param().get_marker()+"_marker"
    else:
        return
    pdf_file_path = os.path.join(genoclass.get_parameter().get_outputdir(), f"{sam_mar}_genotype.pdf")
    if not os.path.exists(pdf_file_path):
        return
    load_pdf(pdf_file_path, canvas)

def produce_fig_pdf(genoclass)->bool:
    """Generate the PDF figures based on the genotype class."""
    # Determine the type of results being generated (sample or marker)
    if genoclass.get_res_param().get_res_type() == "sample":
        selected_sample = genoclass.get_res_param().get_sample()
        if not selected_sample:
            return False
        return produce_fig_sam_mar_pdf(genoclass, selected_sample, 'snp')
    elif genoclass.get_res_param().get_res_type() == "marker":
        selected_marker = genoclass.get_res_param().get_marker()
        if not selected_marker:
            return False
        return produce_fig_mar_sam_pdf(genoclass,selected_marker, 'snp')
    return False