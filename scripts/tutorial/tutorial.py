import customtkinter as ctk
import tkinter as tk
from scripts.utils.colors import COLORS
from scripts.utils.common import module_font
import fitz
from PIL import Image, ImageTk

import os

def create_tutorial_module(parent):
    page = ctk.CTkFrame(parent, fg_color=COLORS['background'])
    page.grid_rowconfigure(0, weight=0)
    page.grid_rowconfigure(1, weight=1)
    page.grid_rowconfigure(2, weight=0)
    page.grid_columnconfigure(0, weight=1)
    
    # Tutorial title label with modern styling
    label = ctk.CTkLabel(page, text="★ Tutorial of SmarTyper", font=module_font, 
                         fg_color="transparent", text_color=COLORS['tutorial_peach'])
    label.grid(row=0, column=0, pady=(30, 10), padx=(40, 50), sticky="n")

    # Display the tutorial PDF one slide at a time.
    pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "tutorial",
        "smartyper_tutorial.pdf",
    )
    if os.path.exists(pdf_path):
        container = ctk.CTkFrame(page, fg_color="white")
        container.grid(row=1, column=0, pady=(10, 30), padx=20, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        doc = fitz.open(pdf_path)
        pdf_pages = []
        for page_num in range(len(doc)):
            pdf_page = doc.load_page(page_num)
            pix = pdf_page.get_pixmap()
            pdf_pages.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
        doc.close()

        nav_frame = ctk.CTkFrame(page, fg_color="transparent")
        nav_frame.grid(row=2, column=0, pady=(0, 20), padx=20, sticky="ew")
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(1, weight=0)
        nav_frame.grid_columnconfigure(2, weight=1)

        page_index = {'value': 0}
        page_text = ctk.StringVar(value=f"Page 1 / {len(pdf_pages)}")
        page_label = ctk.CTkLabel(nav_frame, textvariable=page_text, font=("Segoe UI", 14))
        page_label.grid(row=0, column=1, padx=12)

        prev_button = ctk.CTkButton(nav_frame, text="Previous", width=110)
        prev_button.grid(row=0, column=0, sticky="e", padx=(0, 12))

        next_button = ctk.CTkButton(nav_frame, text="Next", width=110)
        next_button.grid(row=0, column=2, sticky="w", padx=(12, 0))

        def update_nav_state():
            idx = page_index['value']
            page_text.set(f"Page {idx + 1} / {len(pdf_pages)}")
            prev_button.configure(state="normal" if idx > 0 else "disabled")
            next_button.configure(state="normal" if idx < len(pdf_pages) - 1 else "disabled")

        def render_current_page(event=None):
            canvas.delete("all")
            pil_img = pdf_pages[page_index['value']]
            canvas_w = max(canvas.winfo_width(), 1)
            canvas_h = max(canvas.winfo_height(), 1)

            img_w, img_h = pil_img.size
            scale = min((canvas_w - 30) / img_w, (canvas_h - 30) / img_h)
            scale = max(scale, 0.1)
            new_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
            resized = pil_img.resize(new_size, Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(resized)
            canvas.image_ref = img_tk

            x_offset = (canvas_w - new_size[0]) // 2
            y_offset = (canvas_h - new_size[1]) // 2
            canvas.create_image(x_offset, y_offset, anchor="nw", image=img_tk)
            update_nav_state()

        def show_prev_page():
            if page_index['value'] > 0:
                page_index['value'] -= 1
                render_current_page()

        def show_next_page():
            if page_index['value'] < len(pdf_pages) - 1:
                page_index['value'] += 1
                render_current_page()

        def on_wheel(event):
            delta = getattr(event, 'delta', 0)
            num = getattr(event, 'num', None)
            if num == 4 or delta > 0:
                show_prev_page()
            elif num == 5 or delta < 0:
                show_next_page()
            return "break"

        prev_button.configure(command=show_prev_page)
        next_button.configure(command=show_next_page)
        canvas.bind('<Configure>', render_current_page)
        canvas.bind('<Left>', lambda event: show_prev_page())
        canvas.bind('<Right>', lambda event: show_next_page())
        canvas.bind('<MouseWheel>', on_wheel)
        canvas.bind('<Button-4>', on_wheel)
        canvas.bind('<Button-5>', on_wheel)
        canvas.focus_set()

        render_current_page()
    else:
        err_label = ctk.CTkLabel(page, text="Tutorial PDF not found.", font=("Segoe UI", 16), text_color="red")
        err_label.grid(row=1, column=0, pady=(10, 30), padx=20, sticky="n")
    
    return page