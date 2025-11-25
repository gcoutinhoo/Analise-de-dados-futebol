import tkinter as tk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x}+{y}")

        label = tk.Label(
            tw, text=self.text, background="#333", foreground="white",
            relief="solid", borderwidth=1, padx=6, pady=4,
            font=("Helvetica", 10)
        )
        label.pack()

    def hide_tooltip(self, event=None):
        tw = self.tip_window
        if tw:
            tw.destroy()
        self.tip_window = None
