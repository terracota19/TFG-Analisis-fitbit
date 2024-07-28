#imports
import calendar
import threading
import statistics
import tkinter as tk
import pandas as pd
import matplotlib.dates as mdates

#Froms
from tkinter import ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from app.utils.sharedLock import mutex
from datetime import datetime, timedelta
from app.utils.IconsEnum import IconsEnum
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
        self.geometry("810x870")

        """Controller"""
        self.controller = Controller(self)

        """View Elements Status/Information"""
        self.popup = None
        self.update_label = None
        self.current_prediction_canvas = None
        self.current_data_canvas = None
        self.welcome_label = None
        self.prediction_data_title = None
        self.data_pred_title = None
        self.progress_popup = None
        self.prediction_popup = None
        self.filter_popup = None
        self.use_time_checkbox_var = tk.BooleanVar()
        self.change_password_frame = None
        self.change_username_frame = None

        self.from_hour_spinbox = None
        self.from_minute_spinbox = None
        self.to_hour_spinbox = None
        self.to_minute_spinbox = None
        self.purposeComboBox = None

        """Mutex"""
        self.mutex = threading.Lock()

        """Calendar"""
        self.from_date = None
        self.to_date = None
        self.from_hour_var = tk.StringVar(value="00")
        self.from_minute_var = tk.StringVar(value="00")
        self.to_hour_var = tk.StringVar(value="23")
        self.to_minute_var = tk.StringVar(value="59")
        self.to_datetime = None
        self.from_date = None

        """Icons"""
        self.menu_icon = None
        self.x_icon = None
        self.prediction_x_icon = None
        self.home_icon = None
        self.prediction_home_icon = None
        self.conf_icon = None
        self.settings_x_icon = None
        self.register_x_icon = None
        self.smiley_icon = None
        self.sad_icon = None

        """Frames"""
        self.register_frame = None
        self.settings_frame = None
        self.userData_range_graph_frame = None
        self.predict_range_graph_frame = None
        self.prediction_frame = None
        self.status_frame = None
        self.app_frame = None
        self.login_frame = None
        self.dataUser_frame = None
        self.login_auth_frame = None
        self.prediction_comboBox_frame = None
        self.prediction_graph_frame = None

        self.diasMes = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
    
        """TimeDeltas"""
        self.time_deltas = {
                            "1 día": pd.Timedelta(days=1),
                            "1 semana": pd.Timedelta(weeks=1),
                            "1 mes": pd.Timedelta(days=self.diasMes),
                            "1 hora": pd.Timedelta(hours=1),
                            "1 min": pd.Timedelta(minutes=1)
                           }
        
        """Main method to setup HeartPred'it UI"""
        self.setup_ui()

    """
        Creates all elements for HeartPred'it UI
    """
    def setup_ui(self):
        self.login_auth_frame = tk.Frame(self)
        self.login_auth_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.notebook = ttk.Notebook(self.login_auth_frame)
        self.notebook.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.create_login_frame()
    
 
    """Create Login Frame where login elements such as email and password entries"""
    def create_login_frame(self):
        self.login_frame = tk.Frame(self.notebook, bg="#626CC2")
        self.notebook.add(self.login_frame, text="Inicio de Sesión")

        self.create_label(self.login_frame, "Inicio de Sesión", 22)
        self.create_entry(self.login_frame, "Correo: (*)", False, 'email_entry',"<KeyPress-Return>", "on_login_click")
        self.create_entry(self.login_frame, "Contraseña: (*)", True, 'password_entry', "<KeyPress-Return>", "on_login_click")

        self.create_register_link(self.login_frame)

        self.login_label = tk.Label(self.login_frame, text= "Iniciar sesión", font=("Segoe UI", 14),
                                         fg = "white", bg="#626CC2", cursor="hand2")
        self.login_label.pack(pady = 13)
        self.login_label.bind("<KeyPress-Return>", lambda e: self.on_login_click() )
        self.login_label.bind("<Button-1>", lambda e: self.on_login_click() )


    """Creates Label to insert into 'frame' frame with 'text' = text and 'size' = size """
    def create_label(self, frame, text, size, fg="white", bg="#626CC2"):
        label = tk.Label(frame, text=text, font=("Segoe UI", size), fg=fg, bg=bg)
        label.pack(pady=5, padx=20, fill=tk.X)
        return label

    """Creates Tkinter entry on 'frame' = frame with 'text' = text and show attribute """
    def create_entry(self, frame, text, show, attr_name, event = None, function=None):

        tk.Label(frame, text=text, pady=2, fg="white", bg="#626CC2", font=('Segoe UI', 14)).pack(anchor='w', padx=20, pady=(10, 0))
        entry = tk.Entry(frame, show="*" if show else "")
        entry.pack(fill=tk.X, padx=20, pady=5)
        if event and function:
            func_ref = getattr(self, function)
            entry.bind(event, func_ref)

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
    
    """
        Find User Fitbit info

        Parameters:
        -email (str) : Unique user email. 
    """
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
    def create_button(self, frame, text, command, state="normal", label_var = None, font_size = 12):

        button_container = tk.Frame(frame, bg="#626CC2")
        button_container.pack(pady=2)
        button = tk.Button(button_container, text=text, fg="black", bg="white", state=state, command=lambda: self.button_click(command, label_var), font=("Segoe UI", font_size))
        button.pack(side=tk.LEFT, pady = 10) 

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
    def on_login_click(self, event=None):

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
            self.show_error_message(self.login_frame, "¡Inicio de sesión fallido!")

    """
        Show into 'frame' = frame 'text' error

        Parameters:
        -frame (Tkinter Frame) : Frame where error message will be shown
        -text (str) : The text related to error.
    """
    def show_error_message(self, frame, text, mseconds= None):
        error_label = tk.Label(frame, text=text, font=("Segoe UI", 15), fg="red")
        error_label.pack(pady=5, padx=20, fill=tk.X)
        if mseconds is not None :
            self.after(mseconds, error_label.pack_forget)
        else :
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

        "Icon"
        self.herramienta_icon = Image.open('app/assets/images/herramienta.png')
        self.herramienta_icon = self.herramienta_icon.resize((30, 30), Image.LANCZOS)  
        self.herramienta_icon = ImageTk.PhotoImage(self.herramienta_icon)

       
        self.general = tk.Label(self.settings_frame, text="Ajustes General:", font=("Segoe UI", 28), fg="white", bg="#626CC2", image=self.herramienta_icon, compound="right")
        self.general.image = self.saludo_icon  
        self.general.pack()
    

        change_user_name_link = tk.Label(self.settings_frame, text="Cambiar nombre de usuario:", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        change_user_name_link.pack(pady=5)
        change_user_name_link.bind("<Button-1>", lambda e: self.changeUserName())


        change_pass_link = tk.Label(self.settings_frame, text="Cambiar contraseña", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        change_pass_link.pack(pady=5)
        change_pass_link.bind("<Button-1>", lambda e: self.changeUserPass())

        change_porpuse_link = tk.Label(self.settings_frame, text="Cambiar propósito", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        change_porpuse_link.pack(pady=5)
        change_porpuse_link.bind("<Button-1>", lambda e : self.createPorpouseFrame())


        logout_link = tk.Label(self.settings_frame, text="Cerrar Sesión", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        logout_link.pack(pady=5)
        logout_link.bind("<Button-1>", lambda e: self.logout())

        delete_account_link = tk.Label(self.settings_frame, text="Eliminar Cuenta", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        delete_account_link.pack(pady=5)
        delete_account_link.bind("<Button-1>", lambda e: self.deleteUserAccount())

        self.menu_frame.pack()
        self.notebook.select(self.settings_frame)
    
    """
        Logic for user username change
    """
    def changeUserPorpouse(self, event = None):
        new_porpuse = self.purposeComboBox.get()
        self.destroyChangesFrames()
        return self.controller.changeUserPorpouse(new_porpuse)
    
    """
        Destroys all user possible changes frames
    """
    def destroyChangesFrames(self):
        if self.change_password_frame is not None :
            self.change_password_frame.destroy()

        if self.change_username_frame is not None:
             self.change_username_frame.destroy() 

        if self.change_porpouse_frame is not None:
            self.change_porpouse_frame.destroy() 

    """
        Logic for user to change password
    """
    def changeUserPass(self):
        
        self.change_password_frame = tk.Frame(self.settings_frame, bg="#626CC2")
 
        self.create_entry(self.change_password_frame, "Nueva contraseña:", True, 'change_pass_user_entry', "<KeyPress-Return>", "changeUserPassConfirmed")
       
        self.confirm_pass_label = tk.Label(self.change_password_frame, text= "Confirmar", font=("Segoe UI", 14),
                                         fg = "white", bg="#626CC2", cursor="hand2")
        self.confirm_pass_label.pack(pady = 13)
        self.confirm_pass_label.bind("<KeyPress-Return>", lambda e: self.changeUserPassConfirmed() )
        self.confirm_pass_label.bind("<Button-1>", lambda e: self.changeUserPassConfirmed() )
        self.change_password_frame.pack(pady=10, fill=tk.X)
        
    """
        Logic for changing user username
    """
    def changeUserName(self):
        
        self.change_username_frame = tk.Frame(self.settings_frame, bg="#626CC2")
    
        self.create_entry(self.change_username_frame, "Nuevo nombre de usuario:", False, 'change_user_entry', "<KeyPress-Return>", "changeUserNameConfirmed")
       
        self.confirm_username_label = tk.Label(self.change_username_frame, text= "Confirmar", font=("Segoe UI", 14),
                                         fg = "white", bg="#626CC2", cursor="hand2")
        self.confirm_username_label.pack(pady = 13)
        self.confirm_username_label.bind("<KeyPress-Return>", lambda e: self.changeUserNameConfirmed() )
        self.confirm_username_label.bind("<Button-1>", lambda e: self.changeUserNameConfirmed() )
        
        self.change_username_frame.pack(pady=10, fill=tk.X)

    """
        Logic for Porpouse user change creation
    """
    def createPorpouseFrame(self):
          
        self.change_porpouse_frame = tk.Frame(self.settings_frame, bg="#626CC2")
    
        self.purposeComboBox = ttk.Combobox(self.change_porpouse_frame, width=40,values=["Ninguno", "Mejorar salud general", "Quema de grasa", "Mejorar resistencia cardiovascular", "Mejorar la velocidad y potencia", "Mejorar máximo rendimiento"])
        self.purposeComboBox.pack(padx=20)
        self.purposeComboBox.set("Ninguno")

        self.confirm_porpuse_label = tk.Label(self.change_porpouse_frame, text= "Confirmar", font=("Segoe UI", 14),
                                         fg = "white", bg="#626CC2", cursor="hand2")
        self.confirm_porpuse_label.pack(pady = 13)
        self.confirm_porpuse_label.bind("<Button-1>", lambda e: self.changeUserPorpouse() )

        self.change_porpouse_frame.pack(pady=10, fill=tk.X)

    """
        Logic that changes user secret password to a new one.
    """
    def changeUserPassConfirmed(self, event=None):
        try:
            new_pass = self.change_pass_user_entry.get()
            self.controller.changeUserPass(new_pass)

            self.destroyChangesFrames()
           
        except UserRegistrationError as e:
             self.show_error_message(self.change_password_frame, e.getMessage())
        except ModifyError as e:
            self.show_error_message(self.change_password_frame, e.getMessage())

    """
        Logic that changes user username to a new one.
    """
    def changeUserNameConfirmed(self, event = None):
        try:
            new_name = self.change_user_entry.get()
            self.controller.changeUserName(new_name)

            self.destroyChangesFrames()
        
        except ModifyError as e:
            self.show_error_message(self.change_username_frame, e.getMessage())


    """Logic for user account delete"""
    def deleteUserAccount(self):
        """Logic for confirm user delete account"""
        def confirm_deletion():
            self.controller.deleteUserAccount()

            confirm_popup.destroy()
            self.forgetTabs()
            self.deleteAllFrames()
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
        
        self.deleteAllFrames()

        self.create_login_frame()

    """
        Logic for deleting all posible frames in app
    """
    def deleteAllFrames(self):
        self.settings_frame = None
        self.register_frane = None
        self.login_frame = None
        self.register_frame = None
        self.app_frame = None
        self.dataUser_frame = None

    """
        Creates Welcome label into 'frame' = frame

        Parameters:
        -frame (Tkinter Frame) : super.tk.Frame.
    """
    def create_welcome_label(self, frame):
        "Icon"
        self.saludo_icon = Image.open('app/assets/images/saludo.png')
        self.saludo_icon = self.saludo_icon.resize((30, 30), Image.LANCZOS)  
        self.saludo_icon = ImageTk.PhotoImage(self.saludo_icon)

        user_info = self.controller.user_info()
        if user_info:
            self.welcome_label = tk.Label(frame, text=f"¡Bienvenido, {user_info}!", font=("Segoe UI", 20), fg="white", bg="#626CC2", image=self.saludo_icon, compound="right")
            self.welcome_label.image = self.saludo_icon  
            self.welcome_label.pack()
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

        "Icon"
        self.band_icon = Image.open('app/assets/images/band.png')
        self.band_icon = self.band_icon.resize((30, 30), Image.LANCZOS)  
        self.band_icon = ImageTk.PhotoImage(self.band_icon)

        if last_update != "Nunca":
            text = f"Última Sincronización con la pulsera: {last_update}"
        else:
            text = f"Última Sincronización con la pulsera: Nunca"
        
        self.update_label = tk.Label(frame, text=text, font=("Segoe UI", 14), fg="black", bg="white", image=self.band_icon, compound="left")
        self.update_label.image = self.band_icon  
        self.update_label.pack()

    """
        Logic that creates register frame, so user can register
    """
    def create_register_frame(self):
        if self.register_frame :
            self.close_register_tab()

        self.register_frame = tk.Frame(self.notebook, bg="#646CC2")
        self.notebook.add(self.register_frame, text="Registro")

        self.header_frame = tk.Frame(self.register_frame, bg="#626CC2")
    
        self.register_x_icon = Image.open('app/assets/images/x.png')
        self.register_x_icon = self.register_x_icon.resize((30, 30), Image.LANCZOS)  
        self.register_x_icon = ImageTk.PhotoImage(self.register_x_icon)

        self.register_x_button = tk.Button(self.header_frame, image=self.register_x_icon, bg="#626CC2", relief=tk.FLAT, command=self.close_register_tab)
        self.register_x_button.image = self.register_x_button 
        self.register_x_button.pack(side=tk.RIGHT)

        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        try:
            self.create_label(self.register_frame, "Registrarse", 22)

            self.create_entry(self.register_frame, "Usuario: (*)", False, 'user_entry', "<KeyPress-Return>", "on_register_submit")
            self.create_entry(self.register_frame, "Correo: (*)", False, 'email_entry', "<KeyPress-Return>", "on_register_submit")
            self.create_entry(self.register_frame, "Contraseña: (*)", True, 'password_entry', "<KeyPress-Return>", "on_register_submit")
            self.create_entry(self.register_frame, "Edad: (*)", False, 'age_entry', "<KeyPress-Return>", "on_register_submit")

                   
            self.popurse_label = tk.Label(self.register_frame, text="Propósito", font=("Segoe UI", 14), fg="white", bg="#626CC2")
            self.popurse_label.pack( padx=20)

            self.purposeComboBox = ttk.Combobox(self.register_frame, width=40,values=["Ninguno", "Mejorar salud general", "Quema de grasa", "Mejorar resistencia cardiovascular", "Mejorar la velocidad y potencia", "Mejorar máximo rendimiento"])
            self.purposeComboBox.set("Ninguno")
            self.purposeComboBox.pack(padx=20)
        
            # Icon
            self.link_icon = Image.open('app/assets/images/link.png')
            self.link_icon = self.link_icon.resize((15, 15), Image.LANCZOS)  
            self.link_icon = ImageTk.PhotoImage(self.link_icon)


            self.link_label = tk.Label(self.register_frame, text="Registrarse y autorizar con Fitbit", font=("Segoe UI", 14),
                                         fg = "white", bg="#626CC2",  image=self.link_icon, compound="right", cursor="hand2")
            self.link_label.image = self.link_icon
            self.link_label.pack(pady = 11)
            self.link_label.bind("<KeyPress-Return>", lambda e: self.on_register_submit() )
            self.link_label.bind("<Button-1>", lambda e: self.on_register_submit() )

        except UserRegistrationError as e:
            self.show_error_message(self.register_frame, e.getMessage())
    
  
    """
        Logic to register a new user
    """
    def on_register_submit(self, event=None):
        try:
            usuario = self.user_entry.get()
            email = self.email_entry.get()
            password = self.password_entry.get()
            age = self.age_entry.get()
            porpuse = self.purposeComboBox.get()
     
            if self.controller.validateRegisterRequirements(usuario, email, password, age):
                self.authoritize(email)
                with mutex:
                    if self.controller.register(usuario, email, password, age, porpuse):
                        self.close_register_tab()
                        self.notebook.select(self.login_frame)
                        self.show_error_message(self.login_frame, "¡Se ha creado correctamente el usuario!", 10000)

        except UserRegistrationError as e:
            self.show_error_message(self.register_frame, e.getMessage())

    """Logic for register click event"""
    def on_register_click(self, event = None):       
        self.create_register_frame()
        if self.register_frame:
            self.notebook.select(self.register_frame)
        

    """Logic for creation of register frame"""
    def create_prediction_frame(self):
        if self.prediction_frame:
            self.close_prediction_tab()

        self.prediction_frame = tk.Frame(self.notebook, bg="#646CC2")
        self.notebook.add(self.prediction_frame, text="Predecir")

        self.header_frame = tk.Frame(self.prediction_frame, bg="#626CC2")

        self.x_icon = Image.open('app/assets/images/x.png')
        self.x_icon = self.x_icon.resize((30, 30), Image.LANCZOS)  
        self.x_icon = ImageTk.PhotoImage(self.x_icon)

        self.x_button = tk.Button(self.header_frame, image=self.x_icon, bg="#626CC2", relief=tk.FLAT, command=self.close_prediction_tab)
        self.x_button.image = self.x_icon 
        self.x_button.pack(side=tk.RIGHT)

        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.prediction_comboBox_frame = tk.Frame(self.prediction_frame, bg="#626CC2")
     
        self.create_label(self.prediction_comboBox_frame, "Selecciona qué datos quieres visualizar y los minutos a predecir", 14)
        self.comboBox_subframe = tk.Frame(self.prediction_comboBox_frame, bg="#626CC2")
        self.comboBox_subframe.pack(side=tk.TOP, pady=20)

        self.dataPredComboBox = ttk.Combobox(self.comboBox_subframe, values=["HeartRate", "Calories", "Distance", "Steps"])
        self.dataPredComboBox.set("Selecciona")
        self.dataPredComboBox.pack(side=tk.LEFT, padx=10)

        self.spinBox = tk.Spinbox(self.comboBox_subframe, from_=5, to=30, increment=5, wrap=True)
        self.spinBox.pack(side=tk.LEFT, padx=10)

        self.prediction_comboBox_frame.pack(fill=tk.X) 

        predict_link = tk.Label(self.prediction_frame, text="Predecir", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        predict_link.pack(pady=5)
        predict_link.bind("<Button-1>", lambda e: self.predict())

        sincronize_link = tk.Label(self.prediction_frame, text="Sincronizar", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        sincronize_link.pack(pady=5)
        sincronize_link.bind("<Button-1>", lambda e: self.update_status())

        self.prediction_graph_frame = tk.Frame(self.prediction_frame, bg="#626CC2")
        self.prediction_graph_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)


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

    def close_register_tab(self):
        self.notebook.forget(self.register_frame)
        self.register_frame = None

    """Logic that closes settings Notebook"""
    def close_settings_tab(self):

        self.notebook.forget(self.settings_frame)
        self.settings_frame = None
    
    """Logic that closes user data Notebook"""
    def close_user_data_tab(self):
        self.notebook.forget(self.dataUser_frame)
        self.dataUser_frame = None
    

    """Logic for prediction frame creation"""
    def selectUserData(self):
        if self.dataUser_frame:
            self.close_user_data_tab()

        self.dataUser_frame = tk.Frame(self.notebook, bg="#626CC2")
        self.notebook.add(self.dataUser_frame, text="Datos")
        self.notebook.select(self.dataUser_frame)

        self.header_frame = tk.Frame(self.dataUser_frame, bg="#626CC2")

        self.x_icon = Image.open('app/assets/images/x.png')
        self.x_icon = self.x_icon.resize((30, 30), Image.LANCZOS)  
        self.x_icon = ImageTk.PhotoImage(self.x_icon)

        self.x_button = tk.Button(self.header_frame, image=self.x_icon, bg="#626CC2", relief=tk.FLAT, command=self.close_user_data_tab)
        self.x_button.image = self.x_icon 
        self.x_button.pack(side=tk.RIGHT)

        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(self.dataUser_frame, text="Selecciona qué datos quieres visualizar", font=("Segoe UI", 14), fg="white", bg="#626CC2").pack(pady=10)

        combo_frame = tk.Frame(self.dataUser_frame, bg="#626CC2")
        combo_frame.pack(pady=20)

        self.dataComboBox = ttk.Combobox(combo_frame, values=["HeartRate", "Calories", "Distance", "Steps"])
        self.dataComboBox.set("Tipo de dato")
        self.dataComboBox.pack(side=tk.LEFT, padx=5)

        self.timeRangeComboBox = ttk.Combobox(combo_frame, values=["Todos tus datos", "1 mes", "1 semana", "1 día", "1 hora", "1 min"])
        self.timeRangeComboBox.set("Últimos datos")
        self.timeRangeComboBox.pack(side=tk.LEFT, padx=5)

        self.filters_frame = tk.Frame(self.dataUser_frame, bg="#626CC2")
        self.filters_frame.pack(pady=10)

        self.filters_grid_frame = tk.Frame(self.filters_frame, bg="#626CC2")
        self.filters_grid_frame.pack()

        self.mostrar_frame = tk.Frame(self.dataUser_frame, bg="#626CC2")

        show_user_data_link = tk.Label(self.mostrar_frame, text="Mostrar", fg="white", bg="#626CC2", cursor="hand2", font=('Segoe UI', 12))
        show_user_data_link.pack(side=tk.LEFT, pady=5)
        show_user_data_link.bind("<Button-1>", lambda e: self.graphUserData())
        
        self.filter_icon = Image.open('app/assets/images/filter.png')
        self.filter_icon = self.filter_icon.resize((30, 30), Image.LANCZOS)
        self.filter_icon = ImageTk.PhotoImage(self.filter_icon)

        self.filter_button = tk.Button(self.mostrar_frame, image=self.filter_icon, bg="#626CC2", relief=tk.FLAT, command=self.showFilterOptions)
        self.filter_button.image = self.filter_icon
        self.filter_button.pack(side=tk.LEFT)

        self.mostrar_frame.pack()

        self.userData_graph_frame = tk.Frame(self.dataUser_frame, bg="#626CC2", padx=20, pady=20)
        self.userData_graph_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    """
        Logic for showing Filter options
    """   
    def showFilterOptions(self):

        self.filter_popup = tk.Toplevel(self, bg="white")
        self.filter_popup.title("Filtro por fecha avanzado")
        self.filter_popup.geometry("410x170")

        from_frame = tk.Frame(self.filter_popup, bg="white")
        from_frame.pack(fill=tk.X, pady=5)
        tk.Label(from_frame, text="Desde:", font=("Segoe UI", 11), fg="black", bg="white").pack(side=tk.LEFT, padx=5)
        self.from_date = DateEntry(from_frame)
        self.from_date.pack(side=tk.LEFT)

        to_frame = tk.Frame(self.filter_popup, bg="white")
        to_frame.pack(fill=tk.X, pady=5)
        tk.Label(to_frame, text="Hasta:", font=("Segoe UI", 11), fg="black", bg="white").pack(side=tk.LEFT, padx=5)
        self.to_date = DateEntry(to_frame)
        self.to_date.pack(side=tk.LEFT)

        self.use_time_checkbox = tk.Checkbutton(self.filter_popup, text="Hora/Minuto", 
                                                font=("Segoe UI", 11), fg="black", bg="white",
                                                variable=self.use_time_checkbox_var, command=self.toggle_time_spinboxes)
        self.use_time_checkbox.pack(pady=5, anchor=tk.W, padx=5)

        self.select_frame = tk.Frame(self.filter_popup, bg="white")
        self.select_date_range = tk.Label(self.select_frame, text="Filtrar", fg="black", bg="white", cursor="hand2", font=('Segoe UI', 12))
        self.select_date_range.pack(pady=5)
        self.select_date_range.bind("<Button-1>", lambda e: self.selectDateRange())
        self.select_frame.pack(fill=tk.X, pady=10)

        self.create_hour_minute_spinboxes()

    """
        Logic for toogle hour/minute range in data selection spinboxes
    """
    def toggle_time_spinboxes(self):
        if self.use_time_checkbox_var.get():
            self.show_hour_minute_spinboxes()
        else:
            self.hide_hour_minute_spinboxes()

    """
        Logic for creating hour/minute spinboxes
    """
    def create_hour_minute_spinboxes(self):

        self.from_hour_spinbox = tk.Spinbox(self.from_date.master, from_=0, to=23, width=5, format="%02.0f", wrap=True, textvariable=self.from_hour_var)
        self.from_minute_spinbox = tk.Spinbox(self.from_date.master, from_=0, to=59, width=5, format="%02.0f", wrap=True, textvariable=self.from_minute_var)
        
        self.to_hour_spinbox = tk.Spinbox(self.to_date.master, from_=0, to=23, width=5, format="%02.0f", wrap=True, textvariable=self.to_hour_var)
        self.to_minute_spinbox = tk.Spinbox(self.to_date.master, from_=0, to=59, width=5, format="%02.0f", wrap=True, textvariable=self.to_minute_var)

    """
        Logic for showing hour/minute spinboxes
    """
    def show_hour_minute_spinboxes(self):

        self.from_hour_spinbox.pack(side=tk.LEFT, padx=5)
        self.from_minute_spinbox.pack(side=tk.LEFT, padx=5)
        
        self.to_hour_spinbox.pack(side=tk.LEFT, padx=5)
        self.to_minute_spinbox.pack(side=tk.LEFT, padx=5)

    """
        Logic for hiding hour/minute spinboxes
    """
    def hide_hour_minute_spinboxes(self):

        self.from_hour_spinbox.pack_forget()
        self.from_minute_spinbox.pack_forget()
        self.to_hour_spinbox.pack_forget()
        self.to_minute_spinbox.pack_forget()

    """
        Logic for selecting date range in show notebook
    """
    def selectDateRange(self):

        from_date = self.from_date.get_date()  
        
        if self.use_time_checkbox_var.get():
            self.from_hour = int(self.from_hour_spinbox.get())  
            self.from_minute = int(self.from_minute_spinbox.get())

            self.to_hour = int(self.to_hour_spinbox.get())  
            self.to_minute = int(self.to_minute_spinbox.get())  
            
        else :
           self.resetSpinBoxes()
      
        self.from_datetime = datetime.combine(from_date, datetime.min.time())
        self.from_datetime = self.from_datetime.replace(hour=self.from_hour, minute=self.from_minute)

        to_date = self.to_date.get_date()  
           
        self.to_datetime = datetime.combine(to_date, datetime.min.time())
        self.to_datetime = self.to_datetime.replace(hour=self.to_hour, minute=self.to_minute)

        try:
            data_title = self.dataComboBox.get()
            self.graphDataByRange(self.controller.userDataByRange(data_title, self.from_datetime, self.to_datetime),
                                data_title, self.from_datetime, self.to_datetime)

        except Exception as e:
            print(e)
            self.show_error_message(self.dataUser_frame, e)

        self.filter_popup.destroy()  
        
    """
        Resets Spinboxes
    """
    def resetSpinBoxes(self):

            self.from_hour= int(0)
            self.from_minute = int(0)
            self.to_hour = int(23)  
            self.to_minute = int(59)  

    """
        Creates a user data graph with selected data_frec and selected data_title ["HeartRate","Calories","Distance","Steps"]
    """    
    def graphUserData(self):
          
        try:
            
            data_frec = self.timeRangeComboBox.get() 
            data_title = self.dataComboBox.get()

            if data_title == "Tipo de dato":
                raise ValueError("¡Selecciona un opción válida entre las disponibles!")
            
            if data_frec == "Últimos datos":
                 raise ValueError(f"¡Opción {data_frec} no válida!")
            
            data = self.controller.userData(data_title, data_frec)
            ini = data['Time'].min()
            fin = data['Time'].max()
            dif = fin - ini
            try:
                self.graphData(data, data_frec, data_title, ini, fin, dif)
            except GraphDataError as e:
                self.show_error_message(self.dataUser_frame, e.getMessage())

        except ValueError as e :
            self.show_error_message(self.dataUser_frame, e)
        except FileNotFoundError as e:
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
    def checkIfEnoughData(self, data_frec, ini, fin):
        if data_frec in self.time_deltas:
                if ini + self.time_deltas.get(data_frec) > fin:
                    raise GraphDataError(f"No hay suficientes datos para mostrar con la frecuencia {data_frec}")
        return True 
    
    """
        Graphs data_title User data with data_frec frecuency

        Parameters:
        -data (csv) : CSV that contains user data.
        -data_title (str) : requested user data.
        -data_frec (str) : User data frecuency.
        -from_datetime  (Datetime) : Datetime when user data_title begins.
        -to_datetime (Datetime) : Datetime when user data_title ends.

    """
    def graphDataByRange(self, data, data_title, from_datetime, to_datetime):
    
        if self.current_data_canvas:
            self.current_data_canvas.get_tk_widget().destroy()

        if from_datetime is None or to_datetime is None:
            raise GraphDataError("Selecciona correctamente las fechas")
        
        if self.userData_range_graph_frame:
            self.userData_range_graph_frame.destroy()
            self.userData_range_graph_frame = None
        
        if not (from_datetime < to_datetime):
            raise GraphDataError(f"Error: La fecha {from_datetime} debe ser anterior a la fecha {to_datetime}.")
    
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        dif = to_datetime - from_datetime

        data['Time'] = pd.to_datetime(data['Time'])
        data.set_index('Time', inplace=True)

        if dif.days >= 30:
            data = data.resample('M').mean()

        ax.plot(data.index, data[data_title], label=data_title, linestyle='-', color='c', linewidth=0.8)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m %H:%M'))
        fig.autofmt_xdate()  

        ax.set_xlabel('Tiempo')
        ax.set_ylabel(data_title)
        ax.set_title(data_title)

        ax.legend()
        ax.grid(True)

        self.userData_range_graph_frame = tk.Frame(self.userData_graph_frame, bg="#626CC2")
        self.range_label = tk.Label(self.userData_range_graph_frame, text=f'Desde: {from_datetime}      Hasta: {to_datetime}', fg="white", bg="#626CC2", font=("Segoe UI", 14))
        self.range_label.pack(side=tk.LEFT, pady=5)
        self.userData_range_graph_frame.pack()

        canvas = FigureCanvasTkAgg(fig, master=self.userData_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        self.current_data_canvas = canvas

    """
        Logic for plotting user data into a graph

        Parameters:
        -data (csv) : Contains data to be plotted
        -data_frec (str) : Data show frecuency
        -data_title (str) : Selected type of data to be plotted.
        -ini (Datetime) : Datetime object where data begins
        -fin (Datetime) : Datetime object where data ends
        -dif (Datetime) : Datetime that contains data plot length 
    """
    def graphData(self, data, data_frec, data_title, ini, fin, dif):

        if self.current_data_canvas:
            self.current_data_canvas.get_tk_widget().destroy()

        if self.userData_range_graph_frame:
            self.userData_range_graph_frame.destroy()
            self.userData_range_graph_frame = None

        if self.checkIfEnoughData(data_frec, ini, fin):
            data['Time'] = pd.to_datetime(data['Time'])
            data.set_index('Time', inplace=True)

            fig = Figure(figsize=(8, 4))
            ax = fig.add_subplot(111)


            ax.plot(data.index, data[data_title], label=data_title, linestyle='-', color='c', linewidth=0.8)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            fig.autofmt_xdate()  

            ax.set_xlabel('Tiempo')
            ax.set_ylabel(data_title)
            ax.set_title(data_title)

            ax.legend()
            ax.grid(True)

            self.userData_range_graph_frame = tk.Frame(self.userData_graph_frame, bg="#626CC2")
            self.range_label = tk.Label(self.userData_range_graph_frame, text=f'Desde: {ini}      Hasta: {fin}', fg="white", bg="#626CC2", font=("Segoe UI", 14))
            self.range_label.pack(side=tk.LEFT, pady=5)
            self.userData_range_graph_frame.pack()

            canvas = FigureCanvasTkAgg(fig, master=self.userData_graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

            self.current_data_canvas = canvas
        

    """Logic for prediction with ML models"""
    def predict(self):
        try:
            self.data_pred_title = self.dataPredComboBox.get()
            steps = int(self.spinBox.get())
            threading.Thread(target=self.run_thread_prediction, args=(steps,self.data_pred_title,)).start()
        except ValueError :
            self.show_error_message(self.prediction_frame, "¡Selecciona un número de minutos antes de predecir!")

    
    """
        Logic for predictions with ML models with selected number of minutes = steps

        Parameters:
        -steps (int) : Number of minutes to predict into the future.    
    """
    def run_thread_prediction(self, steps,data_pred_title):
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

            self.controller.fitbitAPI.perfectDataForPrediction(steps, data_pred_title)
            
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
    def graphPredictions(self, predictions):
        
        if self.current_prediction_canvas:
            self.current_prediction_canvas.get_tk_widget().destroy()

        if self.predict_range_graph_frame:
            self.predict_range_graph_frame.destroy()
            self.predict_range_graph_frame = None
        
        
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        ax.plot(predictions.index, predictions, label='Predicciones', linestyle='-', color = 'c', linewidth=0.8)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  
        fig.autofmt_xdate() 

        ax.set_xlabel('Tiempo')
        ax.set_ylabel(self.data_pred_title)
        ax.set_title('Predicciones')
        ax.legend()
        ax.grid(True)

        self.predict_range_graph_frame = tk.Frame(self.prediction_graph_frame, bg="#626CC2")
        
        texto = None
        icon = None
        if self.data_pred_title == "HeartRate" :
            texto, icon = self.insidePreferedHeartRateZone(predictions)

        if (texto is not None) and (texto != "Ninguno" and self.data_pred_title == "HeartRate"):
            
            self.any_icon = Image.open(f'app/assets/images/{icon.value}')
            self.any_icon= self.any_icon.resize((30, 30), Image.LANCZOS)  
            self.any_icon = ImageTk.PhotoImage(self.any_icon)

            self.range_label = tk.Label(self.predict_range_graph_frame, text=f" {texto}", fg="white", bg="#626CC2", font=("Segoe UI", 14), image = self.any_icon, compound = "right")
            self.range_label.pack(side=tk.RIGHT, pady=5)
            self.predict_range_graph_frame.pack()
      
        canvas = FigureCanvasTkAgg(fig, master=self.prediction_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        self.current_prediction_canvas = canvas
    
    """
        Logic that checks whether predicted_mean are inside prefered HeartRate Zone

        Parameters:
        -predictions (list) : List of ML prediction for logged user.

    """
    def insidePreferedHeartRateZone(self, predictions):
       
        preferencia, FCM_value, FCR_value =  self.controller.get_user_purpose_FCM_FCR()
             
        if preferencia == "Ninguno" :
            return "Ninguno", None
        
        zonas = self.controller.calcular_zonas_fc(FCM_value, FCR_value) 
        
        zonas_prefererida_enum = self.controller.getZonesEnum(preferencia)
        zona_preferida_fc_min, zona_preferida_fc_max = zonas.get(zonas_prefererida_enum)
    
        prediction_mean = statistics.mean(predictions)

        if (zona_preferida_fc_min <= prediction_mean <= zona_preferida_fc_max):
                return "¡Sigue así! ", IconsEnum.HAPPY
        else :
            return self.checkWhereMeanLands(prediction_mean, zonas, zonas_prefererida_enum)
        
    """
        Logic that returns in which zone predicted_mean lands

        Parameters:
        -prediction_mean (int) : Mean of prediction list
        -zones (dictionary) : Dictionary that contains every zone
        
    """
    def checkWhereMeanLands(self, prediction_mean, zones, zona_preferida):
        return self.controller.checkWhereMeanLands(prediction_mean, zones, zona_preferida)

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
                # =========================================================
                # if ultimaAct == "Nunca":           
                    # mid_point = len(dates) // 2
                    # first_dates = dates[:mid_point]
                    # second_dates = dates[mid_point:]
            
                    #self.controller.fitbitAPI.getHeartRateData("1min", "00:00", "23:59", first_dates)
                    #self.controller.fitbitAPI.getHeartRateData("1min", "00:00", "23:59", second_dates)
                    
                    # self.update_progress(30)
                    #self.controller.fitbitAPI.getCaloriesDistanceStepsData("1min", "00:00", "23:59", first_dates)
                    #self.controller.fitbitAPI.getCaloriesDistanceStepsData("1min", "00:00", "23:59", second_dates)

                # else:
                    # self.controller.fitbitAPI.getHeartRateData("1min", "00:00", "23:59", dates)
                    
                    # self.update_progress(30)
                    # self.controller.fitbitAPI.getCaloriesDistanceStepsData("1min", "00:00", "23:59", dates)
                # =========================================================
                
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
        start_date = today - timedelta(days=29)
        return [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
   
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
        self.popup.title("Reauthorización Requerida")
        self.popup.geometry("400x150")

        message_label = tk.Label(self.popup, text="Tu token de autorización ha expirado.\nPor favor, re-autoriza con tu cuenta Fitbit.")
        message_label.pack(pady=10)
        
        reauthorize_button = tk.Button(self.popup, text="Re-autorizar", command=lambda: self.authoritize(None))
        reauthorize_button.pack(pady=10)
    
    """
        Logic for user authorize with FitBit

        Parameters:
        -email (str) : User mail
       
    """
    def authoritize(self, email):

        "acquire mutex"
        mutex.acquire()

        if self.controller.checkIfUserExistsByEmail(email) : 
            raise UserRegistrationError("El correo con el que intentas registrarte ya existe.")
        
        self.controller.authorize_with_fitbit()
        if self.popup :
            self.popup.destroy()
            