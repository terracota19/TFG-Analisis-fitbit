# PredictionError.py

class PredictionError(Exception):
    """Excepción personalizada para errores de intento de prediccion pero no hay datos para predecir"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def getMessage(self):
        return self.message
