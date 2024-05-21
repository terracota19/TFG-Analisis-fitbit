class Controller:
    def __init__(self, view):
        self.view = view
        
    def on_button_click(self):
        self.view.label.config(text="¡Botón Presionado!")
