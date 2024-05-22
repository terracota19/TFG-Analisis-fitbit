import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from app.controllers import Controller
from assets.fonts.fonts import get_arial20

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("HeartPred'it")
        self.geometry("700x600")

        # MACROS
        self.fontArial = get_arial20()

        self.controller = Controller(self)

        self.createTopLabel()
        self.createFrame()
        self.createRegisterLink()

    def createFrame(self):
      
        self.formFrame = tk.Frame(self)
        self.formFrame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.formFrame.config(bg="#457EAC")

        self.login = tk.Label(self.formFrame, text="Inicio de Sesión", font=self.fontArial, fg="white", bg="#457EAC")
        self.login.pack(pady=5, padx=20, fill=tk.X)

        user_label = tk.Label(self.formFrame, text="Usuario/Correo:", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        user_label.pack(anchor='w', padx=20, pady=(20, 0))
        
        
        self.user_entry = tk.Entry(self.formFrame)
        self.user_entry.pack(fill=tk.X, padx=20, pady=5)

        password_label = tk.Label(self.formFrame, text="Contraseña:", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        password_label.pack(anchor='w', padx=20, pady=(20, 0))

        self.password_entry = tk.Entry(self.formFrame, show="*")
        self.password_entry.pack(fill=tk.X, padx=20, pady=5)

        self.createLoginButton()

    def createLoginButton(self):
        self.loginButton = tk.Button(self.formFrame, text="Inicio de Sesión", fg="white", bg="#457EAC", command=self.on_login_click)
        self.loginButton.pack(pady=20, padx=20)

    def on_login_click(self):
        user = self.user_entry.get()
        password = self.password_entry.get()
        self.controller.check_login(user, password)


    def createTopLabel(self):
        self.label = tk.Label(self, text="Bienvenido a HeartPred'it", bg="#686868", fg="white", font=self.fontArial, height=2)
        self.label.pack(pady=5, padx=20, fill=tk.X)

    def createRegisterLink(self):
        self.registerFrame = tk.Frame(self)
        self.registerFrame.pack(pady=10, padx=20, fill=tk.X)
        self.registerFrame.config(bg="#457EAC")
        self.registerLabel = tk.Label(self.registerFrame, text="¿No tienes cuenta? Regístrate aquí", fg="white", cursor="hand2", bg="#457EAC", font=('arial', 12))
        self.registerLabel.pack(pady=2)
        self.registerLabel.bind("<Button-1>", self.on_register_click)

    def on_register_click(self, event):
        user = self.user_entry.get()
        password = self.password_entry.get()
        self.controller.register(user,password)

    def display_query_results(self):
        query_results = self.controller.get_query_results()  
        query_text = "Resultados de la consulta:\n"
        for result in query_results:
            query_text += f"Correo: {result['email']}, Edad: {result['edad']}\n" 
        
        self.label.config(text=query_text)

if __name__ == "__main__":
    app = App()
    app.mainloop()
