# GraphDataError.py

class GraphDataError(Exception):
    """Excepción personalizada para errores de intento visualización de un rango concreto pero no hay datos suficientes para mostrarlos"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def getMessage(self):
        return self.message
