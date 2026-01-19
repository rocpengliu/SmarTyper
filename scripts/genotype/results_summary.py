from ..utils.common import parent_button_size, child_button_size, bfont, bmbfont,bmfont, brfont, header_font, confirm_button_font, pnbuttonfont
from ..utils.colors import COLORS
import customtkinter as ctk
import tkinter as tk
import os


def results_summary(parent):
    frame = ctk.CTkFrame(parent, fg_color=COLORS['background'])
    frame.grid(row=0, column=0, sticky="nsew")
    
    # Configure grid row and column weights for expansion
    frame.grid_rowconfigure(0, weight=0)  # Header row does not expand
    frame.grid_rowconfigure(1, weight=1)  # Body row expands
    frame.grid_rowconfigure(2, weight=0)  # Footer row does not expand
    frame.grid_columnconfigure(0, weight=1)  # Center content horizontally
    frame.grid_columnconfigure(1, weight=1)
    
    frame.header_frame = create_header(frame)
    frame.body_frame = create_body(parent, frame)
    frame.footer_frame = create_footer(parent, frame)
    return frame

def create_header(frame):
    header_frame = ctk.CTkFrame(frame, fg_color=COLORS['card'], corner_radius=12)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(15, 10), padx=(15, 15))
    header_frame.grid_columnconfigure(0, weight=1)  # Center header content
    
    label = ctk.CTkLabel(header_frame, text="◙ Result Summary", font=header_font,
                         fg_color="transparent", text_color=COLORS['primary'])
    label.pack(side=tk.LEFT, pady=(15, 15), padx=(30, 10))
    return header_frame

def create_footer(parent, frame):
    footer_frame = ctk.CTkFrame(frame, fg_color="transparent")
    footer_frame.grid(row=2, column=0, columnspan=2, pady=(10,10), padx=(15, 15), sticky="ew")
    
    # Configure footer_frame to center its content
    footer_frame.grid_rowconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(0, weight=1)
    footer_frame.grid_columnconfigure(1, weight=1)
    
    # Previous Button
    footer_frame.previous_button = ctk.CTkButton(footer_frame, text="← Previous", font=pnbuttonfont,
                                    fg_color=COLORS['primary'], hover_color=COLORS['secondary'],
                                    corner_radius=10, height=child_button_size['height'], width=child_button_size['width'],
                                    command = lambda:parent.master.show_page("results"))
    footer_frame.previous_button.grid(row=0, column=0, padx=(10, 100), sticky="e")
    
    return footer_frame

def create_body(parent, frame):
    genotype_class = parent.master.genotype_class
    
    body_frame = ctk.CTkFrame(frame, fg_color="transparent")
    body_frame.padx = (10, 10)
    body_frame.pady = (5, 5)
    body_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(2,2))
    
    body_frame.grid_rowconfigure(0, weight=1) #top panel
    body_frame.grid_rowconfigure(1, weight=6) # bottom panel
    body_frame.grid_columnconfigure(0, weight=1) # top and bottom panels
    
    top_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    top_panel.grid(row=0, column=0, sticky="nsw", padx=body_frame.padx, pady=(0,0))
    #top_panel.grid_propagate(False)
    
    bottom_panel = ctk.CTkFrame(body_frame, fg_color="transparent")
    bottom_panel.grid(row=1, column=0, sticky="nsew", padx=body_frame.padx,pady=(0,0))
    
    top_panel.grid_columnconfigure(0, weight=1) #right panel
    top_panel.grid_rowconfigure('all', weight=1)
    
    # Configure the bottom panel (full width)
    bottom_panel.grid_columnconfigure(0, weight=1)
    bottom_panel.grid_rowconfigure(0, weight=1)
    
    row = 0
    
    #confirm button
    
    ctk.CTkLabel(top_panel, text="For microhap identification", font=bfont, text_color="white").grid(row=row, column=0, padx=body_frame.padx, pady=(10,10), sticky="e")
    ctk.CTkButton(top_panel, text="Let's Go",font=confirm_button_font, height=parent_button_size['height'], width=parent_button_size['width'],
                  fg_color=COLORS['primary'], hover_color=COLORS['secondary'], corner_radius=10,
                  command=lambda: go_button(parent)).grid(row=row, column=1, pady=(10,10), padx=(0,10), sticky="w")
    return body_frame

def go_button(parent):
    genoclass = parent.master.genotype_class
    panel = parent.master.pages.get('microtype_data', None)
    if panel is not None:
        panel.body_frame.top_panel.loci_entry.delete(0, 'end')
        panel.body_frame.top_panel.loci_entry.insert(0, genoclass.get_parameter().get_locifile())
        genoclass.get_metadata().read_locifile(genoclass.get_parameter(), genoclass.get_post_microhap(), True)
        if genoclass.get_parameter().get_outputdir() and os.path.isdir(genoclass.get_parameter().get_outputdir()):
            fpath = os.path.join(genoclass.get_parameter().get_outputdir(), 'All_sample_final_genotype.txt')
            if os.path.isfile(fpath):
                genoclass.get_parameter().set_cur_microhap_input_file(fpath)
                panel.body_frame.top_panel.in_entry.delete(0, 'end')
                panel.body_frame.top_panel.in_entry.insert(0, fpath)
                genoclass.get_metadata().read_cur_microhap_file(genoclass.get_parameter())
    parent.master.show_page("microtype_data")