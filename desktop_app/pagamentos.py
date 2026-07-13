import tkinter as tk
from tkinter import ttk, messagebox
from database import db_controller

class PagamentoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.pack(fill="both", expand=True)
        self.pagamento_selecionado_id = None
        self.create_widgets()
        self.carregar_formas_pagamento()

    def create_widgets(self):
        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Forma de Pagamento:", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.nome_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.nome_var).grid(row=0, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="Adicionar", command=self.adicionar).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Atualizar", command=self.atualizar).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Excluir", command=self.excluir).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self, columns=("id", "Descrição"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("Descrição", text="Forma de Pagamento")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("Descrição", width=200, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.configurar_ordenacao(self.tree)

    def carregar_formas_pagamento(self):
        self.tree.delete(*self.tree.get_children())
        formas = db_controller.obter_formas_pagamento()
        for f in formas:
            self.tree.insert("", "end", values=f)

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            valores = self.tree.item(sel[0])["values"]
            self.pagamento_selecionado_id = valores[0]
            self.nome_var.set(valores[1])

    def adicionar(self):
        nome = self.nome_var.get().strip()
        if nome:
            try:
                db_controller.adicionar_forma_pagamento(nome)
                self.carregar_formas_pagamento()
                self.nome_var.set("")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar:\n{e}")
        else:
            messagebox.showwarning("Atenção", "Preencha o nome.")

    def atualizar(self):
        if self.pagamento_selecionado_id:
            nome = self.nome_var.get().strip()
            try:
                db_controller.atualizar_forma_pagamento(self.pagamento_selecionado_id, nome)
                self.carregar_formas_pagamento()
                self.nome_var.set("")
                self.pagamento_selecionado_id = None
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar:\n{e}")
        else:
            messagebox.showwarning("Atenção", "Selecione uma forma de pagamento.")

    def excluir(self):
        if self.pagamento_selecionado_id:
            try:
                db_controller.excluir_forma_pagamento(self.pagamento_selecionado_id)
                self.carregar_formas_pagamento()
                self.nome_var.set("")
                self.pagamento_selecionado_id = None
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir:\n{e}")
        else:
            messagebox.showwarning("Atenção", "Selecione uma forma de pagamento.")

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

            # Atualiza cabeçalhos com setas
            for col in treeview["columns"]:
                seta = ""
                if col == coluna:
                    seta = " 🔽" if not reverso else " 🔼"
                treeview.heading(col, text=col + seta, command=lambda _col=col: ordenar(_col))

            self.ordenacao_atual["coluna"] = coluna
            self.ordenacao_atual["reverso"] = reverso

        for col in treeview["columns"]:
            treeview.heading(col, command=lambda _col=col: ordenar(_col))