#imports
import time
import threading
import tkinter as tk
import pandas as pd
import matplotlib.dates as mdates

#Froms
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from app.controllers.Controller import Controller
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#Exceptions
from app.exceptions.ModifyError import ModifyError
from app.exceptions.GraphDataError import GraphDataError
from app.exceptions.UserLogInError import UserLogInError
from app.exceptions.PredictionError import PredictionError
from app.exceptions.SyncronizedError import SyncronizedError
from app.exceptions.UserRegistrationError import UserRegistrationError
from app.exceptions.UserTriesToPredictException import UserTriesToPredictException

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HeartPred'it")
        self.geometry("810x900")

        """Controller"""
        self.controller = Controller(self)

        """View Elements Status/Information"""
        self.is_authorized = False
        self.popup =None
        self.change_popup = None
        self.change_pass_popup = None
        self.update_label = None
        self.current_prediction_canvas = None
        self.current_data_canvas = None
        self.welcome_label = None
        
        
        """Icons"""
        self.menu_icon = None
        self.x_icon = None
        self.prediction_x_icon = None
        self.home_icon = None
        self.prediction_home_icon = None
        self.conf_icon = None
        self.settings_x_icon = None

        """Frames"""
        self.register_frame = None
        self.settings_frame = None
        self.userData_range_graph_frame = None
        self.prediction_frame = None
        self.data_frame = None
        self.status_frame = None
        self.app_frame = None
        self.login_frame = None
        self.dataUser_frame = None
        self.login_auth_frame = None


        """TimeDeltas"""
        self.time_deltas = {
                            "1 día": pd.Timedelta(days=1),
                            "1 semana": pd.Timedelta(weeks=1),
                            "1 mes": pd.DateOffset(months=1),
                            "1 hora": pd.Timedelta(hours=1),
                            "1 min": pd.Timedelta(minutes=1)
                           }
        
        """Main method to setup HeartPred'it UI"""
        self.setup_ui()

    """
        Creates all elements for HeartPred'it UI
    """
    def setup_ui(self):
        self.login_auth_frame = tk.Frame(self, bg="white")
        self.login_auth_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.notebook = ttk.Notebook(self.login_auth_frame)
        self.notebook.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.create_login_frame()
      

    """Create Login Frame where login elements such as email and password entries"""
    def create_login_frame(self):
        self.login_frame = tk.Frame(self.notebook, bg="#626CC2")
        self.notebook.add(self.login_frame, text="Inicio de Sesión")

        self.create_label(self.login_frame, "Inicio de Sesión", 20)
        self.create_entry(self.login_frame, "Correo: (*)", False, 'email_entry')
        self.create_entry(self.login_frame, "Contraseña: (*)", True, 'password_entry')

        self.create_register_link(self.login_frame)
        self.create_button(self.login_frame, "Inicio de Sesión", self.on_login_click)

    """Creates Label to insert into 'frame' frame with 'text' = text and 'size' = size """
    def create_label(self, frame, text, size, fg="white", bg="#626CC2"):
        label = tk.Label(frame, text=text, font=("Segoe UI", size), fg=fg, bg=bg)
        label.pack(pady=5, padx=20, fill=tk.X)
        return label

    """Creates Tkinter entry on 'frame' = frame with 'text' = text and show attribute """
    def create_entry(self, frame, text, show, attr_name):

        tk.Label(frame, text=text, pady=2, fg="white", bg="#626CC2", font=('Segoe UI', 14)).pack(anchor='w', padx=20, pady=(20, 0))
        entry = tk.Entry(frame, show="*" if show else "")
        entry.pack(fill=tk.X, padx=20, pady=5)
        setattr(self, attr_name, entry)
        return entry
    
    """
        Creates register link on 'frame' = frame

        Parameters:
        -frame (tk.Frame) : Frame where register link will be placed.

        Returns:
        register_label (tk.Label) : Register label so user can register on HeartPred'it App

    """
    def create_register_link(self, frame):
        register_container = tk.Frame(frame, bg="#626CC2")
        register_container .pack(pady=10, padx=20, fill=tk.X)
        register_label = tk.Label(register_container , text="¿No tienes cuenta? Regístrate aquí", fg="white", cursor="hand2", bg="#626CC2", font=('Segoe UI', 12))
        register_label.pack(pady=2)
        register_label.bind("<Button-1>", self.on_register_click)
        return register_label
    

    def findTokenInfo(self, email):
        user_data = self.mongo.find_one_data("usuarios", query={"correo": email})

        if user_data :
            fitbit_data = user_data.get("fitbit")

            access_token = fitbit_data["access_token"]
            refresh_token = fitbit_data["refresh_token"]
            expires_in = fitbit_data["expires_in"]
            user_id = fitbit_data["user_id"]


            if self.fitbitAPI.access_token_is_expired(access_token, expires_in):

                new_access_token, new_refresh_token, new_expires_in, user_id, reauth_required = self.fitbitAPI.refresh_access_token(refresh_token)
                if reauth_required:
                    return None, None, None, None, True

                
                self.storeTokenInfo(email, user_id, new_access_token, new_refresh_token, new_expires_in)
                return new_access_token, new_refresh_token, new_expires_in, user_id, False
            else:
                self.fitbitAPI.storeFibitInfo(access_token, refresh_token, expires_in,user_id)
                return access_token, refresh_token, expires_in, user_id, False

        
    """
        Creates a Tkinter Button into 'frame' = frame with 'text' = text executing when clicked 'command' method 

        Parameters:
        -frame (tK.Frame) : Frame where button will be placed.
        -text (str) : Texto describing Tk.Button.
        -command : Logic executed once clicked.


        Returns:
        - button (tK.Button) : Button that executes command when clicked.
    """
    def create_button(self, frame, text, command, state="normal", label_var=None):

        button_container = tk.Frame(frame, bg="#626CC2")
        button_container.pack(pady=2)
        button = tk.Button(button_container, text=text, fg="white", bg="#626CC2", state=state, command=lambda: self.button_click(command, label_var), font=("Segoe UI", 12))
        button.pack(side=tk.LEFT) 

        if label_var is not None:
            label = tk.Label(button_container, textvariable=label_var, fg="green", bg="#626CC2")
            label.pack(side=tk.LEFT, pady=5)
            
        return button
    
    """
        Executes command method related to a tKinter button

        Parameters:
        -command : Command executed when button clicked.
        label_var (str) : Label variable

    """
    def button_click(self, command, label_var):
        command()
        

    """"Logic that forgets all tabs in notebook"""
    def forgetTabs(self):
        
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
    """Command that implements login in"""
    def on_login_click(self):

        try:
            email = self.email_entry.get()
            password = self.password_entry.get()

            if self.controller.check_login(email, password):
                self.controller.getFitbitUserInfo(email)
                self.forgetTabs()
                self.create_app_notebook()
        except UserLogInError as e: 
            self.show_error_message(self.login_frame, e.getMessage())
            return False
        else:
            self.show_error_message(self.login_frame, "Ups...! Inicio de sesión fallido!")

    """
        Show into 'frame' = frame 'text' error

        Parameters:
        -frame (Tkinter Frame) : Frame where error message will be shown
        -text (str) : The text related to error.
    """
    def show_error_message(self, frame, text):
        error_label = tk.Label(frame, text=text, font=("Segoe UI", 15), fg="red")
        error_label.pack(pady=5, padx=20, fill=tk.X)
        self.after(3000, error_label.pack_forget)

    """
        Toggles menu.
    """
    def toggle_menu(self):
        if self.menu_frame.winfo_ismapped():
            self.menu_frame.pack_forget()
        else:
            self.menu_frame.pack(side=tk.TOP)

    """Creates App notebook"""
    def create_app_notebook(self):

        self.app_frame = tk.Frame(self.notebook, bg="#646CC2")
        self.notebook.add(self.app_frame, text="HeartPred'it")

        self.header_frame = tk.Frame(self.app_frame, bg="#626CC2")
    
        self.conf_icon = Image.open('app/assets/images/conf.png')
        self.conf_icon = self.conf_icon.resize((30, 30), Image.LANCZOS)  
        self.conf_icon = ImageTk.PhotoImage(self.conf_icon)

        self.conf_button = tk.Button(self.header_frame, image=self.conf_icon, bg="#626CC2", relief=tk.FLAT, command=self.settings)
        self.conf_button.image = self.conf_button 
        self.conf_button.pack(side=tk.RIGHT)

        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.menu_frame = tk.Frame(self.app_frame, bg="#626CC2")
      
        try:
            predict_link = tk.Label(self.menu_frame, text="Predecir", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
            predict_link.pack(pady=5)
            predict_link.bind("<Button-1>", lambda e:  self.on_predict_submit())

        except UserTriesToPredictException as e:
            self.show_error_message(self.app_frame, e.getMessage())
            return False

        syncronize_link = tk.Label(self.menu_frame, text="Sincronizar", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        syncronize_link.pack(pady=5)
        syncronize_link.bind("<Button-1>", lambda e: self.update_status())    

    
        show_user_data_link = tk.Label(self.menu_frame, text="Mostrar Datos", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        show_user_data_link.pack(pady=5)
        show_user_data_link.bind("<Button-1>", lambda e: self.selectUserData())


        self.create_welcome_label(self.app_frame)
        self.menu_frame.pack()

    """
        Create settings Notebook
    """
    def settings(self):
        if self.settings_frame :
            self.close_settings_tab()

        self.settings_frame = tk.Frame(self.notebook, bg="#646CC2")
        self.notebook.add(self.settings_frame, text="Configuración")

        self.header_frame = tk.Frame(self.settings_frame, bg="#626CC2")
       
        #icons
        self.settings_x_icon = Image.open('app/assets/images/x.png')
        self.settings_x_icon = self.settings_x_icon.resize((30, 30), Image.LANCZOS)  
        self.settings_x_icon = ImageTk.PhotoImage(self.settings_x_icon)

        self.settings_x_button = tk.Button(self.header_frame, image=self.settings_x_icon, bg="#626CC2", relief=tk.FLAT, command=self.close_settings_tab)
        self.settings_x_button.image = self.settings_x_button 
        self.settings_x_button.pack(side=tk.RIGHT)

        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.menu_frame = tk.Frame(self.settings_frame, bg="#626CC2")

        self.create_label(self.settings_frame, "Ajustes General:", 28)

        change_user_name_link = tk.Label(self.settings_frame, text="Cambiar nombre de usuario:", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        change_user_name_link.pack(pady=5)
        change_user_name_link.bind("<Button-1>", lambda e: self.changeUserName())


        change_pass_link = tk.Label(self.settings_frame, text="Cambiar contraseña", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        change_pass_link.pack(pady=5)
        change_pass_link.bind("<Button-1>", lambda e: self.changeUserPass())
      
        logout_link = tk.Label(self.settings_frame, text="Cerrar Sesión", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        logout_link.pack(pady=5)
        logout_link.bind("<Button-1>", lambda e: self.logout())

        delete_account_link = tk.Label(self.settings_frame, text="Eliminar Cuenta", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        delete_account_link.pack(pady=5)
        delete_account_link.bind("<Button-1>", lambda e: self.controller.deleteUserAccount())

        self.menu_frame.pack()
        self.notebook.select(self.settings_frame)

    """
        Logic for user to change password
    """
    def changeUserPass(self):
        self.change_pass_popup = tk.Toplevel(self.settings_frame)
        self.change_pass_popup.title("Cambiar contraseña de usuario")
        self.change_pass_popup.geometry("400x150")
        self.change_pass_popup.configure(bg="#626CC2")
 
        self.create_entry(self.change_pass_popup, "Nueva contraseña:", True, 'change_pass_user_entry')
        self.create_button(self.change_pass_popup,"Confirmar",self.changeUserPassConfirmed, state=None)
        
    """
        Logic for changing user username
    """
    def changeUserName(self):
         
        self.change_popup = tk.Toplevel(self.settings_frame)
        self.change_popup.title("Cambiar nombre de usuario")
        self.change_popup.geometry("400x150")
        self.change_popup.configure(bg="#626CC2")
 
        self.create_entry(self.change_popup, "Nuevo nombre de usuario:", False, 'change_user_entry')
        self.create_button(self.change_popup,"Confirmar",self.changeUserNameConfirmed, state=None)

    """
        Logic that changes user secret password to a new one.
    """
    def changeUserPassConfirmed(self):
        try:
            new_pass = self.change_pass_user_entry.get()
            self.controller.changeUserPass(new_pass)
            self.change_pass_popup.destroy()

        except UserRegistrationError as e:
             self.show_error_message(self.change_pass_popup, e.getMessage())
        except ModifyError as e:
            self.show_error_message(self.change_popup, e.getMessage())

    """
        Logic that changes user username to a new one.
    """
    def changeUserNameConfirmed(self):
        try:
            new_name = self.change_user_entry.get()
            self.controller.changeUserName(new_name)
            self.change_popup.destroy()
        except ModifyError as e:
            self.show_error_message(self.change_popup, e.getMessage())


    """Logic for user account delete"""
    def deleteUserAccount(self):
        """Logic for confirm user delete account"""
        def confirm_deletion():
            self.controller.deleteUserAccount()
            confirm_popup.destroy()

            self.forgetTabs()
            self.create_login_frame()


        confirm_popup = tk.Toplevel(self.app_frame)
        confirm_popup.title("Confirmar Eliminación")
        confirm_popup.geometry("300x150")
        confirm_popup.configure(bg="#626CC2")

        label = tk.Label(confirm_popup, text="¿Seguro que quieres eliminar la cuenta?\n¡Acción irrevocable!", bg="#626CC2", fg="white")
        label.pack(pady=20)

        button_frame = tk.Frame(confirm_popup, bg="#626CC2")
        button_frame.pack(pady=10)

        confirm_button = tk.Button(button_frame, text="Confirmar", fg="white", bg="#FF0000", command=confirm_deletion)
        confirm_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Atrás", fg="white", bg="#626CC2", command=confirm_popup.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10)
    
    """Logic for user logOut"""
    def logout(self):
        self.controller.logout()
        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)
        self.create_login_frame()

    """
        Creates Welcome label into 'frame' = frame

        Parameters:
        -frame (Tkinter Frame) : super.tk.Frame.
    """
    def create_welcome_label(self, frame):
        user_info = self.controller.user_info()
        if user_info:
            self.welcome_label = self.create_label(frame, f"¡Bienvenido, {user_info}!", 20)
            self.create_status_frame(frame)
    """
        Configures new text into welcome_label.
    """
    def config_welcome_label(self, new_name):   
        if self.welcome_label :    
            texto = f"¡Bienvenido, {new_name}!"
            self.welcome_label.configure(text=texto)
    
    """
        Creates status frame

        Parameters:
        -frame (Tkinter Frame) : super.tk.Frame 
    """
    def create_status_frame(self, frame):
        self.status_frame = tk.Frame(frame, bg="#626CC2")
        self.status_frame.pack(pady=10, padx=20, fill=tk.X)
        self.createLastUpdateLabel(self.status_frame, self.controller.last_update())

    """
        Creates last Update Label

        Parameters:
        -frame (tk.Frame) : Frame where label will be placed.
        -last_update : (str) : Last User update date with Fitbit.
    """
    def createLastUpdateLabel(self, frame, last_update):
        if last_update != "Nunca":
            self.update_label = self.create_label(frame, f"Última Sincronización con la pulsera: {last_update}", 14, fg="white", bg="#626CC2")
        else :
            self.update_label = self.create_label(frame, f"Última Sincronización con la pulsera: Nunca", 14, fg="white", bg="#626CC2")


    """Logic for register click event"""
    def on_register_click(self, event):
       
        self.create_register_frame()
        if self.register_frame:
            self.notebook.select(self.register_frame)
            
    """Logic for creation of register frame"""
    def create_register_frame(self):
        self.register_frame = tk.Frame(self.notebook, bg="#626CC2")
        self.notebook.add(self.register_frame, text="Registro")

        self.create_label(self.register_frame, "Registro", 20)
        self.create_entry(self.register_frame, "Usuario: (*)", False, 'register_user_entry')
        self.create_entry(self.register_frame, "Correo: (*)", False, 'register_email_entry')
        self.create_entry(self.register_frame, "Contraseña: (*)", True, 'register_password_entry')
        self.create_entry(self.register_frame, "Edad: (*)", False, 'age_entry')

        self.authorize_label_var = tk.StringVar()
        self.register_button = self.create_button(self.register_frame, "Registrarse y autorizar con Fitbit", self.on_register_submit, state=None)

    """Logic for user register submit"""
    def on_register_submit(self):

        user = self.register_user_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        age = self.age_entry.get()

        try:
            if self.controller.validateRegisterRequirements(user, email, password, age):
                self.authoritize(email)
                time.sleep(2)
                if self.controller.register(user, email, password, age) :
                    self.forgetTabs()
                    self.create_login_frame()
                return True
        except UserRegistrationError as e: 
            self.show_error_message(self.register_frame, e.getMessage())
            return False
        

    """Logic for user prediction"""
    def on_predict_submit(self):

        self.ult_act = self.controller.last_update()
        if self.ult_act != "Nunca":
            self.create_prediction_frame()
            self.notebook.select(self.prediction_frame)
        else:
           self.show_error_message(self.app_frame, "Sincroniza antes de intentar predecir. Estado de Sincronización: Nunca")

    """Logic that closes prediction Notebook"""
    def close_prediction_tab(self):
        self.notebook.forget(self.prediction_frame)
        self.prediction_frame = None

    """Logic that closes settings Notebook"""
    def close_settings_tab(self):
        self.notebook.forget(self.settings_frame)
        self.settings_frame = None
    
    """Logic that closes user data Notebook"""
    def close_user_data_tab(self):
        self.notebook.forget(self.dataUser_frame)
        self.dataUser_frame = None
    

    """Logic for prediction frame creation"""
    def create_prediction_frame(self):

        if self.prediction_frame :
            self.close_prediction_tab()

        self.prediction_frame = tk.Frame(self.notebook, bg="#626CC2")
        self.notebook.add(self.prediction_frame, text="Predicción")

        self.header_frame = tk.Frame(self.prediction_frame, bg="#626CC2")
        
        self.prediction_x_icon = Image.open('app/assets/images/x.png')
        self.prediction_x_icon = self.prediction_x_icon.resize((30, 30), Image.LANCZOS)  
        self.prediction_x_icon = ImageTk.PhotoImage(self.prediction_x_icon)

        self.prediction_x_button = tk.Button(self.header_frame, image=self.prediction_x_icon, bg="#626CC2", relief=tk.FLAT, command=self.close_prediction_tab)
        self.prediction_x_button.image = self.prediction_x_button 
        self.prediction_x_button.pack(side=tk.RIGHT)

        self.header_frame.pack(side=tk.TOP, fill=tk.X) 
        self.createLastUpdateLabel(self.prediction_frame , self.controller.last_update())
       
        self.comboBox = ttk.Combobox(self.prediction_frame, values=[5, 10, 15, 20, 25, 30])
        self.comboBox.set("Selecciona minutos")
        self.comboBox.pack(pady=20)

        sincronize_link = tk.Label(self.prediction_frame, text="Sincronizar", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        sincronize_link.pack(pady=5)
        sincronize_link.bind("<Button-1>", lambda e: self.update_status())

        predit_now_link = tk.Label(self.prediction_frame, text="Predecir Ahora", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        predit_now_link.pack(pady=5)
        predit_now_link.bind("<Button-1>", lambda e: self.predict())
        
        self.prediction_graph_frame = tk.Frame(self.prediction_frame, bg="#626CC2", padx=20, pady=20)
        self.prediction_graph_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    """
        Selects and creates user data notebook where user data is placed.
    """ 
    def selectUserData(self):

        self.dataUser_frame = tk.Frame(self.notebook, bg="#626CC2")
        self.notebook.add(self.dataUser_frame, text="Datos")
        self.notebook.select(self.dataUser_frame)

        self.header_frame = tk.Frame(self.dataUser_frame, bg="#626CC2")
       
        self.x_icon = Image.open('app/assets/images/x.png')
        self.x_icon = self.x_icon.resize((30, 30), Image.LANCZOS)  
        self.x_icon = ImageTk.PhotoImage(self.x_icon)

        self.x_button = tk.Button(self.header_frame, image=self.x_icon, bg="#626CC2", relief=tk.FLAT, command=self.close_user_data_tab)
        self.x_button.image = self.x_button 
        self.x_button.pack(side=tk.RIGHT)

        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.create_label(self.dataUser_frame, "Selecciona qué datos quieres visualizar", 14)

        
        self.dataComboBox = ttk.Combobox(self.dataUser_frame, values=["HeartRate","Calories","Distance","Steps"])
        self.dataComboBox.set("Selecciona")
        self.dataComboBox.pack(pady=20)

        self.data_radiobutton_frame = tk.Frame(self.dataUser_frame, bg="#626CC2")
        self.radio_option_selected = tk.StringVar()
        
        last_measurements_label = tk.Label(self.data_radiobutton_frame, text="Últimas mediciones:", fg="white", bg="#626CC2",font=("Segoe UI", 14))
        last_measurements_label.pack(side=tk.LEFT, pady=5)
        
        radio_options = ["Todos tus datos", "1 mes", "1 semana", "1 día", "1 hora", "1 min", "ahora"]
        #default value
        self.radio_option_selected.set("Todos tus datos")

        for option in radio_options:
            radioButton = tk.Radiobutton(self.data_radiobutton_frame, text=option, variable=self.radio_option_selected, value=option, bg="#626CC2",fg="black", selectcolor="white")
            radioButton.pack(side=tk.LEFT, padx=5)

        self.data_radiobutton_frame.pack(pady=5)
        
      
        show_user_data_link = tk.Label(self.dataUser_frame, text="Mostrar", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        show_user_data_link.pack(pady=5)
        show_user_data_link.bind("<Button-1>", lambda e: self.graphUserData())

        self.userData_graph_frame = tk.Frame(self.dataUser_frame, bg="#626CC2", padx=20, pady=20)
        self.userData_graph_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    """
        Creates a user data graph with selected data_frec and selected data_title ["HeartRate","Calories","Distance","Steps"]
    """    
    def graphUserData(self):
          
        try:
            data_frec = self.radio_option_selected.get() 
            data_title = self.dataComboBox.get()

            if data_title == "Selecciona":
                raise ValueError("¡Upss... Selecciona un opción válida entre las disponibles!")
    
            data = self.controller.userData(data_title,data_frec)
            ini = data['Time'].min()
            fin = data['Time'].max()

            try:
                self.graphData(data, data_frec, data_title, ini, fin)
            except GraphDataError as e:
                self.show_error_message(self.dataUser_frame, e.getMessage())

        except ValueError as e :
            self.show_error_message(self.dataUser_frame, e)

    """
        Graphs user data_title with data_frec frecuency.

        Parameters:
        -data_frec (str) : User selected Data show frecuency.
        -fin (Datetime): User last minute available of data (data_title) to be shown.
        -ini (Datetime): User first minute available of data (data_title) to be shown.

        Retunrs:
        - (booelan/GraphDataError) True if there is enough data to be graphed. GraphDataError otherwise.
    """    
    def checkIfEnoughData(self, data_frec, fin, ini):
        if data_frec in self.time_deltas:
           if data_frec == "1 mes":
                if ini + pd.DateOffset(months=1) > fin:
                    raise GraphDataError(f"No hay suficientes datos para mostrar con la frecuencia {data_frec}")
           else:
                if ini + self.time_deltas.get(data_frec) > fin:
                    raise GraphDataError(f"No hay suficientes datos para mostrar con la frecuencia {data_frec}")
        return True 
    
    """
        Graphs data_title User data with data_frec frecuency

        Parameters:
        -data (csv) : CSV that contains user data.
        -data_title (str) : requested user data.
        -data_frec (str) : User data frecuency.
        -ini (Datetime) : Datetime when user data_title begins.
        -fin (Datetime) : Datetime when user data_title ends.

    """
    def graphData(self, data, data_frec , data_title, ini, fin):
        
        if self.current_data_canvas:
            self.current_data_canvas.get_tk_widget().destroy()

        if self.userData_range_graph_frame:
            self.userData_range_graph_frame.destroy()
            self.userData_range_graph_frame = None
        
        if self.checkIfEnoughData(data_frec, fin, ini):
            fig = Figure(figsize=(8, 4))
            ax = fig.add_subplot(111)

            ax.plot(data['Time'], data[data_title], label=data_title, linestyle=':', marker='o',color='c')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  
            fig.autofmt_xdate() 

            ax.set_xlabel('Tiempo')
            ax.set_ylabel(data_title)
            ax.set_title(data_title)

            ax.legend()
            ax.grid(True)

            self.userData_range_graph_frame = tk.Frame(self.userData_graph_frame, bg="#626CC2")
            self.range_label = tk.Label(self.userData_range_graph_frame, text=f'Desde: {ini}      Hasta: {fin}', fg="white", bg="#626CC2",font=("Segoe UI", 14))
            self.range_label.pack(side=tk.LEFT, pady=5)
            self.userData_range_graph_frame.pack()

            canvas = FigureCanvasTkAgg(fig, master=self.userData_graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

            self.current_data_canvas = canvas

    """Logic for prediction with ML models"""
    def predict(self):
        try:
            steps = int(self.comboBox.get())
            threading.Thread(target=self.run_thread_prediction, args=(steps,)).start()
        except ValueError :
            self.show_error_message(self.prediction_frame, "¡Selecciona un número de minutos antes de predecir!")

    
    """
        Logic for predictions with ML models with selected number of minutes = steps

        Parameters:
        -steps (int) : Number of minutes to predict into the future.    
    """
    def run_thread_prediction(self, steps):
        try:
            self.prediction_popup = tk.Toplevel(self)
            self.prediction_popup.title("Prediciendo")
            self.prediction_popup.geometry("300x100")

            prediction_label = tk.Label(self.prediction_popup, text="Prediciendo...", font=("Segoe UI", 14))
            prediction_label.pack(pady=10)

            self.prediction_bar = ttk.Progressbar(self.prediction_popup, orient='horizontal', mode='determinate', length=200)
            self.prediction_bar.pack(pady=5)   

            self.update_prediction(2)
            self.update_prediction(30)

            self.controller.fitbitAPI.perfectDataForPrediction(steps)
            
            self.update_prediction(70)
            self.create_prediction_info(steps)
            self.update_prediction(100)

        except PredictionError as e :
            self.show_error_message(self.prediction_frame, e)
        finally:
            self.prediction_popup.destroy()

    """Logic for resulted prediction graph"""
    def create_prediction_info(self,steps):
        predictions = self.controller.predictions(steps)
        self.graphPredictions(predictions)
       
    """
        Creation of Predictions graph.

        Parameters:
        -datos_reales (csv) : CSV that contains lastest user HeartRate for every minute
        -predictions  (csv) : CSV that contains the predicted HeartRate for every minute.

    """
    def graphPredictions(self,  predictions):
        if self.current_prediction_canvas:
            self.current_prediction_canvas.get_tk_widget().destroy()
        
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        ax.plot(predictions.index, predictions, label='Predicciones', linestyle=':', marker='o')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  
        fig.autofmt_xdate() 

        ax.set_xlabel('Tiempo')
        ax.set_ylabel('HeartRate')
        ax.set_title('Predicciones')
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.prediction_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        self.current_prediction_canvas = canvas
    
    """Logic for updating/syncronized with latest user data"""
    def update_status(self):
        
        self.progress_popup = tk.Toplevel(self)
        self.progress_popup.title("Sincronizando...")
        self.progress_popup.geometry("300x100")

        progress_label = tk.Label(self.progress_popup, text="Sincronizando...", font=("Segoe UI", 14))
        progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.progress_popup, orient='horizontal', mode='determinate', length=200)
        self.progress_bar.pack(pady=5)

        threading.Thread(target=self.run_thread_update_status).start()

    """Logic for running on thread update/syncronize logic"""
    def run_thread_update_status(self):
        try:
            self.update_progress(2) 
            ultimaAct = self.controller.last_update()
            self.update_progress(25)

            if ultimaAct == "Nunca":
                dates = self.get_last_30_days()
            else:
                dates = self.get_dates_since_last_activity(ultimaAct)

            try:
                self.controller.fitbitAPI.getHeartRateData("1min", "00:00", "23:59", dates)
                self.update_progress(30) 
                self.controller.fitbitAPI.getCaloriesDistanceStepsData("1min", "00:00", "23:59", dates)
                self.update_progress(75)
                self.controller.fitbitAPI.dataPreprocess()
                ultimaAct = self.controller.lastFitBitDataUpdate()
                self.update_progress(100) 
                                
                self.controller.updateApiLastUpdate(ultimaAct)

                if self.update_label :
                    self.update_label.config(text=f"Última Sincronización con la pulsera: {ultimaAct}")

            except SyncronizedError as e:
                self.show_error_message(self.status_frame, e)
        finally:
            self.progress_popup.destroy()


    """
        Logic for updating syncronize progress bar

        Parameters:
        -value (int) : value from [0,100] indicating % of progress.
    """
    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.progress_popup.update_idletasks()
    
    """
        Logic for updating prediction progress bar

        Parameters:
        -value (int) : value from [0,100] indicating % of progress.
    """
    def update_prediction(self, value):
        self.prediction_bar['value'] = value
        self.prediction_popup.update_idletasks()


    """Logic for get last 30 day from actual date"""
    def get_last_30_days(self):
        today = datetime.today()
        start_date = today - timedelta(days=30)
        return [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(31)]
   
    """
        Logic for getting days passed since last updated/syncronize

        Parameters:
        -ult_act (Datetime) : Last user update/syncronized Datetime.

        Returns:
        - (list) : Containing the day since last update.
    """
    def get_dates_since_last_activity(self, ult_act):
        last_activity_date = ult_act  
        today = datetime.today()
        days_diff = (today - last_activity_date).days
        return [(last_activity_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days_diff + 1)]
    

    """Logic for creation of ReAuthoritazion PopUp with FitBit"""
    def reauthorizationPopup(self):
        
        self.popup = tk.Toplevel(self)
        self.popup.title("Re-authorization Requerida")
        self.popup.geometry("400x150")

        email = None

        message_label = tk.Label(self.popup, text="Tu token de autorización ha expirado.\nPor favor, re-autoriza con tu cuenta Fitbit.")
        message_label.pack(pady=10)
        reauthorize_button = tk.Button(self.popup, text="Re-autorizar", command=lambda: self.authoritize(email))
        reauthorize_button.pack(pady=10)
    
    """
        Logic for user authorize with FitBit

        Parameters:
        -user (str) : User name
        -email (str) : User mail
        -password (str) : User secret password
        -age (int) : User age
    """
    def authoritize(self,email):
        if self.controller.checkIfUserExistsByEmail(email) : 
            raise UserRegistrationError("El correo con el que intentas registrarte ya existe.")
        self.is_authorized = self.controller.authorize_with_fitbit()
        if self.popup :
            self.popup.destroy()
            