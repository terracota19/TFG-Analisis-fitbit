import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from app.controllers import Controller
from assets.fonts.fonts import get_arial20
from datetime import datetime as st
import datetime
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("HeartPred'it")
        self.geometry("800x600")

        self.fontArial = get_arial20()

        self.controller = Controller(self)

        self.createLoginAuthFrame()

    def createLoginAuthFrame(self):
        self.login_auth_frame = tk.Frame(self, bg="white")
        self.login_auth_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.createNotebook()
        self.createLoginFrame()

    def createWelcomeLabel(self, frame):
        user_info = self.controller.user_info()
        if user_info:
            texto_personalizado = f"¡Bienvenido, {user_info}!"
            self.label = tk.Label(frame, text=texto_personalizado, bg="#457EAC", fg="white", font=self.fontArial, height=2)
            self.label.pack(pady=5, padx=20, fill=tk.X)
            self.createStatusFrame(frame)  
        else:
            print("No se pudo obtener la información del usuario")

    def createLoginFrame(self):
        self.login_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.login_frame, text="Inicio de Sesión")

        self.login_label = tk.Label(self.login_frame, text="Inicio de Sesión", font=self.fontArial, fg="white", bg="#457EAC")
        self.login_label.pack(pady=5, padx=20, fill=tk.X)
    
        email_label = tk.Label(self.login_frame, text="Correo: (*)", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        email_label.pack(anchor='w', padx=20, pady=(20, 0))

        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.pack(fill=tk.X, padx=20, pady=5)

        password_label = tk.Label(self.login_frame, text="Contraseña: (*)", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        password_label.pack(anchor='w', padx=20, pady=(20, 0))
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack(fill=tk.X, padx=20, pady=5)

        self.createRegisterLink(self.login_frame)
        self.createLoginButton(self.login_frame)

    def createLoginButton(self, frame):
        self.login_button = tk.Button(frame, text="Inicio de Sesión", fg="white", bg="#457EAC", command=self.on_login_click)
        self.login_button.pack(pady=2, padx=2)

    def loginFailed(self):
        self.login_label = tk.Label(self.login_frame, text="Ups...! Inicio de sesión fallido!", font=self.fontArial, fg="red")
        self.login_label.pack(pady=5, padx=20, fill=tk.X)
        self.after(2000, lambda: self.login_label.pack_forget())

    def registerFailed(self):
        self.register_label = tk.Label(self.register_frame, text="Ups...! Registro fallido! (* Campo Obligatorio)", font=self.fontArial, fg="red")
        self.register_label.pack(pady=5, padx=20, fill=tk.X)
        self.after(2000, lambda: self.register_label.pack_forget())

    def on_login_click(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if self.controller.check_login(email, password):
            for tab in self.notebook.tabs():
                self.notebook.forget(tab)
            self.createAppNotebook()
        else:
            self.loginFailed()

    def createRegisterLink(self, frame):
        self.register_frame_container = tk.Frame(frame, bg="#457EAC")
        self.register_frame_container.pack(pady=10, padx=20, fill=tk.X)

        self.register_label = tk.Label(self.register_frame_container, text="¿No tienes cuenta? Regístrate aquí", fg="white", cursor="hand2", bg="#457EAC", font=('arial', 12))
        self.register_label.pack(pady=2)
        self.register_label.bind("<Button-1>", self.on_register_click)

    def createAppNotebook(self):
        self.app_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.app_frame, text="HeartPred'it")
        self.createWelcomeLabel(self.app_frame)

    def createNotebook(self):
        self.notebook = ttk.Notebook(self.login_auth_frame)
        self.notebook.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

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

        user_label = tk.Label(self.register_frame, text="Usuario: (*)", pady=2, fg="white", bg="#457EAC", font=('arial', 14))
        user_label.pack(anchor='w', padx=20, pady=(20, 0))

        self.register_user_entry = tk.Entry(self.register_frame)
        self.register_user_entry.pack(fill=tk.X, padx=20, pady=5)

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
        self.createPredictionButton(self.notebook)

    def createRegisterButton(self, frame):
        self.register_button = tk.Button(frame, text="Registrarse", fg="white", bg="#457EAC", command=self.on_register_submit)
        self.register_button.pack(pady=20, padx=20)

    def createPredictionButton(self,frame):
        self.register_button = tk.Button(frame, text="Predecir", fg="white", bg="#457EAC", command=self.on_predict_submit)
        self.register_button.pack(pady=20, padx=20)

    def on_register_submit(self):
        user = self.register_user_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        age = self.age_entry.get()

        if self.controller.register(user, email, password, age):
            register_tab_index = self.notebook.index(self.register_frame)
            self.notebook.forget(register_tab_index)
            self.notebook.select(self.login_frame)
        else:
            self.registerFailed()

    def on_predict_submit(self):
        print("logica de prediccion, creacion de nuevo notebook")

    def createStatusFrame(self, frame):
        # Create a new frame for the status information
        self.status_frame = tk.Frame(frame, bg="#457EAC")
        self.status_frame.pack(pady=10, padx=20, fill=tk.X)

        #image_path = os.path.abspath("assets/images/mi_pulsera.png")  
        #print(image_path)
        
        self.color_circle = tk.Canvas(self.status_frame, width=50, height=50, bg="#457EAC", highlightthickness=0)
        self.color_circle.grid(row=0, column=1, padx=10, pady=10)
        self.circle = self.color_circle.create_oval(5, 5, 20, 20, fill="green")

        ult_actualizacion = self.controller.last_update()
        fecha_legible = ult_actualizacion.strftime("%A, %d de %B de %Y a las %H:%M:%S")
        texto_actualizacion_pulsera =f"Última actualización: {fecha_legible}"
        self.update_label = tk.Label(self.status_frame, text= texto_actualizacion_pulsera, fg="white", bg="#457EAC", font=('arial', 12))
        self.update_label.grid(row=0, column=0, padx=10, pady=10)

    
        self.update_button = tk.Button(self.status_frame, text="Actualizar", fg="white", bg="#457EAC", command=self.update_status)
        self.update_button.grid(row=1, column=0, columnspan=3, pady=10, padx=10)

    def textLastUpdateLabel(self):
        ult_actualizacion = datetime.datetime.now()
        fecha_legible = ult_actualizacion.strftime("%A, %d de %B de %Y a las %H:%M:%S")
        texto_actualizacion_pulsera =f"Última actualización: {fecha_legible}"
        return texto_actualizacion_pulsera


    def update_status(self):        
        date = self.controller.updateApi_lastUpdate()
        texto_last_update = self.textLastUpdateLabel()
        self.update_label.config(text=texto_last_update)
        #logica de llamada a la api
        



if __name__ == "__main__":
    app = App()
    app.mainloop()
