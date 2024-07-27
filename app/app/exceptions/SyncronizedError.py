# SyncronizedError.py

class SyncronizedError(Exception):
    """Excepción personalizada para errores en la sincronización con los datos del usuario"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def getMessage(self):
        return self.message
