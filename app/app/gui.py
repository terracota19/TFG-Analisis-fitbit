import tkinter as tk
from tkinter import ttk
from app.controllers import Controller
from assets.fonts.fonts import get_arial20

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("HeartPred'it")
        self.geometry("700x600")
        
        self.controller = Controller(self)

        self.createTopLabel()
    

    def display_query_results(self):
        # Realizar la consulta
        query_results = self.controller.get_query_results()  # Supongamos que hay un método para obtener los resultados de la consulta en el controlador
        
        # Crear un texto para mostrar en el Label
        query_text = ""
        for result in query_results:
            query_text += f"Correo: {result['email']}, Edad: {result['edad']}\n"  # Supongamos que los resultados de la consulta son diccionarios con claves 'email' y 'edad'
        
        # Actualizar el texto del Label con la información de la consulta
        self.label.config(text=query_text)

        
    def createTopLabel(self):
        fontArial = get_arial20()
        self.label = tk.Label(self, text="Bienvenido a HeartPred'it", bg="gray", fg="white", font=fontArial, height=2)
        self.label.pack(pady=20, padx=20, fill=tk.X)
