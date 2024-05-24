import pymongo
from app.models.mongo import Mongo
from app.utils.hash import HashSHA_256
from datetime import datetime

class Controller:
    def __init__(self, view):
        self.view = view
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.model = Mongo("tfg_fitbit", self.mongo_client)
        self.logged_in_user = None


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


    def last_update(self) :
       if self.logged_in_user and "ult_act" in self.logged_in_user:
            return self.logged_in_user["ult_act"]

    def user_info(self):
        if self.logged_in_user and "usuario" in self.logged_in_user:
            return self.logged_in_user["usuario"]
        else:
            return None

    def register(self, user, email, password, edad):
        if not (user and email and password and edad):
            return False
        else:
            hashed_password, salt = HashSHA_256.hash_password(password)
            user_data = {
                "usuario": user,
                "password": hashed_password,
                "edad": edad,
                "salt": salt,
                "correo": email
            }
            return self.model.insert_data("usuarios", user_data)

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
