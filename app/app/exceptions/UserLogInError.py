# UserLogInError.py

class UserLogInError(Exception):
    """Excepción personalizada para errores de inicio de sesion del usuario."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def getMessage(self):
        return self.message
