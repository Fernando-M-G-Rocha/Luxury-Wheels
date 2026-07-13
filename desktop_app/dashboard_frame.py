import tkinter as tk
from tkinter import ttk
from database.db_controller import atualizar_veiculos_para_manutencao, atualizar_reservas_expiradas
from database.dashboard import (
    total_veiculos_disponiveis,
    total_reservas_mes,
    total_financeiro_mes,
    veiculos_alugados_dias_restantes,
    ultimos_clientes,
    veiculos_disponiveis_por_categoria_tipo,
    veiculos_revisao_ate_15_dias,
    veiculos_inspecao_ate_15_dias
)

class DashboardFrame(tk.Frame):
    alerta_exibido = False

    def __init__(self, master):
        super().__init__(master, bg="white")
        self.ordem_colunas = {}
        self.pack(fill="both", expand=True)

        atualizar_reservas_expiradas()
        atualizar_veiculos_para_manutencao()

        self.create_widgets()
        if not DashboardFrame.alerta_exibido:
            self.after(500, self.verificar_alertas_criticos)
            DashboardFrame.alerta_exibido = True

    def create_widgets(self):
        titulo = tk.Label(self, text="Dashboard - Luxury Wheels", font=("Arial", 18, "bold"), bg="white")
        titulo.pack(pady=10)

        # Resumo geral
        frame_resumo = tk.Frame(self, bg="white")
        frame_resumo.pack(pady=10)

        self._criar_resumo_card(frame_resumo, "Veículos Disponíveis", total_veiculos_disponiveis(), 0)
        self._criar_resumo_card(frame_resumo, "Reservas do Mês", total_reservas_mes(), 1)
        self._criar_resumo_card(frame_resumo, "Total Financeiro (€)", f"{total_financeiro_mes():.2f}", 2)

        # Três colunas principais para as tabelas
        corpo = tk.Frame(self, bg="white")
        corpo.pack(fill="both", expand=True, padx=10, pady=10)

        col_esquerda = tk.Frame(corpo, bg="white")
        col_centro   = tk.Frame(corpo, bg="white")
        col_direita  = tk.Frame(corpo, bg="white")

        col_esquerda.pack(side="left", fill="both", expand=True)
        col_centro.pack(side="left", fill="both", expand=True, padx=20)
        col_direita.pack(side="left", fill="both", expand=True)

        # Coluna da esquerda
        self._criar_tabela(col_esquerda, "Veículos alugados (dias restantes)",
            ["Modelo", "Dias Restantes"], veiculos_alugados_dias_restantes())

        self._criar_tabela(col_esquerda, "Últimos Clientes Registados",
            ["Nome", "Email"], ultimos_clientes())

        # Coluna do centro
        self._criar_tabela(col_centro, "Veículos disponíveis por Categoria e Tipo",
            ["Categoria", "Tipo", "Qtd"], veiculos_disponiveis_por_categoria_tipo())

        # Coluna da direita
        self._criar_tabela(col_direita, "Revisão a expirar (15 dias)",
            ["Modelo", "Data Revisão"], veiculos_revisao_ate_15_dias())

        self._criar_tabela(col_direita, "Inspeção a expirar (15 dias)",
            ["Modelo", "Data Inspeção"], veiculos_inspecao_ate_15_dias())

    def _criar_resumo_card(self, master, titulo, valor, coluna):
        card = tk.LabelFrame(master, text=titulo, bg="white", padx=15, pady=10)
        card.grid(row=0, column=coluna, padx=10)
        lbl = tk.Label(card, text=str(valor), font=("Arial", 16, "bold"), bg="white")
        lbl.pack()

    def _criar_tabela(self, master, titulo, colunas, dados):
        frame = tk.LabelFrame(master, text=titulo, bg="white", padx=10, pady=10)
        frame.pack(fill="x", pady=10)

        tree = ttk.Treeview(frame, columns=colunas, show="headings")
        tree.pack(fill="x")

        self.ordem_colunas[tree] = {col: True for col in colunas}

        # Define cabeçalhos com função de ordenação
        for col in colunas:
            tree.heading(col, text=col, command=lambda c=col, t=tree: self._ordenar_por_coluna(t, c))
            tree.column(col, anchor="center", width=150)

        for item in dados:
            tree.insert("", "end", values=item)

    def verificar_alertas_criticos(self):
        from tkinter import messagebox
        from datetime import datetime, timedelta
        from database.db_controller import conectar

        print("A verificar alertas criticos...")
        conn = conectar()
        cursor = conn.cursor()
        hoje = datetime.now()
        limite = hoje + timedelta(days=5)

        # Revisões
        cursor.execute("""
            SELECT marca || ' ' || modelo, data_proxima_revisao
            FROM veiculos
            WHERE data_proxima_revisao <= ?
        """, (limite.strftime('%Y-%m-%d'),))
        revisoes = cursor.fetchall()

        # Inspeções
        cursor.execute("""
            SELECT marca || ' ' || modelo, data_inspecao_obrigatoria
            FROM veiculos
            WHERE data_inspecao_obrigatoria <= ?
        """, (limite.strftime('%Y-%m-%d'),))
        inspecoes = cursor.fetchall()

        conn.close()

        if revisoes or inspecoes:
            msg = "⚠️ ALERTA DE MANUTENÇÃO:\n\n"
            if revisoes:
                msg += "🚗 Revisões a expirar:\n"
                for modelo, data in revisoes:
                    msg += f" - {modelo} (Revisão: {data})\n"
            if inspecoes:
                msg += "\n🛠️ Inspeções a expirar:\n"
                for modelo, data in inspecoes:
                    msg += f" - {modelo} (Inspeção: {data})\n"

            messagebox.showwarning("Alerta Crítico!", msg)

    def _ordenar_por_coluna(self, tree, coluna):
        # Obter dados atuais da treeview
        dados = [(tree.set(k, coluna), k) for k in tree.get_children("")]

        # Verifica se é número ou string
        try:
            dados.sort(key=lambda t: float(t[0]), reverse=not self.ordem_colunas[tree][coluna])
        except ValueError:
            dados.sort(key=lambda t: t[0].lower(), reverse=not self.ordem_colunas[tree][coluna])

        # Reorganiza a ordem visual
        for index, (val, k) in enumerate(dados):
            tree.move(k, "", index)

        # Atualiza a seta nos cabeçalhos
        direcao = "⬇️" if self.ordem_colunas[tree][coluna] else "⬆️"
        for col in tree["columns"]:
            seta = f" {direcao}" if col == coluna else ""
            tree.heading(col, text=col + seta, command=lambda c=col, t=tree: self._ordenar_por_coluna(t, c))

        # Inverte a ordem para próxima vez
        self.ordem_colunas[tree][coluna] = not self.ordem_colunas[tree][coluna]