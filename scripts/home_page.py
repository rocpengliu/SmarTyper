import customtkinter as ctk
import tkinter.font as tkfont

def create_home(parent):
    default_font45 = ("Segoe UI", 45, "bold")
    default_font15 = ("Segoe UI", 15, "bold")
    default_font30 = ("Segoe UI", 30, "bold")
    default_font25 = ("Segoe UI", 25, "bold")
    page = ctk.CTkFrame(parent, fg_color="#3b3b3b")
    page.grid_columnconfigure((0, 1, 2, 3), weight=1)
    page.grid_rowconfigure(0, weight=1)  # Header row will expand
    page.grid_rowconfigure(1, weight=3)  # Content row will expand
    page.grid_rowconfigure(2, weight=1)  # Extra row to push buttons up

    # Header Frame
    header_frame = ctk.CTkFrame(page, fg_color="#3b3b3b")
    header_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")
    header_frame.grid_columnconfigure(0, weight=1)  # Make header frame expandable
    header_frame.grid_rowconfigure(0, weight=1)

    # Content Frame
    content_frame = ctk.CTkFrame(page, fg_color="#3b3b3b")
    content_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
    content_frame.grid_columnconfigure((0, 1), weight=1)  # Columns in content_frame are expandable
    content_frame.grid_rowconfigure(0, weight=1)  # Row in content_frame is expandable

    # Spacer Frame
    spacer_frame = ctk.CTkFrame(page, fg_color="#3b3b3b")
    spacer_frame.grid(row=2, column=0, columnspan=4, sticky="nsew")
    
    # Header Labels
    header_label1 = ctk.CTkLabel(header_frame, text="Welcome to SmarTyper!", font=default_font45,
                                 fg_color="#3b3b3b", text_color="green")
    header_label1.pack(pady=(20, 10), padx=(50, 20), anchor="center")

    header_label2 = ctk.CTkLabel(header_frame, text="A smart platform for genotyping and comprehensive data statistics and visualization!",
                                 font=default_font25, fg_color="#3b3b3b", text_color="green")
    header_label2.pack(pady=(5, 5), padx=(50, 10), anchor="center")

    header_label3 = ctk.CTkLabel(header_frame, text="--powered by Bioinforlligence", font=default_font15,
                                 fg_color="#3b3b3b", text_color="green")
    header_label3.pack(pady=(5, 20), padx=(50, 20), anchor="center")

    # Place buttons side by side within the content_frame
    size = 100
    data_loader_btn = ctk.CTkButton(content_frame, text="Genotype", width=size*2, height=size, font=default_font30,
                                    command=lambda: parent.master.show_page("genotype"))
    data_loader_btn.grid(row=0, column=0, padx=(50, 25), pady=(10, 10), sticky="e")
    
    project_opener_btn = ctk.CTkButton(content_frame, text="Machine Learning", width=size*2, height=size, font=default_font30,
                                        command=lambda: parent.master.show_page("machine learning"))
    project_opener_btn.grid(row=0, column=1, padx=(50, 25), pady=(10, 10), sticky="w")

    project_opener_btn = ctk.CTkButton(content_frame, text="Microtype", width=size*2, height=size, font=default_font30,
                                        command=lambda: parent.master.show_page("microtype"))
    project_opener_btn.grid(row=1, column=0, padx=(50, 25), pady=(10, 10), sticky="e")
    
    microtype_btn = ctk.CTkButton(content_frame, text="Project", width=size*2, height=size, font=default_font30,
                                    command=lambda: parent.master.show_page("project"))
    microtype_btn.grid(row=1, column=1, padx=(50, 25), pady=(10, 10), sticky="w")

    return page
