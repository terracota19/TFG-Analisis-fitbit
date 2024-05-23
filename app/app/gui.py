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
        self.createNotebook()
        self.createLoginFrame()
        self.createRegisterLink()

    def createTopLabel(self):
        self.label = tk.Label(self, text="Bienvenido a HeartPred'it", bg="#686868", fg="white", font=self.fontArial, height=2)
        self.label.pack(pady=5, padx=20, fill=tk.X)

    def createLoginFrame(self):
        self.login_label = tk.Label(self.login_frame, text="Inicio de Sesión", font=self.fontArial, fg="white", bg="#457EAC")
        self.login_label.pack(pady=5, padx=20, fill=tk.X)

        user_label = tk.Label(self.login_frame, text="Correo: (*)", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        user_label.pack(anchor='w', padx=20, pady=(20, 0))

        self.user_entry = tk.Entry(self.login_frame)
        self.user_entry.pack(fill=tk.X, padx=20, pady=5)

        password_label = tk.Label(self.login_frame, text="Contraseña: (*)", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        password_label.pack(anchor='w', padx=20, pady=(20, 0))

        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack(fill=tk.X, padx=20, pady=5)

        self.createLoginButton(self.login_frame)

    def createLoginButton(self, frame):
        self.login_button = tk.Button(frame, text="Inicio de Sesión", fg="white", bg="#457EAC", command=self.on_login_click)
        self.login_button.pack(pady=20, padx=20)

    def loginFailed(self):
        self.login_label = tk.Label(self.login_frame, text="Ups...! Inicio de sesión fallido!", font=self.fontArial, fg="red")
        self.login_label.pack(pady=5, padx=20, fill=tk.X)
        #TTL := TIME TO LIVE
        self.after(2000, lambda: self.login_label.pack_forget())  #expresado en ms 2000 ms = 2s
    
    def register_Failed(self):
        self.register_label = tk.Label(self.register_frame, text="Ups...! Registro fallido! (* Campo Obligatorio)", font=self.fontArial, fg="red")
        self.register_label.pack(pady=5, padx=20, fill=tk.X)
        #TTL := TIME TO LIVE
        self.after(2000, lambda: self.register_label.pack_forget())  #expresado en ms 2000 ms = 2s


    def on_login_click(self):
        user = self.user_entry.get()
        password = self.password_entry.get()
        if self.controller.check_login(user, password):
            # Eliminar todas las pestañas existentes en el notebook
            for tab in self.notebook.tabs():
                self.notebook.forget(tab)
            # Crear una nueva pestaña vacía llamada "HeartPred'it"
            self.createAppNotebook()
        else:
            self.loginFailed()

    def createRegisterLink(self):
        self.register_frame_container = tk.Frame(self)
        self.register_frame_container.pack(pady=10, padx=20, fill=tk.X)
        self.register_frame_container.config(bg="#457EAC")

        self.register_label = tk.Label(self.register_frame_container, text="¿No tienes cuenta? Regístrate aquí", fg="white", cursor="hand2", bg="#457EAC", font=('arial', 12))
        self.register_label.pack(pady=2)
        self.register_label.bind("<Button-1>", self.on_register_click)


    def createAppNotebook(self):
        self.empty_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.empty_frame, text="HeartPred'it",)

    def createNotebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.login_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.login_frame, text="Inicio de Sesión")

        self.register_frame = None

    def on_register_click(self, event):
        if self.register_frame is None:
            self.createRegisterFrame()
        self.notebook.select(self.register_frame)

    def createRegisterFrame(self):
        self.register_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.register_frame, text="Registro")

        register_label = tk.Label(self.register_frame, text="Registro", font=self.fontArial, fg="white", bg="#457EAC")
        register_label.pack(pady=5, padx=20, fill=tk.X)

        email_label = tk.Label(self.register_frame, text="Correo: (*)", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        email_label.pack(anchor='w', padx=20, pady=(20, 0))

        self.register_email_entry = tk.Entry(self.register_frame)
        self.register_email_entry.pack(fill=tk.X, padx=20, pady=5)

        password_label = tk.Label(self.register_frame, text="Contraseña: (*)", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        password_label.pack(anchor='w', padx=20, pady=(20, 0))

        self.register_password_entry = tk.Entry(self.register_frame, show="*")
        self.register_password_entry.pack(fill=tk.X, padx=20, pady=5)

        age_label = tk.Label(self.register_frame, text="Edad: (*)", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        age_label.pack(anchor='w', padx=20, pady=(20, 0))

        self.age_entry = tk.Entry(self.register_frame)
        self.age_entry.pack(fill=tk.X, padx=20, pady=5)

        self.createRegisterButton(self.register_frame)

    def createRegisterButton(self, frame):
        self.register_button = tk.Button(frame, text="Registrarse", fg="white", bg="#457EAC", command=self.on_register_submit)
        self.register_button.pack(pady=20, padx=20)


    def on_register_submit(self):
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        age = self.age_entry.get()

        if self.controller.register(email, password, age) :
            register_tab_index = self.notebook.index(self.register_frame)
            self.notebook.forget(register_tab_index)
            self.notebook.select(self.login_frame)
        else :
            self.register_Failed()



