import tkinter as tk

# Colors for SmarTyper logo
DNA_BLUE = "#7F5CFF"  # Blue for 'Smar'
DNA_ORANGE = "#FFA726"  # Orange for 'Typer'

class SmarTyperLogo(tk.Canvas):
    def __init__(self, parent, width=220, height=60, **kwargs):
        super().__init__(parent, width=width, height=height, bg="white", highlightthickness=0, **kwargs)
        self.draw_logo()

    def draw_logo(self):
        # DNA Helix (two curves)
        self.create_line(30, 10, 40, 30, 30, 50, smooth=True, width=4, fill=DNA_BLUE)
        self.create_line(40, 10, 30, 30, 40, 50, smooth=True, width=4, fill=DNA_ORANGE)
        # Digital Node (circle)
        self.create_oval(31, 26, 39, 34, fill=DNA_BLUE, outline="")
        # App Name: 'Smar' in blue, 'Typer' in orange
        self.create_text(55, 40, text="Smar", anchor="w", font=("Segoe UI", 32, "bold"), fill=DNA_BLUE)
        self.create_text(110, 40, text="Typer", anchor="w", font=("Segoe UI", 32, "bold"), fill=DNA_ORANGE)

# Example usage (uncomment to test standalone)
# if __name__ == "__main__":
#     root = tk.Tk()
#     logo = SmarTyperLogo(root)
#     logo.pack(padx=10, pady=10)
#     root.mainloop()
