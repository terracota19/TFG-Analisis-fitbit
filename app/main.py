from app.gui import App

if __name__ == "__main__":
    app = App()

    def on_close():
        
        #Cerramos la conexion con mongo, ya que no se va a utilizar 
        app.controller.mongo.close_connection()
        
        #paramos el servidor porque ya no se va a utilizar
        app.controller.oauth_server.stop_server()

        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)

    app.mainloop()
