import os
import hashlib
import base64
import requests
from datetime import datetime, timedelta, timezone
import json
import csv

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
        self.expires_at = None  

        self.authentification_url = self.generate_authorization_url()

    def access_token_is_expired(self):
        if self.access_token and self.expires_at:
            return datetime.utcnow().replace(tzinfo=timezone.utc) > self.expires_at
        return True

    def getUserProfile(self):
        if self.access_token_is_expired():
            self.refresh_access_token()

        url_user_profile = "https://api.fitbit.com/1/user/-/profile.json"
        headers_user_profile = {
            "Authorization": f"Bearer {self.access_token}"
        }

        response_user_profile = requests.get(url_user_profile, headers=headers_user_profile)
        
        if response_user_profile.status_code == 200:
            return response_user_profile.json()
        else:
            print(response_user_profile.status_code)
            print(response_user_profile.text)

    def getHeartRateData(self, detail_level, start_time, end_time, dates):
        if self.access_token_is_expired():
            self.refresh_access_token()

        base_url = f"https://api.fitbit.com/1/user/{self.user_id}/activities/heart/date/"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        heart_rate_data = []
        for date in dates:
            url = f"{base_url}{date}/1d/{detail_level}/time/{start_time}/{end_time}.json"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                heart_rate_data.append(data)
            else:
                print(f"Error obteniendo datos para {date}: {response.status_code}")
                print(response.text)

        self.storeHeartRateData(heart_rate_data)
        return heart_rate_data
     
    def storeHeartRateData(self, heart_rate_data):
        # Lista para almacenar los datos a escribir en el CSV
        csv_data = []

        # Recorrer los datos de frecuencia cardíaca
        for data in heart_rate_data:
            # Obtener la fecha
            date = data['activities-heart'][0]['dateTime']
            # Obtener los registros de frecuencia cardíaca intradiarios
            intraday_data = data['activities-heart-intraday']['dataset']
            # Recorrer los registros intradiarios
            for entry in intraday_data:
                # Obtener el tiempo y el ritmo cardíaco
                time = entry['time']
                heart_rate = entry['value']
                # Agregar los datos a la lista
                csv_data.append([self.user_id,date, time, heart_rate])

        # Escribir los datos en un archivo CSV
        csv_file_path = f"app/apiData/heart_rate_data_{4}.csv"
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Id', 'Date', 'Time', 'Heart Rate'])
            writer.writerows(csv_data)

        print(f"Los datos se han escrito en el archivo CSV: {csv_file_path}")

    def store_fitbit_user_info(self, user_id, access_token, refresh_token, expires_in):
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)  # Añade esta línea

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
            scopes = [
                'activity', 'cardio_fitness', 'electrocardiogram', 'heartrate', 'location',
                'nutrition', 'oxygen_saturation', 'profile', 'respiratory_rate', 'settings',
                'sleep', 'social', 'temperature', 'weight'
            ]
        self.code_verifier = self.generate_code_verifier()
        self.code_challenge = self.generate_code_challenge()
        self.state = os.urandom(16).hex()
        scope_string = '+'.join(scopes)
        authorization_url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={self.client_id}&scope={scope_string}&code_challenge={self.code_challenge}&code_challenge_method=S256&state={self.state}&redirect_uri={redirect_uri}"
        return authorization_url

    def get_access_token(self, code, state, redirect_uri="http://localhost:5000"):
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
            response_data = response.json()
            access_token = response_data["access_token"]
            refresh_token = response_data["refresh_token"]
            user_id = response_data["user_id"]
            expires_in = response_data["expires_in"]

            self.store_fitbit_user_info(user_id, access_token, refresh_token, expires_in)

            return access_token, refresh_token, user_id
        else:
            print(f"Error getting access token: {response.status_code}")
            print(response.text)
            return None

    def refresh_access_token(self):
        url = "https://api.fitbit.com/oauth2/token"
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            response_data = response.json()
            self.access_token
