import tkinter as tk
import os
from tkinter import ttk, messagebox
from database import db_controller
from datetime import datetime

CAMINHO_IMAGENS = "web_app/static/images"


def validar_imagem(nome_arquivo):
    caminho_completo = os.path.join(CAMINHO_IMAGENS, nome_arquivo)
    return os.path.isfile(caminho_completo)

class VeiculoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")

        self.filtro_var = tk.StringVar()
        self.pack(fill="both", expand=True)

        self.create_widgets()
        self.carregar_veiculos()
        self.veiculo_selecionado_id = None
        self.bind_all("<Button-1>", self._deselecionar_ao_clicar_fora, add="+")


    def create_widgets(self):
        botoes_frame = tk.Frame(self, bg="white")
        botoes_frame.pack(pady=10)

        self.adicionar_btn = tk.Button(botoes_frame, text="Adicionar Veículo", command=self.abrir_formulario_adicionar)
        self.adicionar_btn.grid(row=0, column=0)

        self.atualizar_btn = tk.Button(botoes_frame, text="Atualizar Veículo", command=self.preparar_atualizacao)
        self.atualizar_btn.grid(row=0, column=1)

        self.excluir_btn = tk.Button(botoes_frame, text="Excluir Selecionado", command=self.excluir_veiculo)
        self.excluir_btn.grid(row=0, column=2)

        # --- Área de Filtro ---
        filtro_frame = tk.Frame(self, bg="white")
        filtro_frame.pack(pady=5)

        tk.Label(filtro_frame, text="Filtrar por Marca / Modelo / Categoria:", bg="white").pack(side="left")
        tk.Entry(filtro_frame, textvariable=self.filtro_var).pack(side="left", padx=5)
        tk.Button(filtro_frame, text="Filtrar", command=self.filtrar_veiculos).pack(side="left")
        tk.Button(filtro_frame, text="Limpar Filtro", command=self.limpar_filtro).pack(side="left", padx=5)

        # --- Lista ---
        nomes_colunas = {
            "id": "ID",
            "marca": "Marca",
            "modelo": "Modelo",
            "categoria": "Categoria",
            "transmissao": "Transmissão",
            "tipo": "Tipo",
            "capacidade_pessoas": "Capacidade",
            "valor_diaria": "Valor Diária",
            "data_ultima_revisao": "Última Revisão",
            "data_proxima_revisao": "Próxima Revisão",
            "data_inspecao_obrigatoria": "Inspeção Obrigatória",
            "em_manutencao": "Em Manutenção",
            "disponivel": "Disponível"
        }
        self.tree = ttk.Treeview(self, columns=tuple(nomes_colunas.keys()), show="headings")
        for col in self.tree["columns"]:
            texto = nomes_colunas.get(col, col)
            self.tree.heading(col, text=texto)
            self.tree.column(col, width=120, anchor='center')

        self.tree.pack(pady=10, fill="both", expand=True)

        scroll_x = tk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=scroll_x.set)
        scroll_x.pack(fill="x", side="bottom")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.configurar_ordenacao(self.tree)

    def on_tree_select(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            item = self.tree.item(selecionado[0])
            self.veiculo_selecionado_id = item["values"][0]

    def carregar_veiculos(self):
        veiculos = db_controller.obter_veiculos()
        self.mostrar_veiculos(veiculos)

    def mostrar_veiculos(self, veiculos):
        self.tree.delete(*self.tree.get_children())

        for veiculo in veiculos:
            veiculo = list(veiculo)
            veiculo[11] = "Sim" if veiculo[11] else "Não"
            veiculo[12] = "Sim" if veiculo[12] else "Não"
            self.tree.insert("", "end", values=veiculo)

    def formatar_data_para_iso(self, data_str):
        try:
            if "-" in data_str:
                return datetime.strptime(data_str, "%d-%m-%Y").strftime("%Y-%m-%d")
            elif "/" in data_str:
                return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            elif len(data_str) == 8 and data_str.isdigit():
                return datetime.strptime(data_str, "%d%m%Y").strftime("%Y-%m-%d")
            return data_str  # já pode estar no formato correto
        except Exception:
            return data_str

    def adicionar_veiculo(self):
        try:
            dados = (
                self.entries["marca"].get(),
                self.entries["modelo"].get(),
                self.entries["categoria"].get(),
                self.entries["transmissao"].get(),
                self.entries["tipo"].get(),
                int(self.entries["capacidade_pessoas"].get()),
                float(self.entries["valor_diaria"].get()),
                self.formatar_data_para_iso(self.entries["data_ultima_revisao"].get()),
                self.formatar_data_para_iso(self.entries["data_proxima_revisao"].get()),
                self.formatar_data_para_iso(self.entries["data_inspecao_obrigatoria"].get()),
                0,
                1,
                self.entries["imagem"].get()
            )
            db_controller.adicionar_veiculo(dados)
            self.carregar_veiculos()
            messagebox.showinfo("Sucesso", "Veículo adicionado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar veículo: {e}")

    def excluir_veiculo(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um veículo para excluir.")
            return

        veiculo_id = self.tree.item(selecionado[0])["values"][0]
        db_controller.excluir_veiculo(veiculo_id)
        self.carregar_veiculos()
        messagebox.showinfo("Removido", "Veículo excluído com sucesso.")

    def atualizar_veiculo(self):
        if not hasattr(self, 'veiculo_selecionado_id') or not self.veiculo_selecionado_id:
            messagebox.showwarning("Aviso", "Selecione um veículo para atualizar.")
            return

        self.abrir_janela_veiculo(modo='atualizar')

        try:
            dados = (
                self.entries["marca"].get(),
                self.entries["modelo"].get(),
                self.entries["categoria"].get(),
                self.entries["transmissao"].get(),
                self.entries["tipo"].get(),
                int(self.entries["capacidade_pessoas"].get()),
                float(self.entries["valor_diaria"].get()),
                self.formatar_data_para_iso(self.entries["data_ultima_revisao"].get()),
                self.formatar_data_para_iso(self.entries["data_proxima_revisao"].get()),
                self.formatar_data_para_iso(self.entries["data_inspecao_obrigatoria"].get()),
                0,
                1,
                self.entries["imagem"].get()
            )
            db_controller.atualizar_veiculo(self.veiculo_selecionado_id, dados)
            self.carregar_veiculos()
            messagebox.showinfo("Atualizado", "Veículo atualizado com sucesso!")
            self.veiculo_selecionado_id = None
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar veículo: {e}")

    def _formatar_data(self, event):
        entry = event.widget
        valor = entry.get().strip().replace("/", "").replace("-", "")

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

        messagebox.showerror("Erro", "Data inválida. Use DD-MM-AAAA ou YYYY-MM-DD.")

    def filtrar_veiculos(self):
        filtro = self.filtro_var.get().strip()
        if filtro:
            veiculos = db_controller.buscar_veiculos(filtro)
            self.mostrar_veiculos(veiculos)

    def limpar_filtro(self):
        self.filtro_var.set("")
        self.carregar_veiculos()

    def _deselecionar_ao_clicar_fora(self, event):
        try:
            widget = event.widget
            ignorar_widgets = [self.tree, self.adicionar_btn, self.atualizar_btn, self.excluir_btn]

            if widget not in ignorar_widgets:
                if self.tree.winfo_exists():
                    self.tree.selection_remove(*self.tree.selection())
                self.veiculo_selecionado_id = None
        except Exception:
            pass

    def abrir_formulario_veiculo(self, modo="adicionar", dados=None, veiculo_id=None):
        janela = tk.Toplevel(self)
        janela.title("Adicionar Veículo" if modo == "adicionar" else "Atualizar Veículo")

        entradas = {}

        campos = [
            ("Marca", "marca"),
            ("Modelo", "modelo"),
            ("Categoria", "categoria"),
            ("Transmissão", "transmissao"),
            ("Tipo", "tipo"),
            ("Capacidade", "capacidade_pessoas"),
            ("Valor Diária", "valor_diaria"),
            ("Última Revisão", "data_ultima_revisao"),
            ("Próxima Revisão", "data_proxima_revisao"),
            ("Inspeção Obrigatória", "data_inspecao_obrigatoria"),
            ("Imagem (ex: bmw.jpg)", "imagem")
        ]

        for i, (label, key) in enumerate(campos):
            tk.Label(janela, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            entry = tk.Entry(janela)
            entry.grid(row=i, column=1, padx=5, pady=2)

            if dados and key in dados:
                valor = dados[key]
                # Tenta formatar campos de data
                if "data" in key and valor and "-" in valor:
                    try:
                        valor = datetime.strptime(valor, "%Y-%m-%d").strftime("%Y-%m-%d")
                    except:
                        pass
                entry.insert(0, valor)

            if "data" in key:
                entry.bind("<FocusOut>", self._formatar_data)

            entradas[key] = entry

        def confirmar():
            try:
                if modo == "adicionar":
                    dados_form = (
                        entradas["marca"].get(),
                        entradas["modelo"].get(),
                        entradas["categoria"].get(),
                        entradas["transmissao"].get(),
                        entradas["tipo"].get(),
                        int(entradas["capacidade_pessoas"].get()),
                        float(entradas["valor_diaria"].get()),
                        self.formatar_data_para_iso(entradas["data_ultima_revisao"].get()),
                        self.formatar_data_para_iso(entradas["data_proxima_revisao"].get()),
                        self.formatar_data_para_iso(entradas["data_inspecao_obrigatoria"].get()),
                        0,  # em_manutencao
                        1,  # disponivel
                        entradas["imagem"].get()
                    )
                    nome_imagem = entradas["imagem"].get()
                    if not validar_imagem(nome_imagem):
                        messagebox.showerror("Erro",
                                             f"A imagem '{nome_imagem}' não foi encontrada em '{CAMINHO_IMAGENS}'")
                        return
                    db_controller.adicionar_veiculo(dados_form)
                else:
                    dados_update = (
                        entradas["marca"].get(),
                        entradas["modelo"].get(),
                        entradas["categoria"].get(),
                        entradas["transmissao"].get(),
                        entradas["tipo"].get(),
                        int(entradas["capacidade_pessoas"].get()),
                        float(entradas["valor_diaria"].get()),
                        self.formatar_data_para_iso(entradas["data_ultima_revisao"].get()),
                        self.formatar_data_para_iso(entradas["data_proxima_revisao"].get()),
                        self.formatar_data_para_iso(entradas["data_inspecao_obrigatoria"].get()),
                        0,
                        1,
                        entradas["imagem"].get()
                    )
                    db_controller.atualizar_veiculo(veiculo_id, dados_update)
                self.carregar_veiculos()
                janela.destroy()
                if modo == "atualizar":
                    print("Atualizando com dados:", dados_update, "ID:", self.veiculo_selecionado_id)
                else:
                    print("Veículo adicionado com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(janela, text="Confirmar", command=confirmar).grid(row=len(campos), column=0, columnspan=2, pady=10)

    def preparar_atualizacao(self):
        if not self.veiculo_selecionado_id:
            messagebox.showwarning("Aviso", "Selecione um veículo para atualizar.")
            return

        selecionado = self.tree.selection()
        if not selecionado:
            return

        item = self.tree.item(selecionado[0])["values"]

        chaves = [
            "marca", "modelo", "categoria", "transmissao", "tipo",
            "capacidade_pessoas", "valor_diaria",
            "data_ultima_revisao", "data_proxima_revisao", "data_inspecao_obrigatoria","em_manutencao","disponivel", "imagem"
        ]

        # Convertendo os valores para texto
        dados = dict(zip(chaves, [str(v) for v in item[1:14]]))

        self.abrir_formulario_veiculo("atualizar", dados, veiculo_id=self.veiculo_selecionado_id)

    def abrir_formulario_adicionar(self):
        self.abrir_formulario_veiculo("adicionar")

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
