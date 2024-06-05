import pymongo
from app.models.Mongo import Mongo
from app.utils.Hashing import HashSHA_256
from datetime import datetime
from flask import Flask, request
import threading
import webbrowser
from app.utils.OAuthServer import OAuthServer
from app.models.ML.LightGBM import LightGBM
from app.models.Fitbit import FitbitAPI
import os


class Controller:
    def __init__(self, view):

       
        self.view = view
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongo = Mongo("tfg_fitbit", self.mongo_client)
        self.logged_in_user = None
        self.login_frame = None 

    
        #API fitbit
        #TODO de momento se los paso por arg, leer del fichero o import con python como macro
        self.fitbitAPI = FitbitAPI("23RY6J","74cfc7ed3a2a070ecfd1139ac9366b17")
    
        #Servidor levanto el servidor que escuchara en localhost::5000 para obtener el code y state, 
        self.oauth_server = OAuthServer(self.fitbitAPI)
        

    
    def  predictions(self, minutes):
        return self.fitbitAPI.predictions(minutes)


    def set_login_frame(self, login_frame):
        self.login_frame = login_frame
    
    def logout(self):
        self.logged_in_user = None
        self.view.create_login_frame()
        
        self.view.heartpred_frame = self.view.app_frame
        self.view.heartpred_frame.destroy()


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
    


    def storeTokenInfo(self,email, new_access_token, new_refresh_token, new_expires_in, user_id):
        self.fitbitAPI.storeFitInfo(new_access_token, new_refresh_token, new_expires_in, user_id= user_id)

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

            self.storeTokenInfo(email, new_access_token, new_refresh_token, new_expires_in, user_id)
            return new_access_token, new_refresh_token, new_expires_in, user_id, False
        else:
            
            self.fitbitAPI.storeFitInfo(access_token, refresh_token, expires_in, user_id)
            return access_token, refresh_token, expires_in, user_id, False

        
    def updateFitbitUserInfo(self, email):
        result = self.findTokenInfo(email)
        if result is None:
            self.view.showErrorPopup("User data not found")
            return

        access_token, refresh_token, expires_in, user_id, needs_reauth = result
        if needs_reauth:
            self.view.reauthorizationPopup()


    def last_update(self) :
       if self.logged_in_user and "ult_act" in self.logged_in_user:
            return self.logged_in_user["ult_act"]

    def user_info(self):
        if self.logged_in_user and "usuario" in self.logged_in_user:
            return self.logged_in_user["usuario"]
        else:
            return None

    def register(self, user, email, password, edad, user_id, access_token, refresh_token, expires_in):
        if not (user and email and password and edad):
            return False
        else:
            hashed_password, salt = HashSHA_256.hash_password(password)
           
            self.user_id = user_id
      
            user_data = {
                "usuario": user,
                "password": hashed_password,
                "edad": edad,
                "salt": salt,
                "correo": email,
                "ult_act" : datetime.now(),
                "fitbit" : {
                    "user_id" : user_id,
                    "access_token" : access_token,
                    "refresh_token" : refresh_token,
                    "expires_in" : expires_in
                }
            }
           
 
        exito = self.mongo.insert_data("usuarios", user_data)
        return exito


    def authorize_with_fitbit(self):
        webbrowser.open(self.fitbitAPI.authentification_url)
        return True
       

   
    def check_login(self,  email, password):
      

        user_data = self.mongo.find_one_data("usuarios", query={"correo": email})
        if user_data and user_data.get("correo") == email:
            if HashSHA_256.verify_password(password, user_data["password"], user_data["salt"]):
                self.logged_in_user = user_data
                return True
            else:
                return False
        else:
            return False
    

    def stop_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        