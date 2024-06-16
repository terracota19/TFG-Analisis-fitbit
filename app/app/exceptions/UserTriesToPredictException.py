# UserTriesToPredictException.py

class UserTriesToPredictException(Exception):
    """Excepción personalizada para errores de intento de predecir sin haber sincronizado nunca la pulsera"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def getMessage(self):
        return self.message
