# UserFitbitAccountAlreadyInUseError.py

class UserFitbitAccountAlreadyInUseError(Exception):
    """Excepción personalizada para errores en el uso de autorizacion con una cuenta de fitbit existe de otro usuario."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def getMessage(self):
        return self.message
