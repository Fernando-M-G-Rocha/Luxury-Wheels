from desktop_app.veiculos import VeiculoFrame
from desktop_app.clientes import ClienteFrame
from desktop_app.reservas import ReservaFrame
from desktop_app.pagamentos import PagamentoFrame
from dashboard_frame import DashboardFrame
from login_window import LoginWindow
import tkinter as tk


class LuxuryWheelsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Luxury Wheels - Gestão de Frota")
        self.geometry("1900x700")
        self.configure(bg="#f0f0f0")

        # Menu lateral
        self.menu_frame = tk.Frame(self, bg="#2c3e50", width=200)
        self.menu_frame.pack(side="left", fill="y")

        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(side="right", expand=True, fill="both")

        # Botões do menu
        options = [
            "Dashboard",
            "Veículos",
            "Clientes",
            "Reservas",
            "Pagamentos",
            "Exportar"
        ]

        self.botoes_menu = {}

        for opt in options:
            btn = tk.Button(self.menu_frame, text=opt, fg="white", bg="#34495e",
                            font=("Arial", 12), relief="flat", height=2, anchor="w",
                            command=lambda o=opt: self.load_view(o))
            btn.pack(fill="x", padx=10, pady=5)
            self.botoes_menu[opt] = btn

        logout_btn = tk.Button(self.menu_frame, text="Logout", fg="white", bg="#c0392b",
                               font=("Arial", 12), relief="flat", height=2, anchor="w",
                               command=self.logout)
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=10)

        self.load_view("Dashboard")

    def load_view(self, view_name):
        for nome, btn in self.botoes_menu.items():
            if nome == view_name:
                btn.configure(bg="#1abc9c")
            else:
                btn.configure(bg="#34495e")

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if view_name == "Veículos":
            frame = VeiculoFrame(self.main_frame)
        elif view_name == "Clientes":
            frame = ClienteFrame(self.main_frame)
        elif view_name == "Reservas":
            frame = ReservaFrame(self.main_frame)
        elif view_name == "Pagamentos":
            frame = PagamentoFrame(self.main_frame)
        elif view_name == "Dashboard":
            frame = DashboardFrame(self.main_frame)
        elif view_name == "Exportar":
            self.abrir_dialogo_exportar()
        else:
            label = tk.Label(self.main_frame, text=f"Gestão de {view_name}",
                         font=("Arial", 16), bg="white")
            label.pack(pady=50)


    def abrir_dialogo_exportar(self):
        from desktop_app import exportar
        janela = tk.Toplevel(self)
        janela.title("Exportar Dados")
        janela.geometry("300x150")
        janela.configure(bg="white")

        tk.Label(janela, text="Escolha o formato:", bg="white", font=("Arial", 12)).pack(pady=10)
        tk.Button(janela, text="Exportar para CSV",
                  command=lambda: [exportar.exportar_dados("csv"), janela.destroy()]).pack(pady=5)
        tk.Button(janela, text="Exportar para Excel",
                  command=lambda: [exportar.exportar_dados("xlsx"), janela.destroy()]).pack(pady=5)

    def logout(self):
        self.destroy()
        root = tk.Tk()
        LoginWindow(root, on_login_success=iniciar_app)
        root.mainloop()


# ✅ Função global para iniciar a aplicação após login bem-sucedido
def iniciar_app():
    root = LuxuryWheelsApp()
    root.mainloop()


# ✅ Inicializar com tela de login
if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root, on_login_success=iniciar_app)
    root.mainloop()