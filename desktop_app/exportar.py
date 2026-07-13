import os
import sqlite3
import pandas as pd
from tkinter import filedialog, messagebox

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'luxury_wheels.db')
DB_PATH = os.path.abspath(DB_PATH)

def exportar_dados(formato="csv"):
    caminho_ficheiro = filedialog.askdirectory(title="Escolha a pasta para guardar os ficheiros")
    if not caminho_ficheiro:
        return

    conn = sqlite3.connect(DB_PATH)
    tabelas = ["veiculos", "clientes", "reservas", "formas_pagamento"]

    for tabela in tabelas:
        df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
        nome_arquivo = f"{caminho_ficheiro}/{tabela}.{formato}"

        try:
            if formato == "csv":
                df.to_csv(nome_arquivo, index=False)
            else:
                df.to_excel(nome_arquivo, index=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar {tabela}: {e}")
            return

    conn.close()
    messagebox.showinfo("Sucesso", f"Dados exportados como {formato.upper()} com sucesso!")