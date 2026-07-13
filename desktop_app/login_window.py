import tkinter as tk
from tkinter import messagebox
from database import db_controller  # Assumindo que você tenha funções de acesso ao BD

class LoginWindow:
    def __init__(self, master, on_login_success):
        self.master = master
        self.on_login_success = on_login_success
        self.master.title("Login - Luxury Wheels")

        tk.Label(master, text="Email:").grid(row=0, column=0, pady=5)
        tk.Label(master, text="Senha:").grid(row=1, column=0, pady=5)

        self.email_entry = tk.Entry(master)
        self.senha_entry = tk.Entry(master, show="*")

        self.email_entry.grid(row=0, column=1, pady=5)
        self.senha_entry.grid(row=1, column=1, pady=5)

        tk.Button(master, text="Login", command=self.fazer_login).grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(master, text="Registar", command=self.abrir_registro).grid(row=3, column=0, columnspan=2)

    def fazer_login(self):
        email = self.email_entry.get()
        senha = self.senha_entry.get()
        user = db_controller.validar_utilizador(email, senha)
        if user:
            self.master.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Erro", "Credenciais inválidas!")

    def abrir_registro(self):
        RegistroWindow(tk.Toplevel(self.master))

class RegistroWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Registrar")

        tk.Label(master, text="Nome:").grid(row=0, column=0, pady=5)
        tk.Label(master, text="Email:").grid(row=1, column=0, pady=5)
        tk.Label(master, text="Senha:").grid(row=2, column=0, pady=5)

        self.nome_entry = tk.Entry(master)
        self.email_entry = tk.Entry(master)
        self.senha_entry = tk.Entry(master, show="*")

        self.nome_entry.grid(row=0, column=1, pady=5)
        self.email_entry.grid(row=1, column=1, pady=5)
        self.senha_entry.grid(row=2, column=1, pady=5)

        tk.Button(master, text="Confirmar", command=self.registrar).grid(row=3, column=0, columnspan=2, pady=5)

    def registrar(self):
        nome = self.nome_entry.get()
        email = self.email_entry.get()
        senha = self.senha_entry.get()
        sucesso = db_controller.registrar_utilizador(nome, email, senha)
        if sucesso:
            messagebox.showinfo("Sucesso", "Utilizador registado com sucesso!")
            self.master.destroy()
        else:
            messagebox.showerror("Erro", "Erro ao registar utilizador.")