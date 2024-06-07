# UserFitbitAccountAlreadyInUseError.py

class UserFitbitAccountAlreadyInUseError(Exception):
    """Excepción personalizada para la prevención de creación de dos cuentas enlazadas con el mismo correo de fitbit."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def getMessage(self):
        return self.message
