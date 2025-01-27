import customtkinter as ctk

def project_loader(parent):
    page = ctk.CTkFrame(parent, fg_color="#3b3b3b")
    label = ctk.CTkLabel(page, text="Project Loading!", font=("Helvetica", 20, "bold"),
                         fg_color="#3b3b3b", text_color="green")
    label.grid(row=0, column=1, pady=20, padx=20, sticky="nsew")
    
    return page