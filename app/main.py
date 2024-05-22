from app.gui import App

if __name__ == "__main__":
    app = App()

    def on_close():
       
        app.controller.model.close_connection()
        app.destroy()

    # Vincula la función on_close al evento de cierre de la ventana
    app.protocol("WM_DELETE_WINDOW", on_close)

    app.mainloop()
