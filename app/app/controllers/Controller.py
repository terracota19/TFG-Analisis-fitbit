import pymongo
import re
from app.models.Mongo import Mongo
from app.utils.Hashing import HashSHA_256
from datetime import datetime
from flask import Flask, request
import threading
import webbrowser
from app.utils.OAuthServer import OAuthServer
from app.models.ML.LightGBM import LightGBM
from app.models.FitBit.Fitbit import FitbitAPI
import os

#Exceptions
from app.exceptions.UserRegistrationError import UserRegistrationError
from app.exceptions.UserLogInError import UserLogInError
from app.exceptions.UserFitbitAccountAlreadyInUseError import UserFitbitAccountAlreadyInUseError

class Controller:
    def __init__(self, view):

        """Gui view"""
        self.view = view
        
        """MongoDB"""
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongo = Mongo("tfg_fitbit", self.mongo_client)
        
        """User info"""
        self.logged_in_user = None
        self.login_frame = None 
    
        """API Fitbit"""
        self.fitbitAPI = FitbitAPI("23RY6J","60cf8dbcf9a5964bb6a57208db6a96a1", self.mongo)
        #self.fitbitAPI = FitbitAPI("23RFGM","4f602285fd2df734b04fe7d26a6680d7", self.mongo)
    
        """OAuthServer""" 
        self.oauth_server = OAuthServer(self.fitbitAPI)
        

    
    def  predictions(self):
        return self.fitbitAPI.predictions()
    
    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email)
        
    
    def datosReales(self):
        return self.fitbitAPI.datosReales()

    def checkLasUpdate(self):
        user_id = self.logged_in_user.get("_id")
        if user_id:
            query = {"_id": user_id}
            self.user_data_actualizada = self.mongo.find_one_data("usuarios", query)
            return self.user_data_actualizada.get("ult_act")
        
        return None
    def deleteUserAccount(self):
        user_id = self.logged_in_user.get("_id")
        if user_id:
            self.mongo.delete_data("usuarios", {"_id": user_id})

            self.view.create_login_frame() 
            self.view.heartpred_frame = self.view.app_frame
            self.view.heartpred_frame.destroy()

    def validate_string(self, s):
        return isinstance(s, str) and bool(s.strip())
    
    def validate_numeric(self, value):
        return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
    
    def sanitize_input(self, input_string):
        return re.sub(r'[<>]', '', input_string)

    def set_login_frame(self, login_frame):
        self.login_frame = login_frame
    
    def logout(self):
        self.logged_in_user = None
    


    def storeMongoTokens(self, access_token, refresh_token, expires_in, user_id):
        
        self.mongo.update_data("usuarios", query = {"fitbit.user_id" : user_id}, field="fitbit.access_token", value=access_token)
        self.mongo.update_data("usuarios", query = {"fitbit.user_id" : user_id}, field="fitbit.refresh_token", value=refresh_token)
        self.mongo.update_data("usuarios", query = {"fitbit.user_id" : user_id} , field="fitbit.expires_in", value=expires_in)
        

    def updateApi_lastUpdate(self):
        hora_actual = datetime.now()
        if self.logged_in_user:
            user_id = self.logged_in_user.get("_id")
            if user_id:
                query = {"_id": user_id}
                new_values = {"set": {"ult_act": hora_actual}}  
                self.mongo.update_data("usuarios", query, "ult_act" , hora_actual)        
                
        return hora_actual
    


    def storeTokenInfo(self,email, user_id, new_access_token, new_refresh_token, new_expires_in):
        self.fitbitAPI.storeFibitInfo(new_access_token, new_refresh_token, new_expires_in,user_id)

        self.mongo.update_data("usuarios", query = {"correo" : email}, field="fitbit.access_token", value=new_access_token)
        self.mongo.update_data("usuarios", query = {"correo" : email}, field="fitbit.refresh_token", value=new_refresh_token)
        self.mongo.update_data("usuarios", query = {"correo" : email} , field="fitbit.expires_in", value=new_expires_in)
        
        return new_access_token, new_refresh_token, new_expires_in
        

    def findTokenInfo(self, email):
        user_data = self.mongo.find_one_data("usuarios", query={"correo": email})
        if not user_data:
            return None, None, None, None, True

        fitbit_data = user_data.get("fitbit")
        if not fitbit_data:
            return None, None, None, None, True

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

        
    def updateFitbitUserInfo(self, email):
        result = self.findTokenInfo(email)
        if result is None:
            self.view.showErrorPopup("User data not found")
            return

        access_token, refresh_token, expires_in, user_id, needs_reauth = result
       


    def last_update(self) :
       if self.logged_in_user and "ult_act" in self.logged_in_user:
            return self.logged_in_user["ult_act"]

    def user_info(self):
        if self.logged_in_user and "usuario" in self.logged_in_user:
            return self.logged_in_user["usuario"]
        else:
            return None
    def validate_pass_strength(self, password):
        
        if len(password) < 8:
            raise UserRegistrationError("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r"[A-Z]", password):
            raise UserRegistrationError("La contraseña debe contener al menos una letra mayúscula.")
        
        if not re.search(r"[a-z]", password):
            raise UserRegistrationError("La contraseña debe contener al menos una letra minúscula.")
        
        if not re.search(r"[0-9]", password):
            raise UserRegistrationError("La contraseña debe contener al menos un número.")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise UserRegistrationError("La contraseña debe contener al menos un carácter especial.")
        
        return True
    
    def register(self, user, email, password, edad, user_id, access_token, refresh_token, expires_in):
        if not (user and email and password and edad):
            raise UserRegistrationError("Upss...Todos los campos son obligatorios (*).")
        
        if not self.validate_numeric(edad):
            raise UserRegistrationError("La edad debe ser un valor numérico.")
        
        if not self.validate_email(email):
            raise UserRegistrationError("El formato del correo electrónico no es válido ej : (example@gmail.com).")
        
        if not self.validate_string(user):
            raise UserRegistrationError("El nombre de usuario no es válido.")
        
        self.validate_pass_strength(password)
        
        
        user = self.sanitize_input(user)
        email = self.sanitize_input(email)
        password = self.sanitize_input(password)
        edad = int(self.sanitize_input(edad))
    
        self.checkIfUserExists(email, user_id)
    
        hashed_password, salt = HashSHA_256.hash_password(password)
        
        self.user_id = user_id
        
        user_data = {
            "usuario": user,
            "password": hashed_password,
            "edad": edad,
            "salt": salt,
            "correo": email,
            "ult_act": None,
            "fitbit": {
                "user_id": user_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in
            }
        }
        
        exito = self.mongo.insert_data("usuarios", user_data)
        return exito
        
    def authorize_with_fitbit(self, user, email, password, age):
          if not (user and email and password and age):
            raise UserRegistrationError("Antes de autorizar rellena todos los campos (*Obligatorios)")
          else :
            webbrowser.open(self.fitbitAPI.authentification_url)
            return True

    def checkIfUserExists(self, email, user_id):
        user_data_by_email = self.mongo.find_one_data("usuarios", query={"correo": email})
        
        if user_data_by_email:
            raise UserRegistrationError(f"Usuario con email '{email}' ya existe.")
        
        user_data_by_user_id = self.mongo.find_one_data("usuarios", query={"fitbit.user_id": user_id})
        
        if user_data_by_user_id:
            raise UserFitbitAccountAlreadyInUseError(f"La cuenta de Fitbit con la que autorizo está asociado a otro usuario ")
        
    def checkReAuth(self, user_data):
        if self.fitbitAPI.checkRefreshToken(user_data.get("fitbit")):
            self.view.reauthorizationPopup()
        
    def check_login(self, email, password):
        if not (email and password):
            raise UserLogInError("Upss...Todos los campos de inicio de sesión son obligatorios (*).")
        
        if not self.validate_email(email):
            raise UserLogInError("El formato del correo electrónico no es válido.")
        
        if not self.validate_string(password):
            raise UserLogInError("La contraseña no es válida.")
        
        
        
        email = self.sanitize_input(email)
        password = self.sanitize_input(password)
        
        user_data = self.mongo.find_one_data("usuarios", query={"correo": email})
        
        if user_data and user_data.get("correo") == email:
            
            self.checkReAuth(user_data)

            if HashSHA_256.verify_password(password, user_data["password"], user_data["salt"]):
                self.logged_in_user = user_data
                return True
            else:
                raise UserLogInError("¡Usuario no identificado!, chequea la contraseña")
        else:
            raise UserLogInError("¡Usuario no identificado!, chequea el campo correo")

    def stop_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        