from app.gui import App

if __name__ == "__main__":
    app = App()

    def on_close():
       
        app.controller.model.close_connection()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)

    app.mainloop()
