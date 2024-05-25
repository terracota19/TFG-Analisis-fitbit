import tkinter as tk
import datetime
import os
import matplotlib.pyplot as plt


from tkinter import ttk
from tkinter import font as tkFont
from app.controllers import Controller
from datetime import datetime 
from datetime import timedelta
from tkinter import PhotoImage
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import webbrowser

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("HeartPred'it")
        self.geometry("800x600")

        self.controller = Controller(self)
        
        #Server
        self.flask_thread = threading.Thread(target=self.controller)
        self.flask_thread.daemon = True
        self.flask_thread.start()

        self.current_date = datetime.now()
        self.year = self.current_date.year
        self.month = self.current_date.month

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
            self.label = tk.Label(frame, text=texto_personalizado, bg="#457EAC", fg="white", font=("arial", 20), height=2)
            self.label.pack(pady=5, padx=20, fill=tk.X)
            self.createStatusFrame(frame)  
        else:
            print("No se pudo obtener la información del usuario")

    def createLoginFrame(self):
        self.login_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.login_frame, text="Inicio de Sesión")

        self.login_label = tk.Label(self.login_frame, text="Inicio de Sesión", font=("arial", 20), fg="white", bg="#457EAC")
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
        self.login_label = tk.Label(self.login_frame, text="Ups...! Inicio de sesión fallido!", font=("arial", 20), fg="red")
        self.login_label.pack(pady=5, padx=20, fill=tk.X)
        self.after(2000, lambda: self.login_label.pack_forget())

    def registerFailed(self):
        self.register_label = tk.Label(self.register_frame, text="Ups...! Registro fallido! (* Campo Obligatorio)", font=("arial", 20), fg="red")
        self.register_label.pack(pady=5, padx=20, fill=tk.X)
        self.after(2000, lambda: self.register_label.pack_forget())

    def on_login_click(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if self.controller.check_login(email, password):
             #check access_token
            if self.controller.fitbitAPI.access_token_is_expired() :
                self.controller.fitbitAPI.refresh_access_token() 

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

        register_label = tk.Label(self.register_frame, text="Registro", font=("arial", 20), fg="white", bg="#457EAC")
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
        

    def createStatusFrame(self, frame):
        
        self.status_frame = tk.Frame(frame, bg="#457EAC")
        self.status_frame.pack(pady=10, padx=20, fill=tk.X)

        #self.color_circle = tk.Canvas(self.status_frame, width=50, height=50, bg="#457EAC", highlightthickness=0)
        #self.color_circle.grid(row=0, column=0)
        #self.circle = self.color_circle.create_oval(5, 5, 20, 20, fill="green")

        ult_actualizacion = self.controller.last_update()
        fecha_legible = ult_actualizacion.strftime("%A, %d de %B de %Y a las %H:%M:%S")
        texto_actualizacion_pulsera = f"Última actualización: {fecha_legible}"
        self.update_label = tk.Label(self.status_frame, text=texto_actualizacion_pulsera, fg="white", bg="#457EAC", font=('arial', 14))
        self.update_label.grid(row=0, column=1)

        self.update_button = tk.Button(self.status_frame, width=10, height=1,text="Actualizar", fg="white", bg="#457EAC", command=self.update_status)
        self.update_button.grid(row=1, column=1, columnspan=3)
        self.createPredictionButton(self.status_frame)

    def createRegisterButton(self, frame):

        self.authorize_button = tk.Button(self.register_frame, text="Paso 1: Autorizar con Fitbit", command=self.controller.authorize_with_fitbit)
        self.authorize_button.pack(padx=10,pady=10)


        self.register_button = tk.Button(frame, text="Paso 2: Registrarse", fg="white", bg="#457EAC", command=self.on_register_submit)
        self.register_button.pack(pady=20, padx=20)

    def createPredictionButton(self,frame):
        self.register_button = tk.Button(frame,width=10, height=1, text="Predecir", fg="white", bg="#457EAC", command=self.on_predict_submit)
        self.register_button.grid(row = 2, column= 1, pady=20, padx=20)

        self.prediction_frame = None



    def on_register_submit(self):
        user = self.register_user_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        age = self.age_entry.get()

        user_id = self.controller.fitbitAPI.user_id
        access_token = self.controller.fitbitAPI.access_token
        refresh_token = self.controller.fitbitAPI.refresh_token
        expires_in = self.controller.fitbitAPI.expires_at


        if self.controller.register(user, email, password, age, user_id, access_token, refresh_token,expires_in):
            register_tab_index = self.notebook.index(self.register_frame)
            self.notebook.forget(register_tab_index)
            self.notebook.select(self.login_frame)
        else:
            self.registerFailed()

    def on_predict_submit(self):
        if self.prediction_frame is None:
            self.createPredictionFrame()
        self.notebook.select(self.prediction_frame)

    def createPredictionFrame(self):
        self.prediction_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.prediction_frame, text="Predicción")

        self.createPredictionInfo()

        # Botón de actualización
        self.update_prediction_button = tk.Button(self.prediction_frame, width=10, height=1, text="Actualizar", fg="white", bg="#457EAC", command=self.update_status)
        self.update_prediction_button.grid(row=0, column=2, columnspan=3, pady=10)  


    def createPredictionInfo(self):
        # Datos de ejemplo para el gráfico
        predicciones = [1, 2, 3, 4, 5]
        datos_test = [10, 15, 7, 10, 5]

        fig, ax = plt.subplots(figsize=(5, 4))  
        ax.plot(predicciones, datos_test)

        
        ax.set_xlabel('Minutos')
        ax.set_ylabel('HeartRate')
        canvas = FigureCanvasTkAgg(fig, master=self.prediction_frame)
        canvas.draw()
        canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor=tk.CENTER)

      


    def textLastUpdateLabel(self):
        ult_actualizacion = datetime.now()
        fecha_legible = ult_actualizacion.strftime("%A, %d de %B de %Y a las %H:%M:%S")
        texto_actualizacion_pulsera =f"Última actualización: {fecha_legible}"
  
        return texto_actualizacion_pulsera
    
    def get_dates_in_month(self, year, month):
        num_days = (datetime(year, month + 1, 1) - datetime(year, month, 1)).days
        return [datetime(year, month, day).strftime("%Y-%m-%d") for day in range(1, num_days + 1)]


    def update_status(self):        
        date = self.controller.updateApi_lastUpdate()
        texto_last_update = self.textLastUpdateLabel()
        self.update_label.config(text=texto_last_update)
        #retrieve data from api
        dates = self.get_dates_in_month(self.year, self.month)
        self.controller.fitbitAPI.getHeartRateData("1min", "00:00", "23:59", dates)
        #getHeartRateData(self, detail_level, start_time, end_time, dates)
       
        
   
        