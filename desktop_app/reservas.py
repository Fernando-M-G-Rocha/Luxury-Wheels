import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import db_controller

class ReservaFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.pack(fill="both", expand=True)

        self.reserva_selecionada_id = None
        self.entries = {}
        self.create_widgets()
        self.carregar_reservas()
        self.forma_pagamento_cb = ttk.Combobox(self)
        self.forma_pagamento_cb.pack()
        self.carregar_formas_pagamento()

    def create_widgets(self):
        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=10)

        # Combobox Cliente
        tk.Label(form_frame, text="Cliente:", bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.cliente_cb = ttk.Combobox(form_frame, state="readonly")
        self.cliente_cb.grid(row=0, column=1, padx=5, pady=2)

        # Combobox Veículo
        tk.Label(form_frame, text="Veículo:", bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.veiculo_cb = ttk.Combobox(form_frame, state="readonly")
        self.veiculo_cb.grid(row=1, column=1, padx=5, pady=2)

        # Datas com StringVar e formatação automática
        tk.Label(form_frame, text="Data Início:", bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.data_inicio_var = tk.StringVar()
        self.data_inicio = tk.Entry(form_frame, textvariable=self.data_inicio_var)
        self.data_inicio.grid(row=2, column=1, padx=5, pady=2)
        self.data_inicio.bind("<FocusOut>", self._formatar_data)

        tk.Label(form_frame, text="Data Fim:", bg="white").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.data_fim_var = tk.StringVar()
        self.data_fim = tk.Entry(form_frame, textvariable=self.data_fim_var)
        self.data_fim.grid(row=3, column=1, padx=5, pady=2)
        self.data_fim.bind("<FocusOut>", self._formatar_data)

        # Forma de pagamento
        tk.Label(form_frame, text="Pagamento:", bg="white").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.pagamento_cb = ttk.Combobox(form_frame, state="readonly")
        self.pagamento_cb.grid(row=4, column=1, padx=5, pady=2)

        # Valor total
        tk.Label(form_frame, text="Valor Total:", bg="white").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.valor_total_lbl = tk.Label(form_frame, text="0.00", bg="white")
        self.valor_total_lbl.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        tk.Label(form_frame, text="Estado:", bg="white").grid(row=6, column=0, sticky="e", padx=5, pady=2)
        self.estado_var = tk.StringVar()
        self.estado_cb = ttk.Combobox(form_frame, textvariable=self.estado_var, state="readonly")
        self.estado_cb['values'] = ("Preparando Reserva", "Sendo Usado", "Terminada")
        self.estado_cb.grid(row=6, column=1, padx=5, pady=2)

        # Botões
        botoes_frame = tk.Frame(form_frame, bg="white")
        botoes_frame.grid(row=7, column=0, columnspan=2, pady=10)

        tk.Button(botoes_frame, text="Atualizar", command=self.atualizar_reserva).pack(side="left", pady=10)
        tk.Button(botoes_frame, text="Excluir", command=self.excluir_reserva).pack(side="left", pady=10)

        # Lista de reservas
        self.tree = ttk.Treeview(self, columns=("id", "cliente", "veiculo", "data_inicio", "data_fim", "valor_total", "forma_pagamento", "estado"),
                                 show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, anchor="center", width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.carregar_comboboxes()
        self.configurar_ordenacao(self.tree)

    def carregar_comboboxes(self):
        # Combobox Cliente
        clientes = db_controller.obter_clientes()
        self.clientes_dict = {f"{c[1]} ({c[2]})": c[0] for c in clientes}
        self.cliente_cb['values'] = list(self.clientes_dict.keys())

        # Combobox Veículo (apenas disponíveis)
        veiculos = db_controller.obter_veiculos_disponiveis()
        self.veiculos_dict = {f"{v[1]} {v[2]} ({v[3]})": (v[0], v[7]) for v in veiculos}
        self.veiculo_cb['values'] = list(self.veiculos_dict.keys())

        # Combobox Pagamento
        pagamentos = db_controller.obter_formas_pagamento()
        self.pagamento_dict = {p[1]: p[0] for p in pagamentos}
        self.pagamento_cb['values'] = list(self.pagamento_dict.keys())


    def calcular_valor_total(self, dias, diaria):
        return round(dias * diaria, 2)

    def carregar_reservas(self):
        reservas = db_controller.obter_reservas_detalhado()
        self.tree.delete(*self.tree.get_children())
        for r in reservas:
            self.tree.insert("", "end", values=r)


    def on_select(self, event):
            sel = self.tree.selection()
            if not sel:
                return
            valores = self.tree.item(sel[0])["values"]
            self.reserva_selecionada_id = valores[0]

            self.cliente_cb.set(valores[1])
            self.veiculo_cb.set(valores[2])
            self.data_inicio_var.set(datetime.strptime(valores[3], "%Y-%m-%d").strftime("%Y-%m-%d"))
            self.data_fim_var.set(datetime.strptime(valores[4], "%Y-%m-%d").strftime("%Y-%m-%d"))
            self.valor_total_lbl.config(text=str(valores[5]))
            self.pagamento_cb.set(valores[6])
            self.estado_var.set(valores[7])
    pass

    def atualizar_reserva(self):
        if not self.reserva_selecionada_id:
            messagebox.showwarning("Atenção", "Nenhuma reserva selecionada.")
            return

        try:
            cliente_id = self.clientes_dict[self.cliente_cb.get()]
            veiculo_id, diaria = self.veiculos_dict[self.veiculo_cb.get()]
            data_inicio = datetime.strptime(self.data_inicio_var.get(), "%Y-%m-%d")
            data_fim = datetime.strptime(self.data_fim_var.get(), "%Y-%m-%d")
            dias = (data_fim - data_inicio).days
            valor_total = self.calcular_valor_total(dias, diaria)
            pagamento_id = self.pagamento_dict[self.pagamento_cb.get()]
            estado = self.estado_var.get()

            dados = (
            cliente_id, veiculo_id, data_inicio.strftime("%Y-%m-%d"), data_fim.strftime("%Y-%m-%d"), pagamento_id,
            valor_total, estado)
            db_controller.atualizar_reserva(self.reserva_selecionada_id, dados)
            messagebox.showinfo("Atualizado", "Reserva atualizada com sucesso.")
            self.carregar_reservas()
            self.carregar_comboboxes()
            self.reserva_selecionada_id = None
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar reserva:\n{e}")
    pass

    def _clear_placeholder(self, entry):
        if entry.get() in ("AAAA-MM-DD", "__-__-____"):
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def _add_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg="grey")

    def excluir_reserva(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma reserva.")
            return
        reserva_id = self.tree.item(selecionado[0])["values"][0]
        db_controller.excluir_reserva(reserva_id)
        self.carregar_reservas()
        self.carregar_comboboxes()
        messagebox.showinfo("Removido", "Reserva excluída com sucesso.")

    def _formatar_data(self, event):
        entry = event.widget
        valor = entry.get().strip().replace("/", "-").replace("-", "")
        if len(valor) == 8 and valor.isdigit():
            try:
                data = datetime.strptime(valor, "%d%m%Y")
                entry.delete(0, tk.END)
                entry.insert(0, data.strftime("%Y-%m-%d"))
                return
            except ValueError:
                pass
        for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                data = datetime.strptime(entry.get().strip(), formato)
                entry.delete(0, tk.END)
                entry.insert(0, data.strftime("%Y-%m-%d"))
                return
            except ValueError:
                continue

        messagebox.showerror("Erro", "Data inválida. Use o formato DD-MM-AAAA ou YYYY-MM-DD.")

    def carregar_formas_pagamento(self):
        formas = db_controller.obter_formas_pagamento()  # retorna lista [(id, descricao), ...]
        self.formas_pagamento_dict = {descricao: id for (id, descricao) in formas}
        descricoes = [descricao for (id, descricao) in formas]
        self.forma_pagamento_cb['values'] = descricoes

    def carregar_dados_reserva(self, reserva_id):
        # Buscar dados da reserva pelo id, incluindo forma_pagamento_id
        reserva = db_controller.obter_reserva_por_id(reserva_id)  # você deve implementar esta função
        if reserva:
            cliente_id, veiculo_id, data_inicio, data_fim, forma_pagamento_id, valor_total, estado = reserva[1:8]
            # Preenche os campos do formulário
            self.cliente_cb.set(cliente_id)
            self.veiculo_cb.set(veiculo_id)
            self.data_inicio_var.set(data_inicio)
            self.data_fim_var.set(data_fim)
            self.valor_total_var.set(valor_total)
            # Ajeita a forma de pagamento
            for descricao, id_fp in self.formas_pagamento_dict.items():
                if id_fp == forma_pagamento_id:
                    self.forma_pagamento_cb.set(descricao)
                    break
            self.estado_var.set(estado)

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