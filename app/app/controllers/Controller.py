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

    
        #API fitbit
        #TODO de momento se los paso por arg, leer del fichero o import con python como macro
        self.fitbitAPI = FitbitAPI("23RFGM","4f602285fd2df734b04fe7d26a6680d7")
    
        #Servidor levanto el servidor que escuchara en localhost::5000 para obtener el code y state, 
        self.oauth_server = OAuthServer(self.fitbitAPI)
        

    
    def  predictions(self, minutes):
        return self.fitbitAPI.predictions(minutes)

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
        

    def findTokenInfo(self, email) :
       user_data = self.mongo.find_one_data("usuarios", query={"correo": email})
       fitbit_data = user_data.get("fitbit")
       access_token = fitbit_data["access_token"]
       refresh_token =fitbit_data["refresh_token"] 
       expires_in = fitbit_data["expires_in"] 
       user_id = fitbit_data["user_id"]

       if self.fitbitAPI.access_token_is_expired(access_token, expires_in) :
          print("needed new acces token")
          new_access_token , new_refresh_token, new_expires_in = self.fitbitAPI.refresh_access_token(refresh_token)
          return self.storeTokenInfo(email, new_access_token, new_refresh_token, new_expires_in, user_id)
       else :
           self.storeTokenInfo(email, access_token, refresh_token, expires_in, user_id)
           return access_token, refresh_token, expires_in
      
        
    def updateFitbitUserInfo(self, email):
        access_token, refresh_token, expires_in = self.findTokenInfo(email)

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
           
 
        return self.mongo.insert_data("usuarios", user_data)


    def authorize_with_fitbit(self):
        webbrowser.open(self.fitbitAPI.authentification_url)

   
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
        # Detener el servidor Flask
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        