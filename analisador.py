# src/analisador.py
import os
import shutil
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from src.ui import aplicar_tema
from utils.data_loader import carregar_csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

# importa a janela do glossário
from screens.glossary_window import abrir_glossario

MAX_DISPLAY_ROWS = 300

# campos aceitos (com ou sem ":")
PROFILE_COLS = {
    "Name": ["Name", "Name:"],
    "Position": ["Position", "Position:"],
    "Foot": ["Foot", "Foot:", "Footer", "Footer:"],
    "Born": ["Born", "Born:"],
    "National Team": ["National Team", "National Team:"],
    "Club": ["Club", "Club:"],
    "Wages": ["Wages", "Wages:"],
}


class JanelaJogador:
    def __init__(self, root, jogador, remover_callback=None):
        self.jogador = jogador
        self.remover_callback = remover_callback

        self.win = ttk.Toplevel(root)
        self.win.title(f"Análise de {jogador}")
        self.win.geometry("1200x780")
        aplicar_tema(self.win)

        self.current_csv = None
        self.df_original = None
        self.df_filtrado = None
        self.df_atual = None

        # LAYOUT
        container = ttk.Frame(self.win)
        container.pack(fill="both", expand=True, padx=10, pady=8)

        # LEFT (perfil + hotbar)
        left = ttk.Frame(container, width=340)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        prof_card = ttk.Labelframe(left, text="Perfil (Name.csv)", bootstyle="secondary")
        prof_card.pack(fill="x", padx=6, pady=6)

        self.label_profile = ttk.Label(prof_card, text="(Name.csv não encontrado)", wraplength=300, justify="left")
        self.label_profile.pack(anchor="w", padx=8, pady=8)

        ttk.Separator(left).pack(fill="x", pady=6)
        ttk.Label(left, text="Tabelas", font=("Helvetica", 11, "bold")).pack(anchor="w", padx=8)
        self.hotbar_frame = ttk.Frame(left)
        self.hotbar_frame.pack(fill="both", expand=True, padx=6, pady=6)

        # RIGHT
        right = ttk.Frame(container)
        right.pack(side="left", fill="both", expand=True)

        top_actions = ttk.Frame(right)
        top_actions.pack(fill="x", pady=(0, 6))

        # Nome do jogador (esquerda)
        ttk.Label(top_actions, text=self.jogador, font=("Helvetica", 16, "bold")).pack(side="left", padx=6)

        # Botão de Glossário (❓) - canto superior direito
        ttk.Button(
            top_actions, text="❓", width=3, bootstyle="info-outline",
            command=lambda: abrir_glossario(self.win)
        ).pack(side="right", padx=6)

        # Botão remover
        ttk.Button(
            top_actions, text="🗑 Remover Jogador", bootstyle="danger-outline",
            command=self._remover_jogador
        ).pack(side="right", padx=6)

        self.file_label = ttk.Label(right, text="", font=("Helvetica", 11, "italic"))
        self.file_label.pack(anchor="w", padx=6)

        # FILTROS
        filters = ttk.Frame(right)
        filters.pack(fill="x", padx=6, pady=6)

        ttk.Label(filters, text="Temporada:").pack(side="left")
        self.combo_season = ttk.Combobox(filters, width=18)
        self.combo_season.pack(side="left", padx=(6, 12))

        ttk.Label(filters, text="Competição:").pack(side="left")
        self.combo_comp = ttk.Combobox(filters, width=18)
        self.combo_comp.pack(side="left", padx=(6, 12))

        ttk.Button(filters, text="Aplicar", bootstyle="info", command=self.aplicar_filtros).pack(side="left")
        ttk.Button(filters, text="Limpar", bootstyle="outline-secondary", command=self.limpar_filtros).pack(side="left", padx=6)

        # TABELA
        self.table_frame = ttk.Frame(right)
        self.table_frame.pack(fill="both", expand=True, padx=6, pady=6)

        # GRÁFICOS
        chart_controls = ttk.Frame(right)
        chart_controls.pack(fill="x", padx=6, pady=6)

        ttk.Label(chart_controls, text="Selecionar colunas p/ gráfico:").pack(anchor="w")
        self.chart_cols_frame = ttk.Frame(chart_controls)
        self.chart_cols_frame.pack(fill="x")

        chart_opts = ttk.Frame(chart_controls)
        chart_opts.pack(fill="x", pady=6)

        ttk.Label(chart_opts, text="Tipo:").pack(side="left")
        self.chart_type = ttk.Combobox(chart_opts, values=["Pizza", "Barra"], width=12)
        self.chart_type.set("Pizza")
        self.chart_type.pack(side="left", padx=8)
        ttk.Button(chart_opts, text="Abrir Gráfico", bootstyle="primary", command=self.abrir_grafico).pack(side="left")

        # carregar name e hotbar
        self._carregar_name_and_hotbar()

    # -----------------------------
    def _carregar_name_and_hotbar(self):
        pasta = os.path.join("data/jogadores", self.jogador)
        arquivos = sorted(
            [f for f in os.listdir(pasta) if f.lower().endswith(".csv") and not f.startswith("._")],
            key=lambda x: (0 if x.lower() == "name.csv" else 1, x.lower())
        )

        for w in self.hotbar_frame.winfo_children():
            w.destroy()

        # Name.csv para o perfil (não cria botão para ele)
        if "Name.csv" in arquivos:
            df_name = carregar_csv(os.path.join(pasta, "Name.csv"))
            if df_name is not None and not df_name.empty:
                # Normaliza colunas (remove BOM, espaços invisíveis e ":")
                new_cols = {}
                for col in df_name.columns:
                    clean = str(col).replace("\ufeff", "").replace("\xa0", " ").replace("\t", " ").replace("\u200b", "")
                    clean = clean.strip()
                    # manter o ":" nos dados originais, mas para busca remover:
                    clean_no_colon = clean.replace(":", "").strip()
                    new_cols[col] = clean_no_colon
                df_name.rename(columns=new_cols, inplace=True)

                row = df_name.iloc[0]
                lines = []
                for label, options in PROFILE_COLS.items():
                    # procurar coluna normalizada (sem ":"), ou variações
                    for opt in options:
                        key = opt.replace(":", "")
                        if key in df_name.columns:
                            val = str(row.get(key, "")).strip()
                            if val and val.lower() != "nan":
                                lines.append(f"{label}: {val}")
                            break
                if lines:
                    self.label_profile.config(text="\n".join(lines))
                else:
                    self.label_profile.config(text="(Name.csv sem dados válidos)")
            else:
                self.label_profile.config(text="(Name.csv vazio)")
        else:
            self.label_profile.config(text="(Name.csv não encontrado)")

        # hotbar com os outros CSVs (sem Name.csv)
        for arq in arquivos:
            if arq.lower() == "name.csv":
                continue
            ttk.Button(self.hotbar_frame, text=arq.replace(".csv", ""), bootstyle="secondary",
                       command=lambda a=arq: self._selecionar_csv(a)).pack(fill="x", pady=4)

        # abrir o primeiro csv não-Name se existir
        others = [a for a in arquivos if a.lower() != "name.csv"]
        if others:
            self._selecionar_csv(others[0])
        else:
            # limpar área de tabela se não houver dados
            for w in self.table_frame.winfo_children():
                w.destroy()
            ttk.Label(self.table_frame, text="Nenhum CSV de estatísticas encontrado.").pack(pady=10)

    # -----------------------------
    def _selecionar_csv(self, nome_arquivo):
        pasta = os.path.join("data/jogadores", self.jogador)
        caminho = os.path.join(pasta, nome_arquivo)

        df = carregar_csv(caminho)
        if df is None:
            messagebox.showerror("Erro", f"Não foi possível ler {nome_arquivo}")
            return

        if "Season" in df.columns:
            df["Season"] = df["Season"].astype(str).str.replace(".0", "").str.strip()

        self.current_csv = nome_arquivo
        self.df_original = df.copy()
        self.df_filtrado = df.fillna("")
        self.df_atual = df.copy()
        self.file_label.config(text=f"Arquivo: {nome_arquivo}")

        self._popular_filtros(self.df_filtrado)
        self._popular_chart_columns(self.df_atual)
        self._render_table(self.df_filtrado)

    # -----------------------------
    def _popular_filtros(self, df):
        if "Season" in df.columns:
            vals = sorted(df["Season"].astype(str).unique())
            self.combo_season["values"] = ["Todas"] + vals
            self.combo_season.set("Todas")
        if "Comp" in df.columns:
            vals = sorted(df["Comp"].astype(str).unique())
            self.combo_comp["values"] = ["Todas"] + vals
            self.combo_comp.set("Todas")

    # -----------------------------
    def _popular_chart_columns(self, df):
        for w in self.chart_cols_frame.winfo_children():
            w.destroy()
        self.chart_vars = {}
        numeric = df.select_dtypes(include="number").columns.tolist()
        cols = numeric if numeric else df.columns.tolist()
        for c in cols:
            var = tk.BooleanVar()
            ttk.Checkbutton(self.chart_cols_frame, text=c, variable=var).pack(side="left", padx=6)
            self.chart_vars[c] = var

    # -----------------------------
    def aplicar_filtros(self):
        if self.df_original is None:
            return
        df = self.df_original.copy()
        season = self.combo_season.get()
        comp = self.combo_comp.get()
        if "Season" in df.columns and season != "Todas":
            df = df[df["Season"] == season]
        if "Comp" in df.columns and comp != "Todas":
            df = df[df["Comp"] == comp]
        self.df_atual = df.copy()
        self.df_filtrado = df.fillna("")
        self._render_table(self.df_filtrado)

    # -----------------------------
    def limpar_filtros(self):
        if self.df_original is None:
            return
        if "Season" in self.df_original.columns:
            self.combo_season.set("Todas")
        if "Comp" in self.df_original.columns:
            self.combo_comp.set("Todas")
        for v in getattr(self, "chart_vars", {}).values():
            v.set(False)
        self.df_atual = self.df_original.copy()
        self.df_filtrado = self.df_original.fillna("")
        self._render_table(self.df_filtrado)

    # -----------------------------
    def _render_table(self, df):
        for w in self.table_frame.winfo_children():
            w.destroy()
        cols = df.columns.tolist()
        tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", height=22)
        tree.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, minwidth=100, width=130)
        for i in range(min(len(df), MAX_DISPLAY_ROWS)):
            row = df.iloc[i]
            tree.insert("", "end", values=[str(row.get(c, "")) for c in cols])
        self.table = tree

    # -----------------------------
    def abrir_grafico(self):
        chosen = [c for c, v in getattr(self, "chart_vars", {}).items() if v.get()]
        if not chosen:
            messagebox.showinfo("Aviso", "Selecione colunas para o gráfico.")
            return
        df = self.df_atual.copy()
        numeric = {}
        for col in chosen:
            s = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")
            if s.notna().sum() > 0:
                numeric[col] = s.mean()
        if not numeric:
            messagebox.showwarning("Aviso", "Nenhuma coluna numérica válida.")
            return
        valores = pd.Series(numeric)
        win = ttk.Toplevel(self.win)
        win.title("Gráfico")
        win.geometry("800x600")
        aplicar_tema(win)
        fig, ax = plt.subplots(figsize=(7, 5))
        if self.chart_type.get() == "Pizza":
            ax.pie(valores, labels=valores.index, autopct="%1.1f%%")
        else:
            ax.barh(valores.index, valores.values)
            ax.invert_yaxis()
            ax.grid(alpha=0.3)
        canvas = FigureCanvasTkAgg(fig, win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        ttk.Button(win, text="Fechar", bootstyle="danger-outline", command=win.destroy).pack(pady=8)

    # -----------------------------
    def _remover_jogador(self):
        if not messagebox.askyesno("Remover", f"Remover o jogador {self.jogador}?"):
            return
        if self.remover_callback:
            self.remover_callback(self.jogador)
        self.win.destroy()
