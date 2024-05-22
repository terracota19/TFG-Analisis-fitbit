from app.models.mongo import Mongo
from app.utils.hash import HashSHA_256

class Controller:
    def __init__(self, view):
        self.view = view
        self.model = Mongo("tfg_fitbit")
        self.logged_in_user = None
    
    def get_query_results(self):
        query_results = self.model.find_data("usuarios", query={})
        return query_results


    def register(self, user, password):
        print("logica de registro")

    def check_login(self, user, password):
        user_data = self.model.find_data("usuarios", query={"usuario": user})
        for document in user_data:
            stored_hashed_password = document.get("password")
            stored_salt = document.get("salt")
            
            if HashSHA_256.verify_password(password, stored_hashed_password, stored_salt):
                self.logged_in_user = document
                print("Inicio de sesión exitoso")
                return
        print("Usuario no encontrado o contraseña incorrecta")
