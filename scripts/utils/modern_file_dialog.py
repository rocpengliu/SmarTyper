import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path
from . import modern_messagebox

# Modern color palette
COLORS = {
    'primary': '#3b82f6',
    'secondary': '#14b8a6',
    'accent': '#d97706',
    'background': '#0f172a',
    'card': '#1e293b',
    'card_hover': '#334155',
    'text_primary': '#f1f5f9',
    'text_secondary': '#94a3b8',
    'border': '#475569',
}

class ModernFileDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Select File", mode="file", filetype="all", initialdir=None, button_widget=None):
        super().__init__(parent)
        
        self.result = None
        self.mode = mode  # "file" or "directory"
        self.filetype = filetype
        self.current_path = Path(initialdir).resolve() if initialdir and os.path.exists(initialdir) else Path.home().resolve()
        self.button_widget = button_widget
        
        # Configure window
        self.title(title)
        self.geometry("900x600")
        self.configure(fg_color=COLORS['background'])
        
        # Make modal - need to wait for window to be viewable
        self.transient(parent)
        
        self.create_widgets()
        self.update_file_list()
        
        # Position near button or center on screen
        self.position_window()
        
        # Set grab after window is fully created and visible
        self.after(100, self.grab_set)
        
    def position_window(self):
        """Position window near the button that triggered it, or center on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        
        if self.button_widget:
            try:
                # Get button position on screen
                button_x = self.button_widget.winfo_rootx()
                button_y = self.button_widget.winfo_rooty()
                button_width = self.button_widget.winfo_width()
                button_height = self.button_widget.winfo_height()
                
                # Position dialog to the right and slightly below the button
                x = button_x + button_width + 20
                y = button_y - 50
                
                # Ensure dialog stays within screen bounds
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                
                # Adjust if going off right edge
                if x + width > screen_width:
                    x = button_x - width - 20
                    # If still off screen, center horizontally
                    if x < 0:
                        x = (screen_width - width) // 2
                
                # Adjust if going off bottom edge
                if y + height > screen_height:
                    y = screen_height - height - 50
                
                # Ensure not off top edge
                if y < 0:
                    y = 50
                
                self.geometry(f'{width}x{height}+{x}+{y}')
            except:
                # Fallback to center if button position can't be determined
                self.center_window()
        else:
            self.center_window()
    
    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        # Header with path navigation
        header_frame = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=12, height=60)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_propagate(False)
        
        # Back button
        self.back_btn = ctk.CTkButton(header_frame, text="◀ Back", width=80, height=35,
                                       corner_radius=8, fg_color=COLORS['primary'],
                                       hover_color=COLORS['secondary'],
                                       command=self.go_back)
        self.back_btn.pack(side=tk.LEFT, padx=10, pady=12)
        
        # Up level button
        up_btn = ctk.CTkButton(header_frame, text="⬆ Up", width=80, height=35,
                                 corner_radius=8, fg_color=COLORS['secondary'],
                                 hover_color=COLORS['primary'],
                                 command=self.go_up)
        up_btn.pack(side=tk.LEFT, padx=5, pady=12)
        
        # Path display
        self.path_var = tk.StringVar(value=str(self.current_path))
        path_entry = ctk.CTkEntry(header_frame, textvariable=self.path_var,
                 height=26, corner_radius=8,
                      border_width=2, border_color=COLORS['border'])
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=12)
        path_entry.bind("<Return>", self.navigate_to_path)
        
        # Main content area
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # File/Directory list with scrollbar
        list_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['card'], corner_radius=12)
        list_frame.grid(row=0, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Create Treeview for file list
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Modern.Treeview",
                       background=COLORS['card'],
                       foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['card'],
                       borderwidth=0,
                       font=('Segoe UI', 11))
        style.configure("Modern.Treeview.Heading",
                       background=COLORS['background'],
                       foreground=COLORS['text_primary'],
                       borderwidth=1,
                       font=('Segoe UI', 12, 'bold'))
        style.map('Modern.Treeview',
                 background=[('selected', COLORS['primary'])],
                 foreground=[('selected', COLORS['text_primary'])])
        
        self.file_tree = ttk.Treeview(list_frame, style="Modern.Treeview",
                                      columns=('Type', 'Size', 'Modified'),
                                      show='tree headings', selectmode='browse')
        
        self.file_tree.heading('#0', text='Name')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Modified', text='Modified')
        
        self.file_tree.column('#0', width=400, minwidth=200)
        self.file_tree.column('Type', width=100, minwidth=80)
        self.file_tree.column('Size', width=100, minwidth=80)
        self.file_tree.column('Modified', width=180, minwidth=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 10))
        
        self.file_tree.bind('<Double-Button-1>', self.on_double_click)
        self.file_tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Selected file entry
        selection_frame = ctk.CTkFrame(self, fg_color="transparent")
        selection_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=10)
        
        ctk.CTkLabel(selection_frame, text="Selected:", font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['text_primary']).pack(side=tk.LEFT, padx=5)
        
        self.selected_var = tk.StringVar()
        selected_entry = ctk.CTkEntry(selection_frame, textvariable=self.selected_var,
                 height=26, corner_radius=8,
                          border_width=2, border_color=COLORS['border'])
        selected_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(5, 15))
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", width=120, height=40,
                                   corner_radius=8, fg_color=COLORS['border'],
                                   hover_color=COLORS['card_hover'],
                                   command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        if self.mode == "directory":
            new_folder_btn = ctk.CTkButton(
                button_frame,
                text="New Folder",
                width=120,
                height=40,
                corner_radius=8,
                fg_color=COLORS['accent'],
                hover_color=COLORS['secondary'],
                command=self.create_new_folder,
            )
            new_folder_btn.pack(side=tk.RIGHT, padx=5)
        
        select_text = "Select" if self.mode == "directory" else "Open"
        self.select_btn = ctk.CTkButton(button_frame, text=select_text, width=120, height=40,
                                        corner_radius=8, fg_color=COLORS['primary'],
                                        hover_color=COLORS['secondary'],
                                        command=self.select)
        self.select_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
    def update_file_list(self):
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Update path display
        self.path_var.set(str(self.current_path))
        
        try:
            items = sorted(self.current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if item.name.startswith('.'):
                    continue
                    
                try:
                    is_dir = item.is_dir()
                    item_type = "📁 Folder" if is_dir else "📄 File"
                    
                    if is_dir:
                        size = ""
                        modified = ""
                    else:
                        size = self.format_size(item.stat().st_size)
                        modified = self.format_time(item.stat().st_mtime)
                    
                    # Apply file type filter
                    if not is_dir and self.mode == "file":
                        if not self.matches_filetype(item.name):
                            continue
                    
                    self.file_tree.insert('', 'end', text=item.name,
                                         values=(item_type, size, modified),
                                         tags=('directory' if is_dir else 'file',))
                except (PermissionError, OSError):
                    continue
                    
        except PermissionError:
            self.file_tree.insert('', 'end', text="[Permission Denied]",
                                 values=("", "", ""), tags=('error',))

    def select_item_by_name(self, item_name):
        for item_id in self.file_tree.get_children():
            if self.file_tree.item(item_id, 'text') == item_name:
                self.file_tree.selection_set(item_id)
                self.file_tree.focus(item_id)
                self.file_tree.see(item_id)
                break
    
    def matches_filetype(self, filename):
        if self.filetype == "all":
            return True
        elif self.filetype == "index":
            return filename.endswith((
                '.txt', '.csv', '.tsv', '.tab', '.pkl', '.dill'))
        else:
            return True
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def format_time(self, timestamp):
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
    
    def on_double_click(self, event):
        selection = self.file_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_text = self.file_tree.item(item, 'text')
        item_path = self.current_path / item_text
        
        if item_path.is_dir():
            self.current_path = item_path
            self.update_file_list()
        elif self.mode == "file":
            self.selected_var.set(item_text)
            self.select()
    
    def on_select(self, event):
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            item_text = self.file_tree.item(item, 'text')
            self.selected_var.set(item_text)
    
    def go_back(self):
        parent = self.current_path.parent.resolve()
        if parent != self.current_path:
            self.current_path = parent
            self.update_file_list()
    
    def go_up(self):
        parent = self.current_path.parent.resolve()
        if parent != self.current_path:
            self.current_path = parent
            self.update_file_list()
        else:
            print(f"Already at root")
    
    def navigate_to_path(self, event=None):
        try:
            new_path = Path(self.path_var.get()).expanduser()
            if new_path.exists() and new_path.is_dir():
                self.current_path = new_path
                self.update_file_list()
        except Exception:
            self.path_var.set(str(self.current_path))

    def create_new_folder(self):
        folder_name = self.prompt_new_folder_name()

        if folder_name is None:
            return

        folder_name = folder_name.strip()
        if not folder_name:
            modern_messagebox.showwarning(None, "Invalid Name", "Folder name cannot be empty.")
            return

        if any(ch in folder_name for ch in ('/', '\\')):
            modern_messagebox.showwarning(None, "Invalid Name", "Use a folder name, not a path.")
            return

        new_dir = self.current_path / folder_name
        try:
            new_dir.mkdir(parents=False, exist_ok=False)
            self.update_file_list()
            self.selected_var.set(folder_name)
            self.select_item_by_name(folder_name)
        except FileExistsError:
            modern_messagebox.showwarning(None, "Already Exists", f"Folder '{folder_name}' already exists.")
        except Exception as e:
            modern_messagebox.showerror(None, "Create Folder Failed", f"Unable to create folder: {e}")

    def prompt_new_folder_name(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create New Folder")
        dialog.geometry("420x150")
        dialog.configure(fg_color=COLORS['background'])
        dialog.transient(self)
        dialog.resizable(False, False)

        self._position_child_dialog(dialog)

        result = {"value": None}
        name_var = tk.StringVar()

        frame = ctk.CTkFrame(dialog, fg_color=COLORS['card'], corner_radius=12)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        ctk.CTkLabel(
            frame,
            text="Enter new folder name:",
            text_color=COLORS['text_primary'],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        entry = ctk.CTkEntry(
            frame,
            textvariable=name_var,
            height=30,
            corner_radius=8,
            border_width=2,
            border_color=COLORS['border'],
        )
        entry.pack(fill=tk.X, padx=16, pady=(0, 12))

        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.pack(fill=tk.X, padx=16, pady=(0, 12))

        def on_cancel():
            dialog.destroy()

        def on_create(event=None):
            result["value"] = name_var.get()
            dialog.destroy()

        ctk.CTkButton(
            button_row,
            text="Cancel",
            width=90,
            height=34,
            corner_radius=8,
            fg_color=COLORS['border'],
            hover_color=COLORS['card_hover'],
            command=on_cancel,
        ).pack(side=tk.RIGHT, padx=(8, 0))

        ctk.CTkButton(
            button_row,
            text="Create",
            width=90,
            height=34,
            corner_radius=8,
            fg_color=COLORS['primary'],
            hover_color=COLORS['secondary'],
            command=on_create,
        ).pack(side=tk.RIGHT)

        dialog.bind("<Return>", on_create)
        dialog.bind("<Escape>", lambda event: on_cancel())
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        dialog.after(50, lambda: (dialog.grab_set(), entry.focus_set()))
        self.wait_window(dialog)
        return result["value"]

    def _position_child_dialog(self, dialog):
        self.update_idletasks()
        dialog.update_idletasks()

        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = max(0, min(x, screen_width - dialog_width))
        y = max(0, min(y, screen_height - dialog_height))

        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def select(self):
        selected = self.selected_var.get()
        
        if self.mode == "directory":
            # For directory mode
            if selected:
                result_path = self.current_path / selected
                # If it's a directory, select it
                if result_path.is_dir():
                    self.result = str(result_path)
                    self.destroy()
                    return
            # If nothing selected or selected is a file, use current directory
            self.result = str(self.current_path)
            self.destroy()
        else:
            # For file mode
            if selected:
                result_path = self.current_path / selected
                # Accept the file regardless of whether it exists (for compatibility)
                self.result = str(result_path)
                self.destroy()
            else:
                # If nothing selected, don't close dialog
                from . import modern_messagebox
                modern_messagebox.showwarning(None, "No Selection", "Please select a file.")
    
    def cancel(self):
        self.result = None
        self.destroy()


def modern_file_dialog(parent, title="Select File", mode="file", filetype="all", initialdir=None, button_widget=None):
    """
    Show a modern file/directory selection dialog
    
    Args:
        parent: Parent window
        title: Dialog title
        mode: "file" for file selection, "directory" for directory selection
        filetype: "all", "index", etc.
        initialdir: Initial directory path
        button_widget: The button widget that triggered the dialog (for positioning)
        
    Returns:
        Selected file/directory path as string, or None if cancelled
    """
    dialog = ModernFileDialog(parent, title, mode, filetype, initialdir, button_widget)
    parent.wait_window(dialog)
    return dialog.result
