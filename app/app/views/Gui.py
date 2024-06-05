import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from app.controllers.Controller import Controller
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import time
import webbrowser

#Exceptions
from app.exceptions.UserRegistrationError import UserRegistrationError
from app.exceptions.UserLogInError import UserLogInError

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HeartPred'it")
        self.geometry("870x600")
        self.controller = Controller(self)

        self.is_authorized = False
        self.popup =None
        self.authorize_fitbit_button = None

        self.setup_ui()
        self.register_frame = None
        self.prediction_frame = None
        self.progress_var = tk.DoubleVar()

    def setup_ui(self):
        self.login_auth_frame = tk.Frame(self, bg="white")
        self.login_auth_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.notebook = ttk.Notebook(self.login_auth_frame)
        self.notebook.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.create_login_frame()
      
        self.controller.set_login_frame(self.login_frame)

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.login_frame, text="Inicio de Sesión")
        self.create_label(self.login_frame, "Inicio de Sesión", 20)
        self.create_entry(self.login_frame, "Correo: (*)", False, 'email_entry')
        self.create_entry(self.login_frame, "Contraseña: (*)", True, 'password_entry')
        self.create_register_link(self.login_frame)
        self.create_button(self.login_frame, "Inicio de Sesión", self.on_login_click)

    def create_label(self, frame, text, size, fg="white", bg="#457EAC"):
        label = tk.Label(frame, text=text, font=("arial", size), fg=fg, bg=bg)
        label.pack(pady=5, padx=20, fill=tk.X)

    def create_entry(self, frame, text, show, attr_name):
        tk.Label(frame, text=text, pady=2, fg="white", bg="#457EAC", font=('arial', 14)).pack(anchor='w', padx=20, pady=(20, 0))
        entry = tk.Entry(frame, show="*" if show else "")
        entry.pack(fill=tk.X, padx=20, pady=5)
        setattr(self, attr_name, entry)

    def create_register_link(self, frame):
        container = tk.Frame(frame, bg="#457EAC")
        container.pack(pady=10, padx=20, fill=tk.X)
        register_label = tk.Label(container, text="¿No tienes cuenta? Regístrate aquí", fg="white", cursor="hand2", bg="#457EAC", font=('arial', 12))
        register_label.pack(pady=2)
        register_label.bind("<Button-1>", self.on_register_click)

    def select_login_frame(self):
        for tab_id in self.notebook.tabs():
            tab_name = self.notebook.tab(tab_id, "text")
            if tab_name == "Inicio de Sesión":
                self.notebook.select(tab_id)
                break 

    def create_button(self, frame, text, command, state="normal", label_var=None):
        container = tk.Frame(frame, bg="#457EAC")
        container.pack(pady=2)
        button = tk.Button(container, text=text, fg="white", bg="#457EAC", state=state, command=lambda: self.button_click(command, label_var), font=("arial", 12))
        button.pack(side=tk.LEFT)  
        if label_var is not None:
            label = tk.Label(container, textvariable=label_var, fg="green", bg="#457EAC")
            label.pack(side=tk.LEFT, pady=5)
        return button

    def button_click(self, command, label_var):
        command()
        if label_var is not None:
            label_var.set("✓")

    def on_login_click(self):

        try:
            email = self.email_entry.get()
            password = self.password_entry.get()

            if self.controller.check_login(email, password):
                self.controller.updateFitbitUserInfo(email)
                for tab in self.notebook.tabs():
                    self.notebook.forget(tab)
                self.create_app_notebook()

        except UserLogInError as e: 
            self.show_error_message(self.login_frame, e.getMessage())
            return False
        
       
        else:
            self.show_error_message(self.login_frame, "Ups...! Inicio de sesión fallido!")

    def show_error_message(self, frame, text):
        error_label = tk.Label(frame, text=text, font=("arial", 20), fg="red")
        error_label.pack(pady=5, padx=20, fill=tk.X)
        self.after(2000, error_label.pack_forget)

    def create_app_notebook(self):
        self.app_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.app_frame, text="HeartPred'it")
        
        header_frame = tk.Frame(self.app_frame, bg="#457EAC")
        header_frame.pack(side=tk.TOP, fill=tk.X)

        logout_button = tk.Button(header_frame, text="Cerrar Sesión", fg="white", bg="#457EAC", command=self.logout)
        logout_button.pack(side=tk.RIGHT, padx=20, pady=10)

        self.create_welcome_label(self.app_frame)


    def logout(self):
        self.controller.logout()
       
    
    def create_welcome_label(self, frame):
        user_info = self.controller.user_info()
        if user_info:
            self.create_label(frame, f"¡Bienvenido, {user_info}!", 20)
            self.create_status_frame(frame)

    def create_status_frame(self, frame):
        self.status_frame = tk.Frame(frame, bg="#457EAC")
        self.status_frame.pack(pady=10, padx=20, fill=tk.X)
        last_update = self.controller.last_update().strftime("%A, %d de %B de %Y a las %H:%M:%S")
        self.create_label(self.status_frame, f"Última actualización: {last_update}", 14, fg="white", bg="#457EAC")
        self.create_button(self.status_frame, "Actualizar", self.update_status)
        self.create_button(self.status_frame, "Predecir", self.on_predict_submit)

    def on_register_click(self, event):
        if self.register_frame is None:
            self.create_register_frame()
        self.notebook.select(self.register_frame)

    def create_register_frame(self):
        self.register_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.register_frame, text="Registro")
        self.create_label(self.register_frame, "Registro", 20)
        self.create_entry(self.register_frame, "Usuario: (*)", False, 'register_user_entry')
        self.create_entry(self.register_frame, "Correo: (*)", False, 'register_email_entry')
        self.create_entry(self.register_frame, "Contraseña: (*)", True, 'register_password_entry')
        self.create_entry(self.register_frame, "Edad: (*)", False, 'age_entry')
        self.authorize_label_var = tk.StringVar()

       

        self.authorize_fitbit_button = self.create_button(self.register_frame, "Paso 1: Autorizar con Fitbit", self.authorize_with_fitbit, label_var=self.authorize_label_var)
        self.register_button = self.create_button(self.register_frame, "Paso 2: Registrarse", self.on_register_submit, state="disabled")

    def on_register_submit(self):
        user = self.register_user_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        age = self.age_entry.get()

        user_id = self.controller.fitbitAPI.user_id
        access_token = self.controller.fitbitAPI.access_token
        refresh_token = self.controller.fitbitAPI.refresh_token
        expires_in = self.controller.fitbitAPI.expires_in
        
        try:
            exito = self.controller.register(user, email, password, age, user_id, access_token, refresh_token, expires_in)
            if exito :
                 self.notebook.forget(self.register_frame)
                 self.notebook.select(self.login_frame)
            return exito
        
        except UserRegistrationError as e: 
            self.show_error_message(self.register_frame, e.getMessage())
            return False

    def on_predict_submit(self):
        if self.prediction_frame is None:
            self.create_prediction_frame()
        self.notebook.select(self.prediction_frame)

    def create_prediction_frame(self):
        self.prediction_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.prediction_frame, text="Predicción")
        self.create_prediction_info(5)
        self.create_button(self.prediction_frame, "Actualizar", self.update_status)

    def create_prediction_info(self, minutes):
        predictions = self.controller.predictions(minutes)
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(predictions)
        ax.set_xlabel('Minutos')
        ax.set_ylabel('HeartRate')
        canvas = FigureCanvasTkAgg(fig, master=self.prediction_frame)
        canvas.draw()
        canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def update_status(self):
        self.progress = ttk.Progressbar(self.status_frame, orient='horizontal', mode='determinate', variable=self.progress_var, maximum=100)
        self.progress.pack(pady=5)
        threading.Thread(target=self.run_update_status).start()

    def run_update_status(self):
        self.controller.updateApi_lastUpdate()
        self.update_progress(25) 
        last_update = datetime.now().strftime("%A, %d de %B de %Y a las %H:%M:%S")
        self.update_label.config(text=f"Última actualización: {last_update}")
        dates = self.get_dates_in_month(datetime.today().month)
        
        self.controller.fitbitAPI.getHeartRateData("1min", "00:00", "23:59", dates)
        self.update_progress(50) 
        self.controller.fitbitAPI.getCaloriesDistanceStepsData("1min", "00:00", "23:59", dates)
        self.update_progress(75) 

        self.controller.fitbitAPI.dataPreprocess()
        self.update_progress(100) 

        self.progress.pack_forget()  

    def update_progress(self, value):
        self.progress_var.set(value)
        self.update_idletasks()  

    def get_dates_in_month(self, month):
        today = datetime.today()
        first_day = datetime(today.year, month, 1)
        return [(first_day + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((today - first_day).days + 1)]

    def reauthorizationPopup(self):
        
        self.popup = tk.Toplevel(self)
        self.popup.title("Re-authorization Required")
        self.popup.geometry("400x150")

        message_label = tk.Label(self.popup, text="Your Fitbit access token has expired.\nPlease re-authorize to continue.")
        message_label.pack(pady=10)

        reauthorize_button = tk.Button(self.popup, text="Re-authorize", command=self.authorize_with_fitbit)
        reauthorize_button.pack(pady=10)
        
    def authorize_with_fitbit(self):
        
        user = self.register_user_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        age = self.age_entry.get()
      
        try :
          
            self.is_authorized = self.controller.authorize_with_fitbit(user, email, password, age)
            if self.popup :
                self.popup.destroy()
            if self.is_authorized:
                if self.authorize_fitbit_button:
                    self.authorize_fitbit_button.config(state="disabled")
                    self.authorize_label_var.set("✓")
                    self.register_button.config(state="normal")

        except UserRegistrationError as e: 
            
            self.show_error_message(self.register_frame, e.getMessage())
            return False      
    
      
      
           

        

       
