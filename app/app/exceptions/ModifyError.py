# ModifyError.py

class ModifyError(Exception):
    """Excepción personalizada para errores de intento modificación de ajustes de usuario"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def getMessage(self):
        return self.message
