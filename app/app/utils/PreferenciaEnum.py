from enum import Enum

class PreferenciaEnum(Enum):
    
    NINGUNA = ("Ninguna", -1)
    ZONA0 = ("Ninguna zona", 0)
    ZONA1 = ("Mejorar salud general", 1)
    ZONA2 = ("Quema de grasa", 2)
    ZONA3 = ("Mejorar resistencia cardiovascular", 3)
    ZONA4 = ("Mejorar la velocidad y potencia", 4)
    ZONA5 = ("Mejorar máximo rendimiento", 5)
    ZONA6 = ("Ninguna zona", 6)

    def __init__(self, description, value):
        self._description = description
        self._value = value

    @property
    def description(self):
        return self._description

    @property
    def value(self):
        return self._value
