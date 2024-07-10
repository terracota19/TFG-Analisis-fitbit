from app.views.Gui import App

if __name__ == "__main__":
    """
        App HeartPred'it instance.
    """
    app = App()
    
    """
        Logic for closing mongoDB client conection and stop localhost OAuthServer on port 5000 and destroy app HeartPred'it.
    """
    def on_close():
        
        #Cerramos la conexion con mongo, ya que no se va a utilizar 
        app.controller.mongo.close_connection()
        
        #Paramos el servidor porque ya no se va a utilizar
        app.controller.oauth_server.stop_server()

        app.destroy()
        
    """
        Associate closing app window with on_close logic.
    """
    app.protocol("WM_DELETE_WINDOW", on_close)

    """
        Main HeartPred'it Loop
    """
    app.mainloop()
