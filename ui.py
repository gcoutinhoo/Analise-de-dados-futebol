import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk

def aplicar_tema(root):

    # cores personalizadas
    root.configure(bg="#F7F3ED")  # bege clean

    style = ttk.Style()

    # geral
    style.configure(".", 
        background="#F7F3ED", 
        foreground="#2E2E2E",
        font=("Helvetica", 12)
    )

    # frames
    style.configure("TFrame", background="#F7F3ED")

    # labels
    style.configure("TLabel",
        background="#F7F3ED",
        foreground="#2E2E2E",
        font=("Helvetica", 13)
    )

    # botões clean (cinza)
    style.configure("Clean.TButton",
        background="#D1D0CD",
        foreground="#2E2E2E",
        padding=10,
        relief="flat",
        borderwidth=0,
        font=("Helvetica", 12, "bold")
    )

    # hover effect
    style.map("Clean.TButton",
        background=[("active", "#BFBDBA")],
        relief=[("pressed", "sunken")]
    )

    # treeview (tabela)
    style.configure("Treeview",
        background="#EFE9E4",
        fieldbackground="#EFE9E4",
        foreground="#2E2E2E",
        bordercolor="#C8C3BD",
        borderwidth=1,
        font=("Helvetica", 12)
    )
    style.configure("Treeview.Heading",
        background="#D1D0CD",
        foreground="#2E2E2E",
        font=("Helvetica", 12, "bold")
    )
