from flask import Flask, request
import threading
import requests
from app.models.Fitbit import FitbitAPI


class OAuthServer:
    def __init__(self, fitbit_api):
        self.app = Flask(__name__)
        self.app.route('/')(self.home)

        self.fitbit_api = fitbit_api
        self.oauth_server.start_server()

    
        self.code = None
        self.state = None

    def home(self):
        self.code = request.args.get('code')
        self.state = request.args.get('state')

        # Llama a la función get_access_token con los datos necesarios
        self.get_access_token()

        return "Puedes cerrar este navegador"

    def get_access_token(self):
        # Obtiene los datos del cliente y el código verificador de la instancia de FitbitAPI
        client_id = self.fitbit_api.client_id
        client_secret = self.fitbit_api.client_secret
        code_verifier = self.fitbit_api.code_verifier

        url = "https://api.fitbit.com/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "client_id": client_id,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:5000",
            "code": self.code,
            "code_verifier": code_verifier,
        }

        response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))

        if response.status_code == 200:
            response_data = response.json()
    
            user_id = response_data['user_id']
            access_token = response_data['access_token']
            refresh_token = response_data['refresh_token']
            expires_in = response_data["expires_in"]
         
            # Guardar la información en la base de datos
            self.store_fitbit_user_info(user_id, access_token, refresh_token,expires_in)
        else:
            print(f"La solicitud falló con el código de estado {response.status_code}")
            
    def store_fitbit_user_info(self, user_id, access_token, refresh_token,expires_in):
        self.fitbit_api.storeFitbitUserInfo(user_id, access_token, refresh_token,expires_in)

    def start_server(self):
        if not self.flask_thread or not self.flask_thread.is_alive():
            self.flask_thread = threading.Thread(target=self.run_flask)
            self.flask_thread.daemon = True
            self.flask_thread.start()

    def run_flask(self):
        self.app.run(debug=False, port=5000)

    def stop_server(self):
        try:
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None:
                func()
        except Exception as e:
            print(f"Error al detener el servidor: {e}")

