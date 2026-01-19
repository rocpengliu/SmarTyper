import customtkinter as ctk
from ..utils.colors import COLORS
from ..utils.common import module_font

def create_genotype_module(parent):
    page = ctk.CTkFrame(parent, fg_color=COLORS['background'])
    page.grid_rowconfigure(0, weight=1)  # Allow row to expand
    page.grid_rowconfigure(1, weight=1)
    page.grid_rowconfigure(2, weight=1)
    page.grid_columnconfigure(0, weight=1)  # Allow column to expand
    
    # Genotype title label with modern styling
    label = ctk.CTkLabel(page, text="◆ Genotype Module", font=module_font, 
                         fg_color="transparent", text_color=COLORS['primary'])
    label.grid(row=0, column=0, pady=(30, 10), padx=(40, 50), sticky="n")
    
    return page