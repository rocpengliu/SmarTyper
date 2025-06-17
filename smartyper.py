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

from scripts.home_page import create_home
from scripts.project.project_module import create_project_module
from scripts.genotype.genotype_module import create_genotype_module
from scripts.genotype.data_loader import data_loader
from scripts.genotype.parameter_setter import parameter_setter
from scripts.genotype.job_runner import job_runner
from scripts.genotype.results_viewer import results_viewer
from scripts.genotype.results_summary import results_summary
from scripts.project.project_loader import project_loader
from scripts.microtype.micro_module import create_micro_module
from scripts.microtype.micro_loader import micro_loader
from scripts.microtype.micro_viewer import micro_viewer
from PIL import Image, ImageTk
import os
from scripts.class_modules.class_modules import GenotypeClass

ctk.set_appearance_mode("dark")
class SmarTyperApp(ctk.CTk):
    def __init__(self):
        print(ctk.__version__)
        print(tk.TkVersion)  # Tk version (e.g., 8.6)
        print(tk.TclVersion) # Tcl version (e.g., 8.6)
        super().__init__()
        self.title("SmarTyper")
        #self.geometry("900x600")
        self.setup_window()
        self.resizable(True,True)
        
        self.bfont = ("Arial", 20, "bold")
        self.sfont = ("Arial", 13, "bold")
        
        self.default_fg_color = "darkgreen"
        self.highlight_color = "orange" 
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Left panel should not expand
        self.grid_columnconfigure(1, weight=1)  # Right panel should expand
        
        self.left_panel = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#2b2b2b")
        self.left_panel.grid(row=0, column=0, sticky="ns")
        self.left_panel.grid_rowconfigure(0, minsize=200)  # Minimum size for the first row
        self.left_panel.grid_rowconfigure(1, weight=1)    # Push exit button down
        self.left_panel.grid_rowconfigure(999, weight=0)  # Last row weight as 0
        
        self.right_panel = ctk.CTkFrame(self, corner_radius=0, fg_color="#3b3b3b")
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        self.genotype_class = GenotypeClass()
        
        self.parent_children = {
            "data": "genotype",
            "parameters": "genotype",
            "run": "genotype",
            "results": "genotype",
            "summary": "genotype",
            "micro_data": "microtype",
            "micro_res": "microtype",
            "opener": "project"
        }
        self.tab_names = ["home", "genotype", "microtype", "project"]
        self.children_buttons = {
            "genotype": ["data", "parameters", "run", "results", "summary"],
            "microtype": ["micro_data", "micro_res"],
            "project": ["opener"]
        }
        self.menu_expanded = {
            "genotype": False,
            "microtype": False,
            "project": False
        }
        self.home_path = os.path.dirname(os.path.realpath(__file__))
        self.icons = {
            "home": os.path.join(self.home_path, "images", "home.png"),
            "genotype": os.path.join(self.home_path, "images", "genotyping.png"),
            "project": os.path.join(self.home_path, "images", "project.png"),
            "microtype": os.path.join(self.home_path, "images", "microtype.png"),
            "opener": os.path.join(self.home_path, "images", "opener.png"),
            "run": os.path.join(self.home_path, "images", "run.png"),
            "parameters": os.path.join(self.home_path, "images", "parameters.png"),
            "data": os.path.join(self.home_path, "images", "data.png"),
            "micro_data": os.path.join(self.home_path, "images", "data.png"),
            "micro_res": os.path.join(self.home_path, "images", "results.png"),
            "results": os.path.join(self.home_path, "images", "results.png"),
            "summary": os.path.join(self.home_path, "images", "summary.png"),
            "exit": os.path.join(self.home_path, "images", "exit.png")
        }
        self.buttons = {}
        self.create_tabs()
        self.pages = {
            "home": create_home(self.right_panel),
            "genotype": create_genotype_module(self.right_panel),
            "data": data_loader(self.right_panel),
            "parameters": parameter_setter(self.right_panel),
            "run": job_runner(self.right_panel),
            "results": results_viewer(self.right_panel),
            "summary": results_summary(self.right_panel),
            "microtype": create_micro_module(self.right_panel),
            "micro_data": micro_loader(self.right_panel),
            "micro_res": micro_viewer(self.right_panel),
            "project": create_project_module(self.right_panel),
            "opener": project_loader(self.right_panel)
        }
        self.show_page("home")

    def setup_window(self):
        screen_width=self.winfo_screenwidth()*0.4
        screen_height=self.winfo_screenheight()*0.6
        self.geometry(f"{screen_width}x{screen_height}")
    def create_tabs(self):
        self.tab_frame = ctk.CTkFrame(self.left_panel, fg_color="#2b2b2b")
        self.tab_frame.grid(row=0, column=0, pady=20, sticky="nsew")
        parent_button_padding = (5, 5)
        child_button_padding = (10, 10)
        parent_button_size = {'width': 160, 'height': 30}
        child_button_size = {'width': 100, 'height': 20}

        row_index = 1  # Start from row 1 for children under the tab buttons
        for tab_name in self.tab_names:
            tab_button = ctk.CTkButton(
                    self.tab_frame, text=tab_name, corner_radius=50, font=self.bfont,
                    width=parent_button_size['width'], height=parent_button_size['height'],
                    command= lambda t=tab_name.lower():self.show_page(t))
            tab_button.grid(row=row_index, column=0, pady=10, padx=parent_button_padding, sticky="w")

            tab_icon = None
            tab_icon_path = self.icons.get(tab_name)
            if tab_icon_path and os.path.exists(tab_icon_path):
                try:
                    tab_image = Image.open(tab_icon_path)
                    #tab_image.save(tab_icon_path)
                    #tab_image = tab_image.resize((20, 20), Image.Resampling.LANCZOS)
                    tab_icon = CTkImage(tab_image)  # Use ImageTk.PhotoImage
                except IOError:
                    print(f"Error: Could not open image file {tab_icon_path}")
            
            if tab_icon:
                tab_button.configure(image=tab_icon)
                tab_button.image = tab_icon
            self.buttons[tab_name] = tab_button
            row_index += 1

            if tab_name in self.children_buttons:
                button_refs = []
                for child_name in self.children_buttons[tab_name]:
                    unique_id = f"{tab_name}_{child_name}"
                    sub_tab_icon = None
                    sub_tab_icon_path = self.icons.get(child_name)
                    if sub_tab_icon_path:
                        try:
                            sub_tab_image = Image.open(sub_tab_icon_path)
                            #sub_tab_image.save(sub_tab_icon_path)
                            #tab_image = tab_image.resize((20, 20), Image.Resampling.LANCZOS)
                            sub_tab_icon = CTkImage(sub_tab_image)  # Use ImageTk.PhotoImage
                        except IOError:
                            print(f"Error: Could not open image file {tab_icon_path}")
                    child_button = ctk.CTkButton(
                        self.tab_frame, text=child_name, corner_radius=50, font=self.sfont,
                        width=child_button_size['width'], height=child_button_size['height'],
                        command=lambda c=child_name.lower(): self.show_page(c))
                    if sub_tab_icon:
                        child_button.configure(image=sub_tab_icon)
                        child_button.image = sub_tab_icon
                    child_button.grid(row=row_index, column=0, pady=5, padx=child_button_padding, sticky="e")
                    child_button.grid_remove()  # Initially hidden
                    button_refs.append(child_button)
                    row_index += 1
                    self.buttons[unique_id] = child_button
                self.children_buttons[tab_name] = button_refs

        # Place the Exit button at the very end
        exit_icon_path = self.icons.get("exit")
        exit_icon = None
        if exit_icon_path and os.path.exists(exit_icon_path):
                try:
                    exit_image = Image.open(exit_icon_path)
                    exit_image = exit_image.resize((20, 20), Image.Resampling.LANCZOS)
                    exit_icon = CTkImage(exit_image)  # Use ImageTk.PhotoImage
                except IOError:
                    print(f"Error: Could not open image file {exit_icon_path}")
        self.exit_button = ctk.CTkButton(self.left_panel, text="Exit", text_color="red", font=self.bfont,
                                         corner_radius=50, width=parent_button_size['width'], height=parent_button_size['height'],
                                         fg_color = self.default_fg_color,
                                         command=self.destroy)
        if exit_icon:
            self.exit_button.configure(image=exit_icon)
            self.exit_button.image = exit_icon
        self.exit_button.grid(row=999, column=0, pady=10, columnspan=2, sticky="s")
        self.buttons["exit"] = self.exit_button

    def button_clicked(self, button_id, parent_name=None):
        # Reset color for all buttons
        for btn_id, button in self.buttons.items():
            button.configure(fg_color=self.default_fg_color)
        
        # Highlight the currently clicked button
        active_btn = self.buttons.get(button_id)
        if active_btn:
            active_btn.configure(fg_color=self.highlight_color)

        # Highlight parent button if parent_name is provided
        if parent_name:
            parent_button = self.buttons.get(parent_name)
            if parent_button:
                parent_button.configure(fg_color=self.highlight_color)

    def toggle_menu(self, menu_name, all=False):
        if all:
            for menu in self.children_buttons:
                for button in self.children_buttons[menu]:
                    button.grid_remove()
            self.menu_expanded = {key: False for key in self.menu_expanded}
        else:
            expanded = self.menu_expanded[menu_name]
            for menu in self.children_buttons:
                if menu == menu_name:
                    for button in self.children_buttons[menu]:
                        if expanded:
                            button.grid_remove()
                        else:
                            button.grid()
                    self.menu_expanded[menu_name] = not expanded
                else:
                    for button in self.children_buttons[menu]:
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
        elif page_name in ["genotype", "microtype", "project"]:
            self.toggle_menu(page_name)
            
    def switch_theme(self, theme_mode):
        new_mode = "light" if ctk.get_appearance_mode() == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
    
if __name__ == '__main__':
    app = SmarTyperApp()
    app.mainloop()
