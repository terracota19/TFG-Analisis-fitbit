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
        
    def createTopLabel(self):
        fontArial = get_arial20()
        self.label = tk.Label(self, text="Bienvenido a HeartPred'it", bg="gray", fg="white", font=fontArial, height=2)
        self.label.pack(pady=20, padx=20, fill=tk.X)
       
