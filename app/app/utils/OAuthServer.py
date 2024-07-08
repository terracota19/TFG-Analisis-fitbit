import requests
import threading

from flask import Flask, request

class OAuthServer:
    def __init__(self, fitAPI):

        """OAuthServer Flask app"""
        self.app = Flask(__name__)
        self.app.route('/')(self.home)
        
        """Flask Thread"""
        self.flask_thread = None
        
        """API Fitbit"""
        self.fitbit_api = fitAPI
        
        """Start server in localhost:5000"""
        self.start_server()

        """OAuthServer requests"""
        self.code = None
        self.state = None

    """Main method"""
    def home(self):
        self.code = request.args.get('code')
        self.state = request.args.get('state')

        self.get_access_token()
        return "¡Puedes Cerrar este navegador y Proceder a registrarte en HeartPred'it!"

    """Get access token from redirect_uri from Fitbit with assosiated code and state"""
    def get_access_token(self):
        
        client_id = self.fitbit_api.client_id
        client_secret = self.fitbit_api.client_secret
        code_verifier = self.fitbit_api.auth.code_verifier

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
            self.fitbit_api.storeFibitInfo(response_data['access_token'], response_data['refresh_token'],  response_data["expires_in"], response_data['user_id'])

        else:
            print(f"La solicitud falló con el código de estado {response.status_code}")
            
    """Start OAuthServer"""
    def start_server(self):
        if not self.flask_thread or not self.flask_thread.is_alive():

            self.flask_thread = threading.Thread(target=self.run_flask)
            self.flask_thread.daemon = True
            self.flask_thread.start()

    """Run server on localhost:5000"""
    def run_flask(self):
        self.app.run(debug=False, port=5000)

    """Stop server on localhost:5000"""
    def stop_server(self):
        try:
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None:
                func()
        except Exception as e:
            print(f"Error al detener el servidor: {e}")

