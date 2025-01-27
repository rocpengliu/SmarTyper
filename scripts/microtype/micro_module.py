import customtkinter as ctk

def create_micro_module(parent):
    page = ctk.CTkFrame(parent, fg_color="#3b3b3b")
    page.grid_rowconfigure(0, weight=1)  # Allow row to expand
    page.grid_rowconfigure(1, weight=1)
    page.grid_rowconfigure(2, weight=1)
    page.grid_columnconfigure(0, weight=1)  # Allow column to expand
    
    # Project title label
    label = ctk.CTkLabel(page, text="Project Module", font=("Helvetica", 20, "bold"), 
                         fg_color="#3b3b3b", text_color="blue")
    label.grid(row=0, column=0, pady=(30, 10), padx=(40, 50), sticky="n")
    
    return page