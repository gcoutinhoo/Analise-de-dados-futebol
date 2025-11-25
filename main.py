# main.py
import os
import shutil
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog

from src.ui import aplicar_tema
from src.analisador import JanelaJogador


class MainApp:
    def __init__(self, root):
        aplicar_tema(root)

        root.title("Sistema de Scouting")
        root.geometry("650x520")

        ttk.Label(
            root,
            text="Sistema de Análise de Jogadores",
            font=("Helvetica", 22, "bold")
        ).pack(pady=20)

        ttk.Button(
            root,
            text="Adicionar Jogador",
            bootstyle="success-outline",
            command=self.add_jogador
        ).pack(pady=10)

        # LISTA DE JOGADORES
        self.lista = ttk.Treeview(root, columns=["nome"], show="headings", height=10)
        self.lista.heading("nome", text="Jogadores cadastrados")
        self.lista.pack(fill="both", expand=True, padx=20, pady=10)

        # Abrir com duplo clique
        self.lista.bind("<Double-1>", self.abrir_jogador)

        # Botão remover jogador selecionado
        ttk.Button(
            root,
            text="🗑 Remover Jogador Selecionado",
            bootstyle="danger",
            command=self.remover_atleta_selecionado
        ).pack(pady=5)

        os.makedirs("data/jogadores", exist_ok=True)
        self.carregar_jogadores()

    # ============================================
    def carregar_jogadores(self):
        self.lista.delete(*self.lista.get_children())
        base = "data/jogadores"

        for item in os.listdir(base):
            caminho = os.path.join(base, item)
            if os.path.isdir(caminho):
                self.lista.insert("", "end", values=[item])

    # ============================================
    def add_jogador(self):
        pasta = filedialog.askdirectory(title="Escolher pasta do jogador")
        if not pasta:
            return

        nome = os.path.basename(pasta)
        destino = os.path.join("data/jogadores", nome)

        os.makedirs(destino, exist_ok=True)

        # COPIAR SOMENTE CSVs VÁLIDOS (NUNCA ._ARQUIVO)
        count = 0
        for arquivo in os.listdir(pasta):
            if arquivo.startswith("._"):
                continue
            if not arquivo.lower().endswith(".csv"):
                continue

            origem = os.path.join(pasta, arquivo)
            destino_arquivo = os.path.join(destino, arquivo)
            shutil.copy2(origem, destino_arquivo)
            count += 1

        messagebox.showinfo(
            "Sucesso",
            f"Jogador '{nome}' adicionado com {count} arquivos CSV."
        )

        self.carregar_jogadores()

    # ============================================
    def abrir_jogador(self, event):
        item = self.lista.item(self.lista.selection())
        jogador = item["values"][0]

        JanelaJogador(self.lista, jogador, remover_callback=self.remover_atleta)

    # ============================================
    def remover_atleta(self, jogador):
        pasta = os.path.join("data/jogadores", jogador)

        if not os.path.exists(pasta):
            messagebox.showerror("Erro", "Pasta do jogador não encontrada!")
            return

        confirm = messagebox.askyesno(
            "Remover Jogador",
            f"Tem certeza que deseja remover todos os dados de {jogador}?\n"
            "⚠ Esta ação não pode ser desfeita!"
        )

        if not confirm:
            return

        try:
            shutil.rmtree(pasta)
            messagebox.showinfo("Sucesso", f"Jogador {jogador} removido!")
            self.carregar_jogadores()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível remover:\n{e}")

    # ============================================
    def remover_atleta_selecionado(self):
        sel = self.lista.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um jogador para remover.")
            return

        jogador = self.lista.item(sel)["values"][0]
        self.remover_atleta(jogador)


if __name__ == "__main__":
    root = ttk.Window()
    app = MainApp(root)
    root.mainloop()
