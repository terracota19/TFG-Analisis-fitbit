import pymongo
from app.models.mongo import Mongo
from app.utils.hash import HashSHA_256
from datetime import datetime
from flask import Flask, request
import threading
import webbrowser
from app.utils.mini_server import OAuthServer
from app.models.ml.LightGBM import LightGBM
from app.models.Fitbit import FitbitAPI
import os


class Controller:
    def __init__(self, view):

       
        self.view = view
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.model = Mongo("tfg_fitbit", self.mongo_client)
        self.logged_in_user = None

        #Fitbit user DATA
        self.user_id = None
        self.access_token = None 
        self.refresh_token = None

        #API fitbit
        #TODO de momento se los paso por arg, leer del fichero o import con python como macro
        self.fitbitAPI = FitbitAPI("23RY6J","74cfc7ed3a2a070ecfd1139ac9366b17")
        print(self.fitbitAPI.authentification_url)


        #Servidor levanto el servidor que escuchara en localhost::5000 para obtener el code y state, 
        #para posteriomenre obtener el access token del cliente autorizado
        self.oauth_server = OAuthServer(self.fitbitAPI)
        self.oauth_server.start_server()

        #Modelo de prediccion, pasarle los datos iniciales previamente porcesados
        self.datos_train = []
        self.datos_test = []

        self.light = LightGBM(datos_train=self.datos_train, datos_test=self.datos_test)
       

    #(self, collection_name, query, field, value
    def updateApi_lastUpdate(self):
        hora_actual = datetime.now()
        if self.logged_in_user:
            user_id = self.logged_in_user.get("_id")
            if user_id:
                query = {"_id": user_id}
                new_values = {"set": {"ult_act": hora_actual}}  
                self.model.update_data("usuarios", query, "ult_act" , hora_actual)        
                
        return hora_actual
    
    def storeFitBitUserInfo(self,user_id, access_token, refresh_token):
        self.user_id = user_id
        self.access_token = access_token 
        self.refresh_token = refresh_token


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
            self.access_token = access_token
            self.refresh_token = refresh_token

            user_data = {
                "usuario": user,
                "password": hashed_password,
                "edad": edad,
                "salt": salt,
                "correo": email,
                "ult_act" : datetime.now(),
                "fitbit": {
                    "user_id": user_id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in
                }
            }
           
            #encript data
 
        return self.model.insert_data("usuarios", user_data)


    def authorize_with_fitbit(self):
        webbrowser.open(self.fitbitAPI.authentification_url)

   
    def check_login(self,  email, password):
        user_data = self.model.find_one_data("usuarios", query={"correo": email})
        if user_data and user_data.get("correo") == email:
            if HashSHA_256.verify_password(password, user_data["password"], user_data["salt"]):
                self.logged_in_user = user_data
                return True
            else:
                return False
        else:
            return False
    


    #def start_oauth_flow(self):
        # Abre el navegador web para iniciar el flujo OAuth
     #   oauth_url = self.fitbitAPI.authentification_url
       # webbrowser.open(oauth_url)
      #  #messagebox.showinfo("Info", "OAuth flow started. Please authorize the app in your browser.")

    def stop_server(self):
        # Detener el servidor Flask
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        #messagebox.showinfo("Server", "Server stopped")