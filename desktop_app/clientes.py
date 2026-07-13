import tkinter as tk
from tkinter import ttk
from database import db_controller

class ClienteFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.pack(fill="both", expand=True)

        self.filtro_var = tk.StringVar()
        self.create_widgets()
        self.carregar_clientes()

    def create_widgets(self):
        # Área de filtro
        filtro_frame = tk.Frame(self, bg="white")
        filtro_frame.pack(pady=10)

        tk.Label(filtro_frame, text="Filtrar por Nome / Email:", bg="white").pack(side="left")
        tk.Entry(filtro_frame, textvariable=self.filtro_var).pack(side="left", padx=5)
        tk.Button(filtro_frame, text="Filtrar", command=self.filtrar_clientes).pack(side="left")
        tk.Button(filtro_frame, text="Limpar", command=self.limpar_filtro).pack(side="left", padx=5)

        # Lista de clientes
        self.tree = ttk.Treeview(self, columns=("id", "nome", "email", "telefone"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, anchor="center", width=200)
        self.tree.pack(pady=10, fill="both", expand=True)
        self.configurar_ordenacao(self.tree)

    def carregar_clientes(self):
        clientes = db_controller.obter_clientes()
        self.mostrar_clientes(clientes)

    def mostrar_clientes(self, clientes):
        self.tree.delete(*self.tree.get_children())
        for c in clientes:
            self.tree.insert("", "end", values=c)

    def filtrar_clientes(self):
        termo = self.filtro_var.get().strip()
        if termo:
            clientes = db_controller.buscar_clientes(termo)
            self.mostrar_clientes(clientes)

    def limpar_filtro(self):
        self.filtro_var.set("")
        self.carregar_clientes()

    def configurar_ordenacao(self, treeview):
        self.ordenacao_atual = {"coluna": None, "reverso": False}

        def ordenar(coluna):
            reverso = False
            if self.ordenacao_atual["coluna"] == coluna:
                reverso = not self.ordenacao_atual["reverso"]

            dados = [(treeview.set(k, coluna), k) for k in treeview.get_children('')]

            try:
                dados.sort(key=lambda t: float(t[0]) if t[0].replace('.', '', 1).isdigit() else t[0], reverse=reverso)
            except Exception:
                dados.sort(key=lambda t: t[0], reverse=reverso)

            for index, (_, k) in enumerate(dados):
                treeview.move(k, '', index)

            # Atualiza os cabeçalhos com setas
            for col in treeview["columns"]:
                seta = ""
                if col == coluna:
                    seta = " 🔽" if not reverso else " 🔼"
                treeview.heading(col, text=col + seta, command=lambda _col=col: ordenar(_col))

            self.ordenacao_atual["coluna"] = coluna
            self.ordenacao_atual["reverso"] = reverso

        for col in treeview["columns"]:
            treeview.heading(col, command=lambda _col=col: ordenar(_col))