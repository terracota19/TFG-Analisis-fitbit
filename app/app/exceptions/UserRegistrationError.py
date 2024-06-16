# UserRegistrationError.py

class UserRegistrationError(Exception):
    """Excepción personalizada para errores de registro de usuario."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def getMessage(self):
        return self.message
