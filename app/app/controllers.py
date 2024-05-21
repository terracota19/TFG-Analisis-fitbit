from app.models.mongo import Mongo

class Controller:
    def __init__(self, view):
        self.view = view
        self.model = Mongo("tfg_fitbit")
    
    def get_query_results(self):

        query_results = self.model.find_data("usuarios", query={})  # Suponiendo que esto devuelve los resultados de la consulta
        return query_results
