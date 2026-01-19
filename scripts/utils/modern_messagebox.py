
import customtkinter as ctk
import tkinter as tk
from .common import parent_button_size

# Modern color palette
COLORS = {
    'primary': '#3b82f6',
    'secondary': '#14b8a6',
    'accent': '#d97706',
    'success': '#10b981',
    'error': '#ef4444',
    'warning': '#f59e0b',
    'background': '#0f172a',
    'card': '#1e293b',
    'card_hover': '#334155',
    'text_primary': '#f1f5f9',
    'text_secondary': '#94a3b8',
}

class ModernMessageBox(ctk.CTkToplevel):
    def __init__(self, parent, title="Message", message="", type="info"):
        super().__init__(parent)
        
        self.result = None
        self.type = type  # "info", "success", "error", "warning"
        self.parent = parent
        
        # Configure window
        self.title(title)
        self.geometry("500x250")
        self.configure(fg_color=COLORS['background'])
        
        # Make modal
        self.transient(parent)
        
        self.create_widgets(title, message)
        self.center_on_parent()
        
        # Set grab after window is positioned
        self.after(100, self.grab_set)
        
    def center_on_parent(self):
        """Center window relative to parent window"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        
        try:
            # Get parent window position and size
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            # Calculate center position relative to parent
            x = parent_x + (parent_width - width) // 2
            y = parent_y + (parent_height - height) // 2
            
            # Ensure dialog stays within screen bounds
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            x = max(0, min(x, screen_width - width))
            y = max(0, min(y, screen_height - height))
            
            self.geometry(f'{width}x{height}+{x}+{y}')
        except:
            # Fallback to screen center if parent position can't be determined
            x = (self.winfo_screenwidth() - width) // 2
            y = (self.winfo_screenheight() - height) // 2
            self.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self, title, message):
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon and title section
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Icon based on type
        icons = {
            "info": "ℹ️",
            "success": "✓",
            "error": "✗",
            "warning": "⚠"
        }
        colors = {
            "info": COLORS['primary'],
            "success": COLORS['success'],
            "error": COLORS['error'],
            "warning": COLORS['warning']
        }
        
        icon = icons.get(self.type, "ℹ️")
        color = colors.get(self.type, COLORS['primary'])
        
        # Icon label
        icon_label = ctk.CTkLabel(header_frame, text=icon, font=("Segoe UI", 48),
                                  text_color=color)
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Title label
        title_label = ctk.CTkLabel(header_frame, text=title, 
                                   font=("Segoe UI", 24, "bold"),
                                   text_color=COLORS['text_primary'])
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Message section
        message_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        message_label = ctk.CTkLabel(message_frame, text=message,
                                     font=("Segoe UI", 14),
                                     text_color=COLORS['text_secondary'],
                                     wraplength=440,
                                     justify=tk.LEFT)
        message_label.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Button section
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        ok_btn = ctk.CTkButton(button_frame, text="OK", width=parent_button_size['width'], height=parent_button_size['height'],
                              corner_radius=10, 
                              fg_color=color,
                              hover_color=COLORS['secondary'],
                              font=("Segoe UI", 14, "bold"),
                              command=self.ok)
        ok_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key to OK
        self.bind("<Return>", lambda e: self.ok())
        self.bind("<Escape>", lambda e: self.ok())
        
    def ok(self):
        self.result = True
        self.grab_release()
        self.destroy()


def showinfo(parent, title, message):
    """Show an info message box"""
    dialog = ModernMessageBox(parent, title, message, type="info")
    parent.wait_window(dialog)
    return dialog.result


def showsuccess(parent, title, message):
    """Show a success message box"""
    dialog = ModernMessageBox(parent, title, message, type="success")
    parent.wait_window(dialog)
    return dialog.result


def showerror(parent, title, message):
    """Show an error message box"""
    dialog = ModernMessageBox(parent, title, message, type="error")
    parent.wait_window(dialog)
    return dialog.result


def showwarning(parent, title, message):
    """Show a warning message box"""
    dialog = ModernMessageBox(parent, title, message, type="warning")
    parent.wait_window(dialog)
    return dialog.result
