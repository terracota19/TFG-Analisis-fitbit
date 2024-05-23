from app.models.mongo import Mongo
from app.utils.hash import HashSHA_256

class Controller:
    def __init__(self, view):
        self.view = view
        self.model = Mongo("tfg_fitbit")
        self.logged_in_user = None
   


    def register(self, user, password, edad):
        if not (user and password and edad) : return False
        else : 
            hashed_password, salt = HashSHA_256.hash_password(password) 
            user_data = {
                "usuario": user,
                "password": hashed_password,
                "edad" : edad,
                "salt" : salt
            }
            
            return self.model.insert_data("usuarios", user_data)

       
    #print(f"User: {user_data['usuario']}, Password: {user_data['password']}") 
    def check_login(self, user, password):
        user_data = self.model.find_one_data("usuarios", query={"usuario": user})
        if user_data:
            if HashSHA_256.verify_password(password, user_data["password"], user_data["salt"]):
                self.logged_in_user = user
                return True
            else:
                return False
        else:
            return False