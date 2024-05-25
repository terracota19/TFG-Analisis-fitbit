import os
import hashlib
import base64
import requests

class FitbitAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.code_verifier = None
        self.code_challenge = None
        self.state = None
        
        self.access_token = None
        self.refresh_token = None
        self.user_id = None

        
        self.authentification_url = self.generate_authorization_url()

    def store_fitbit_user_info(self, user_id, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_id = user_id

    def generate_code_verifier(self, length=64):
        code_verifier = os.urandom(length)
        code_verifier = base64.urlsafe_b64encode(code_verifier).rstrip(b'=')
        self.code_verifier = code_verifier.decode('utf-8')
        return self.code_verifier

    def generate_code_challenge(self):
        sha256_hash = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=')
        self.code_challenge = code_challenge.decode('utf-8')
        return self.code_challenge

    def generate_authorization_url(self, redirect_uri='http://localhost:5000', scopes=None):
        if scopes is None:
            scopes = ['activity', 'cardio_fitness', 'electrocardiogram', 'heartrate', 'location', 'nutrition', 'oxygen_saturation', 'profile', 'respiratory_rate', 'settings', 'sleep', 'social', 'temperature', 'weight']
        self.code_verifier = self.generate_code_verifier()
        self.code_challenge = self.generate_code_challenge()
        self.state = os.urandom(16).hex()
        scope_string = '+'.join(scopes)
        authorization_url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={self.client_id}&scope={scope_string}&code_challenge={self.code_challenge}&code_challenge_method=S256&state={self.state}&redirect_uri={redirect_uri}"
        return authorization_url

    def get_access_token(self, code, state, redirect_uri = "http://localhost:5000"):
        url = "https://api.fitbit.com/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "client_id": self.client_id,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code,
            "code_verifier": self.code_verifier,
        }

        response = requests.post(url, headers=headers, data=data, auth=(self.client_id, ''))
        if response.status_code == 200:
            access_token = response.json()['access_token']
            refresh_token = response.json()['refresh_token']
            user_id = response.json()['user_id']
            return access_token, refresh_token, user_id
        else:
            print(f"La solicitud falló con el código de estado {response.status_code}")
            return None
        
   

    def refresh_access_token(self, refresh_token):
        url = "https://api.fitbit.com/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token,
        }
        response = requests.post(url, data=data, auth=(self.client_id, self.client_secret))
        if response.status_code != 200:
            print(f"La solicitud falló con el código de estado {response.status_code}")
            return None
        data = response.json()
        self.access_token = data['access_token']
        return self.access_token

    def get_user_data(self):
        url = "https://api.fitbit.com/1/user/-/profile.json"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"La solicitud falló con el código de estado {response.status_code}")
            return None
        return response.json()

# Ejemplo de uso
#if __name__ == "__main__":
 #   client_id = "23RY6J"
  #  client_secret = "your_client_secret"

   # fitbit_oauth = FitbitOAuth(client_id, client_secret)

    # Paso 1: Generar URL de autorización
    #authorization_url = fitbit_oauth.generate_authorization_url()
    #print("URL de autorización:", authorization_url)

    # Paso 2: Obtener código de autorización manualmente y redirigir a la URL de autorización
    #code = input("Ingrese el código de autorización: ")

    # Paso 3: Obtener token de acceso
    ##access_token = fitbit_oauth.get_access_token(code)
   # print("Token de acceso:", access_token)

    # Paso 4: Obtener datos del usuario
    #user_data = fitbit_oauth.get_user_data()
    #print("Datos del usuario:", user_data)
