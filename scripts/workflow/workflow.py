import customtkinter as ctk
from scripts.utils.colors import COLORS
from scripts.utils.common import module_font

from PIL import Image
import os

def create_wkfl_module(parent):
    page = ctk.CTkFrame(parent, fg_color=COLORS['background'])
    page.grid_rowconfigure(0, weight=1)  # Allow row to expand
    page.grid_rowconfigure(1, weight=1)
    page.grid_rowconfigure(2, weight=1)
    page.grid_columnconfigure(0, weight=1)  # Allow column to expand
    
    # Machine Learning title label with modern styling
    label = ctk.CTkLabel(page, text="★ Main Workflow of SmarTyper", font=module_font, 
                         fg_color="transparent", text_color=COLORS['workflow_cherry'])
    label.grid(row=0, column=0, pady=(30, 10), padx=(40, 50), sticky="n")

    # Display the workflow image
    img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "images", "smartyper_workflow.jpg")
    if os.path.exists(img_path):
        pil_img_orig = Image.open(img_path)
        img_label = ctk.CTkLabel(page, text="")
        img_label.grid(row=1, column=0, pady=(10, 30), padx=20, sticky="nsew")

        def resize_image(event=None):
            # Get available size from the frame
            frame_w = page.winfo_width() or 800
            frame_h = page.winfo_height() or 600
            # Leave some space for label and padding
            avail_w = max(frame_w - 80, 100)
            avail_h = max(frame_h - 180, 100)
            img_w, img_h = pil_img_orig.size
            scale = min(avail_w / img_w, avail_h / img_h, 1.0)
            new_size = (int(img_w * scale), int(img_h * scale))
            pil_img = pil_img_orig.resize(new_size, Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=new_size)
            img_label.configure(image=ctk_img)
            img_label.image = ctk_img  # Prevent garbage collection

        page.bind('<Configure>', resize_image)
        resize_image()
    else:
        err_label = ctk.CTkLabel(page, text="Workflow image not found.", font=("Segoe UI", 16), text_color="red")
        err_label.grid(row=1, column=0, pady=(10, 30), padx=20, sticky="n")
    
    return page