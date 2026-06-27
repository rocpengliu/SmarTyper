import platform
if platform.system() == "Windows":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # or -4
    except Exception:
        pass

import customtkinter as ctk
from customtkinter import CTkImage
import tkinter as tk
import argparse
import json
import os
import multiprocessing as mp

from scripts.home_page import create_home
from scripts.genotype.genotype_module import create_genotype_module
from scripts.genotype.data_loader import data_loader
from scripts.genotype.parameter_setter import parameter_setter
from scripts.genotype.job_runner import job_runner
from scripts.genotype.results_viewer import results_viewer
from scripts.genotype.results_summary import results_summary
from scripts.project.project_loader import project_loader
from scripts.project.project_module import create_project_module
from scripts.microtype.micro_module import create_micro_module
from scripts.microtype.micro_loader import micro_loader
from scripts.microtype.micro_viewer import micro_viewer
from scripts.machine_learning.modeling_loader import modeling_loader
from scripts.machine_learning.machine_learning import create_ml_module
from scripts.workflow.workflow import create_wkfl_module
from scripts.tutorial.tutorial import create_tutorial_module
from scripts.utils.colors import COLORS
from PIL import Image, ImageTk, ImageOps, ImageEnhance
from scripts.class_modules.class_modules import GenotypeClass
ctk.set_appearance_mode("dark")


def _is_wsl() -> bool:
    if platform.system() != "Linux":
        return False
    release = platform.release().lower()
    if "microsoft" in release or "wsl" in release:
        return True
    try:
        with open("/proc/version", "r", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False


def collect_gui_diagnostics() -> dict:
    info = {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "is_wsl": _is_wsl(),
        "display": os.environ.get("DISPLAY", ""),
        "wayland_display": os.environ.get("WAYLAND_DISPLAY", ""),
        "xdg_session_type": os.environ.get("XDG_SESSION_TYPE", ""),
        "gdk_backend": os.environ.get("GDK_BACKEND", ""),
        "tk_scaling_env": os.environ.get("SMARTYPER_TK_SCALING", ""),
    }

    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.update_idletasks()
        info["tk_windowing_system"] = root.tk.call("tk", "windowingsystem")
        info["tk_scaling"] = float(root.tk.call("tk", "scaling"))
        info["tk_pixels_per_inch"] = float(root.winfo_fpixels("1i"))
        info["screen_width"] = int(root.winfo_screenwidth())
        info["screen_height"] = int(root.winfo_screenheight())
        max_w, max_h = root.maxsize()
        info["max_width"] = int(max_w)
        info["max_height"] = int(max_h)
    except Exception as e:
        info["diagnostic_error"] = str(e)
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass

    return info

class SmarTyperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide window during setup
        self.title("SmarTyper - Smart genotyper")
        self.setup_window()
        self.resizable(True,True)
        
        # Modern typography
        self.bfont = ("Segoe UI", 18, "bold")
        self.sfont = ("Segoe UI", 13, "bold")
        self.title_font = ("Segoe UI", 32, "bold")
        self.subtitle_font = ("Segoe UI", 14)
        
        self.default_fg_color = COLORS['primary']
        self.highlight_color = COLORS['accent'] 
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Left panel should not expand
        self.grid_columnconfigure(1, weight=1)  # Right panel should expand
        
        # Modern sidebar with gradient-like appearance
        self.left_panel = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLORS['sidebar'])
        self.left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 2))
        self.left_panel.grid_rowconfigure(0, minsize=200)  # Minimum size for the first row
        self.left_panel.grid_rowconfigure(1, weight=1)    # Push exit button down
        self.left_panel.grid_rowconfigure(999, weight=0)  # Last row weight as 0
        
        # Modern content area with better background
        self.right_panel = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS['background'])
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        # Do not grid right_panel yet; will grid after home page is ready
        
        self.genotype_class = GenotypeClass()
        
        self.parent_children = {
            "data": "genotyping",
            "parameters": "genotyping",
            "run": "genotyping",
            "results": "genotyping",
            "summary": "genotyping",
            "modeling": "machine learning",
            "microtype_data": "microtyping",
            "microtype_results": "microtyping",
            "loader": "project",
            "workflow_loader": "workflow",
            "tutorial_folder": "tutorial"
        }
        self.tab_names = ["home", "genotyping", "machine learning", "microtyping", "project", "workflow", "tutorial"]
        self.children_buttons = {
            "genotyping": ["data", "parameters", "run", "results", "summary"],
            "machine learning": ["modeling"],
            "microtyping": ["microtype_data", "microtype_results"],
            "project": ["loader"],
            "workflow": ["workflow_loader"],
            "tutorial": ["tutorial_folder"]
        }
        self.menu_expanded = {
            "genotyping": False,
            "microtyping": False,
            "machine learning": False,
            "project": False,
            "workflow": False,
            "tutorial": False
        }
        self.home_path = os.path.dirname(os.path.realpath(__file__))
        
        # Use simple Unicode symbols that are widely supported
        self.icon_symbols = {
            "home": "⌂",
            "genotyping": "◆",
            "project": "●",
            "microtyping": "◇",
            "machine learning": "★",
            "loader": "►",
            "run": "►",
            "parameters": "⚙",
            "data": "■",
            "modeling": "▲",
            "microtype_data": "■",
            "microtype_results": "◘",
            "results": "◘",
            "summary": "◙",
            "workflow_loader": "►",
            "tutorial_folder": "📁",
            "exit": "✕"
        }
        self.buttons = {}
        self.button_colors = {}  # Store original colors for each button
        self.children_button_refs = {}  # Store child button references
        self.create_tabs()
        
        # Create pages but don't display them yet
        self.pages = {
            "genotyping": create_genotype_module(self.right_panel),
            "data": data_loader(self.right_panel),
            "parameters": parameter_setter(self.right_panel),
            "run": job_runner(self.right_panel),
            "results": results_viewer(self.right_panel),
            "summary": results_summary(self.right_panel),
            "machine learning": create_ml_module(self.right_panel),
            "modeling": modeling_loader(self.right_panel),
            "microtyping": create_micro_module(self.right_panel),
            "microtype_data": micro_loader(self.right_panel),
            "microtype_results": micro_viewer(self.right_panel),
            "project": create_project_module(self.right_panel),
            "loader": project_loader(self.right_panel),
            "workflow_loader": create_wkfl_module(self.right_panel),
            "tutorial_folder": create_tutorial_module(self.right_panel)
            
        }
        # Ensure all pages are hidden initially
        for page in self.pages.values():
            page.grid_remove()
        
        # Create and show home page last
        self.pages["home"] = create_home(self.right_panel, self)
        self.pages["home"].grid(row=0, column=0, sticky="nswe")
        self.button_clicked("home")
        # Now show the right panel after home is ready
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.deiconify()  # Show window only after everything is ready

    def _maximize_window(self):
        try:
            self.state("zoomed")
            return
        except Exception:
            pass

        try:
            self.attributes("-zoomed", True)
            return
        except Exception:
            pass

        # Last-resort maximize fallback that works across X11/Wayland variants.
        try:
            max_w, max_h = self.maxsize()
            self.geometry(f"{max_w}x{max_h}+0+0")
        except Exception:
            pass

    def setup_window(self):
        screen_width=self.winfo_screenwidth()*0.4
        screen_height=self.winfo_screenheight()*0.6
        self.geometry(f"{screen_width}x{screen_height}")
        self.minsize(1280, 720)

        scaling_env = os.environ.get("SMARTYPER_TK_SCALING")
        if scaling_env:
            try:
                self.tk.call("tk", "scaling", float(scaling_env))
            except Exception:
                pass

        # Maximize window on launch
        self._maximize_window()
    def create_tabs(self):
        # Add logo/branding area
        brand_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        brand_frame.grid(row=0, column=0, pady=(25, 10), sticky="ew")
        # Insert logo image instead of text
        #logo_pil = Image.open("images/smartyper_logo_black.png")
        logo_pil = Image.open("images/Smartyper_white_letters.png")
        orig_w, orig_h = logo_pil.size
        panel_w = 220
        target_w = int(panel_w * 1.1)
        scale = target_w / orig_w
        target_h = int(orig_h * scale * 1.0)
        logo_image = CTkImage(dark_image=logo_pil, size=(target_w, target_h))
        logo_label = ctk.CTkLabel(brand_frame, image=logo_image, text="", fg_color="transparent", anchor="n")
        logo_label.pack(side="top", anchor="n", pady=(5,0))
        version_label = ctk.CTkLabel(brand_frame, text="v1.0", 
                         font=("Segoe UI", 15),
                         text_color=COLORS['text_secondary'], anchor="n")
        version_label.pack(side="top", anchor="n", pady=(10,0))
        
        self.tab_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.tab_frame.grid(row=1, column=0, pady=0, sticky="nsew")
        parent_button_padding = (8, 8)
        child_button_padding = (35, 8)  # Increased left padding for child buttons
        parent_button_size = {'width': 180, 'height': 40}
        child_button_size = {'width': 160, 'height': 32}

        row_index = 0  # Start from row 0 for children under the tab buttons
        
        # Define colors for each module to match home page cards
        module_colors = {
            "home": COLORS['home'],
            "genotyping": COLORS['primary'],
            "machine learning": COLORS['success'],
            "microtyping": COLORS['accent'],
            "project": COLORS['workflow_gold'],
            "workflow": COLORS['workflow_cherry'],
            "tutorial": COLORS['tutorial_peach']
        }
        
        for tab_name in self.tab_names:
            button_color = module_colors.get(tab_name, COLORS['text_primary'])
            # Use simple Unicode symbol instead of image icon
            icon_symbol = self.icon_symbols.get(tab_name, "•")
            # Map workflow tab to workflow_loader page
            if tab_name == "workflow":
                page_key = "workflow_loader"
            elif tab_name == "tutorial":
                page_key = "tutorial_folder"
            else:
                page_key = tab_name.lower()
            tab_button = ctk.CTkButton(
                    self.tab_frame, text=f"{icon_symbol}  {tab_name.upper()}", 
                    corner_radius=12, font=self.bfont,
                    width=parent_button_size['width'], height=parent_button_size['height'],
                    fg_color="transparent", hover_color=COLORS['card'],
                    border_width=0, anchor="w", text_color=button_color,
                    command= lambda t=page_key: self.show_page(t))
            tab_button.grid(row=row_index, column=0, pady=8, padx=parent_button_padding, sticky="ew")
            self.buttons[tab_name] = tab_button
            self.button_colors[tab_name] = button_color  # Store the color
            row_index += 1

            if tab_name in self.children_buttons:
                button_refs = []
                for child_name in self.children_buttons[tab_name]:
                    unique_id = f"{tab_name}_{child_name}"
                    # Use simple Unicode symbol for child buttons
                    child_symbol = self.icon_symbols.get(child_name, "▸")
                    # Custom display name for left panel only
                    if child_name == "microtype_data":
                        display_name = "Microtype data"
                    elif child_name == "microtype_results":
                        display_name = "Microtype results"
                    elif child_name == 'summary':
                        display_name = "Results Output"
                    else:
                        display_name = child_name.capitalize()
                    child_button = ctk.CTkButton(
                        self.tab_frame, text=f"{child_symbol}  {display_name}", 
                        corner_radius=8, font=self.sfont,
                        width=child_button_size['width'], height=child_button_size['height'],
                        fg_color="transparent", hover_color=COLORS['card'],
                        border_width=0, anchor="w", text_color=button_color,
                        command=lambda c=child_name.lower(): self.show_page(c))
                    child_button.grid(row=row_index, column=0, pady=4, padx=child_button_padding, sticky="ew")
                    child_button.grid_remove()  # Hide all child buttons initially
                    self.buttons[unique_id] = child_button
                    self.button_colors[unique_id] = button_color  # Store the color
                    button_refs.append(child_button)
                    row_index += 1
                self.children_button_refs[tab_name] = button_refs

        # Place the Exit button at the very end
        self.exit_button = ctk.CTkButton(self.left_panel, text="✕  Exit", text_color=COLORS['text_primary'], font=self.bfont,
                                         corner_radius=12, width=parent_button_size['width'], height=parent_button_size['height'],
                                         fg_color=COLORS['danger'], hover_color="#dc2626",
                                         border_width=0,
                                         command=self.destroy)
        self.exit_button.grid(row=999, column=0, pady=20, padx=parent_button_padding, columnspan=2, sticky="sew")
        self.buttons["exit"] = self.exit_button

    def button_clicked(self, button_id, parent_name=None):
        # Reset color for all buttons to their original colors
        for btn_id, button in self.buttons.items():
            if btn_id != "exit":
                original_color = self.button_colors.get(btn_id, COLORS['text_secondary'])
                button.configure(fg_color="transparent", text_color=original_color)
        
        # Highlight the currently clicked button with its own module color
        active_btn = self.buttons.get(button_id)
        if active_btn:
            active_color = self.button_colors.get(button_id, COLORS['primary'])
            active_btn.configure(fg_color=active_color, text_color=COLORS['text_primary'])

        # Highlight parent button if parent_name is provided
        if parent_name:
            parent_button = self.buttons.get(parent_name)
            if parent_button:
                parent_color = self.button_colors.get(parent_name, COLORS['primary'])
                parent_button.configure(fg_color=parent_color, text_color=COLORS['text_primary'])

    def toggle_menu(self, menu_name, all=False):
        if all:
            for menu in self.children_button_refs:
                for button in self.children_button_refs[menu]:
                    button.grid_remove()
            self.menu_expanded = {key: False for key in self.menu_expanded}
        else:
            expanded = self.menu_expanded.get(menu_name, False)
            for menu in self.children_button_refs:
                if menu == menu_name:
                    for button in self.children_button_refs[menu]:
                        if expanded:
                            button.grid_remove()
                        else:
                            button.grid()
                    self.menu_expanded[menu_name] = not expanded
                else:
                    for button in self.children_button_refs[menu]:
                        button.grid_remove()
                    self.menu_expanded[menu] = False

    def show_page(self, page_name):
        # Hide all pages
        for page in self.pages.values():
            page.grid_forget()
        # Show the selected page
        self.pages[page_name].grid(row=0, column=0, sticky="nswe")
        # Highlight the buttons
        parent = self.parent_children.get(page_name)
        if parent:
            unique_id = f"{parent}_{page_name}"
            self.button_clicked(unique_id, parent)
        else:
            self.button_clicked(page_name)
            
        # Toggle menus
        if page_name == "home":
            self.toggle_menu(page_name, True)
        elif page_name in ["genotyping", "microtyping", "machine learning", "project", "workflow", "tutorial"]:
            self.toggle_menu(page_name)
            
    def switch_theme(self, theme_mode):
        new_mode = "light" if ctk.get_appearance_mode() == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SmarTyper launcher")
    parser.add_argument(
        "--diagnose-gui",
        action="store_true",
        help="print GUI/runtime diagnostics for comparing WSL and native Ubuntu",
    )
    args = parser.parse_args()

    if args.diagnose_gui:
        print(json.dumps(collect_gui_diagnostics(), indent=2, sort_keys=True))
        raise SystemExit(0)

    mp.set_start_method('spawn', force=True)
    app = SmarTyperApp()
    app.mainloop()
