# screens/glossary_window.py
import os
import json
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import ttk as tkttk  # para Tipos

DEFAULT_TEXT = """
📘 GLOSSÁRIO FBref — RESUMO

1) Estatísticas Gerais
MP — Matches Played (Jogos disputados)
Starts — Jogos como titular
Min — Minutos jogados
90s — Jogos equivalentes a 90 min
Age — Idade
Born — Data de nascimento

2) Ataque
G — Goals (Gols)
A — Assists (Assistências)
G+A — Goals + Assists (Participações em gols)
G-PK — Gols sem pênaltis
PK — Penalties Made (Pênaltis convertidos)
PKatt — Penalties Attempted (Pênaltis tentados)
Sh — Shots (Finalizações)
SoT — Shots on Target (Finalizações no alvo)
SoT% — Percentual de finalizações no alvo
G/Sh — Gols por finalização
G/SoT — Gols por finalização no alvo

3) Expected Goals / Expected Assists
xG — Expected Goals (Gols esperados)
npxG — Non-Penalty xG (xG sem pênaltis)
xA — Expected Assists (Assistências esperadas)
xG+xA — xG + xA

4) Passes (resumo)
Cmp, Att, Cmp%, KP, 1/3, PPA, Crs, TB, Sw, PrgP

5) Condução / Progresso
Carries, PrgC, Touches, Succ, TakeOn%, CPA

6) Defesa
Tkl, Tkl%, TklW, Press, Int, Blk, ShBl, PassBl, Clr, Err, Recov

7) Duelos Aéreos
AER, Won, Lost, AER%

8) Goleiros
GA, Saves, Save%, PSxG, CS, CS%

9) Criação / Ações
SCA, GCA, PassLive, PassDead, Drib, Fld, Def

10) Outros
Rec, PrgR, %ile (percentil)
"""

def _load_json_glossary(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def abrir_glossario(parent_window=None):
    """
    Abre a janela de Glossário. parent_window pode ser a janela principal (Toplevel) para posicionamento.
    """
    win = ttk.Toplevel(parent_window) if parent_window is not None else ttk.Window()
    win.title("Glossário FBref")
    win.geometry("680x720")
    # aplica tema se estiver usando aplicar_tema no seu projeto
    try:
        from src.ui import aplicar_tema
        aplicar_tema(win)
    except Exception:
        pass

    # Frame com canvas + scrollbar
    container = ttk.Frame(win)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Título
    ttk.Label(scroll_frame, text="📘 Glossário FBref", font=("Helvetica", 16, "bold")).pack(pady=(0,10), anchor="w")

    # tentar carregar data/glossary.json
    glossary = _load_json_glossary("data/glossary.json")
    if glossary and isinstance(glossary, dict):
        # montar texto organizado por chave
        for key, val in glossary.items():
            ttk.Label(scroll_frame, text=f"{key} — {val}", wraplength=620, justify="left").pack(anchor="w", pady=2)
    else:
        # fallback texto padrão
        ttk.Label(scroll_frame, text=DEFAULT_TEXT, wraplength=620, justify="left").pack(anchor="w")

    ttk.Button(scroll_frame, text="Fechar", bootstyle="danger-outline", command=win.destroy).pack(pady=12)
    return win
