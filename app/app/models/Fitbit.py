import os
import hashlib
import base64
import requests
import json
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from app.models.ml.LightGBM import LightGBM


class FitbitAPI:
    def __init__(self, client_id, client_secret):

        self.client_id = client_id
        self.client_secret = client_secret
        self.code_verifier = None
        self.code_challenge = None
        self.state = None

        #info cambiante
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.expires_in = None
        
        self.data = None
        self.datos_train = None
        self.datos_test = None
        self.heartRateData = None
        self.exogenousData = None
        self.authentification_url = self.generate_authorization_url()

        self.light = LightGBM(datos_train=self.datos_train, datos_test=self.datos_test)



    def storeFitInfo(self, new_access_token, new_refresh_token, new_expires_in, user_id):
        self.access_token = new_access_token
        self.refresh_token = new_refresh_token
        self.expires_in = new_expires_in
        self.user_id = user_id

    def combine_monthly_data(self, base_filename, output_filename):
        combined_data = pd.DataFrame()
        for month in range(1, 13):
            filename = f"app/apiData/{base_filename}_{month}.csv"
            try:
                monthly_data = pd.read_csv(filename)
                combined_data = pd.concat([combined_data, monthly_data])
            except FileNotFoundError:
                continue
        combined_data.to_csv(output_filename, index=False)
        print(f"Los datos han sido combinados y guardados en '{output_filename}'.")


    def dataPreprocess(self):
        self.combine_monthly_data("calories_data", "app/apiData/calories_merged.csv")
        self.combine_monthly_data("distance_data", "app/apiData/distance_merged.csv")
        self.combine_monthly_data("heart_rate_data", "app/apiData/heart_rate_merged.csv")
        self.combine_monthly_data("steps_data", "app/apiData/steps_merged.csv")

        merged_files = [
            "app/apiData/calories_merged.csv",
            "app/apiData/distance_merged.csv",
            "app/apiData/heart_rate_merged.csv",
            "app/apiData/steps_merged.csv"
        ]

        combined_final_data = pd.read_csv(merged_files[0])
        for file in merged_files[1:]:
            data = pd.read_csv(file)
            combined_final_data = pd.merge(combined_final_data, data, on=["Id", "Date", "Time"], how="outer")

        combined_final_data['Time'] = pd.to_datetime(combined_final_data['Date'] + ' ' + combined_final_data['Time'])
        combined_final_data.drop(columns='Date', inplace=True)
        combined_final_data['HeartRate'] = combined_final_data.pop('Heart Rate')
        combined_final_data.to_csv("app/apiData/test_train_data_api_merged.csv", index=False)

        print(combined_final_data.head())
        self.perfectDataForPrediction(combined_final_data)

    def perfectDataForPrediction(self, data):
        data['Time'] = pd.to_datetime(data['Time'], format='%Y-%m-%d %H:%M:%S')
        data.set_index('Time', inplace=True)
        data = data.asfreq('60s').sort_index()

        self.datos_train = data[:-self.light.steps]
        self.datos_test = data[-self.light.steps:]

        print(f"Fechas train: {self.datos_train.index.min()} --- {self.datos_train.index.max()} (n={len(self.datos_train)})")
        print(f"Fechas test: {self.datos_test.index.min()} --- {self.datos_test.index.max()} (n={len(self.datos_test)})")
        print(f'Número de filas con missing values (datos_train): {self.datos_train.isnull().any(axis=1).mean()}')
        print(f'Número de filas con missing values (datos_test): {self.datos_test.isnull().any(axis=1).mean()}')

        self.datos_train.bfill(inplace=True)
        self.datos_test.bfill(inplace=True)

   
    def access_token_is_expired(self, access_token, expires_in):
        if access_token and expires_in:  
            expires_at_utc = expires_in.astimezone(timezone.utc)

            now_utc = datetime.now(timezone.utc)
            return now_utc > expires_at_utc
        else:
            return True 

    def checkRefreshToken(self):
         if self.access_token_is_expired(self.access_token, self.expires_in):
            self.refresh_access_token(self.refresh_token)

    def getUserProfile(self):
        self.checkRefreshToken()

        url = "https://api.fitbit.com/1/user/-/profile.json"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            self.guardar_en_csv(response.json())
            return response.json()
        else:
            print(response.status_code, response.text)

    def guardar_en_csv(self, data):
        csv_filename = f'app/apiData/{self.user_id}/profile.csv'
        os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
        csv_headers = data.keys()
    
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=csv_headers)
            writer.writeheader()
            writer.writerow(data)

    def fetch_and_store_data(self, base_url, detail_level, start_time, end_time, dates, csv_filename, csv_headers):
        self.checkRefreshToken()

        headers = {"Accept": "application/json", "Authorization": f"Bearer {self.access_token}"}
        all_data = []

        for date in dates:
            url = f"{base_url}{date}/1d/{detail_level}/time/{start_time}/{end_time}.json"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                all_data.append(response.json())
            else:
                print(f"Error obteniendo datos para {date}: {response.status_code}")
                print(response.text)

        self.store_csv_data(all_data, csv_filename, csv_headers)

    def store_csv_data(self, data, csv_filename, csv_headers):
        csv_data = []
        for day_data in data:
            date = day_data['activities-heart'][0]['dateTime']
            intraday_data = day_data['activities-heart-intraday']['dataset']
            for entry in intraday_data:
                time = entry['time']
                value = entry['value']
                csv_data.append([self.user_id, date, time, value])

        # Crear el directorio si no existe
        directory = os.path.dirname(csv_filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_headers)
            writer.writerows(csv_data)

        print(f"Los datos se han escrito en el archivo CSV: {csv_filename}")

    def getHeartRateData(self, detail_level, start_time, end_time, dates):
        self.checkRefreshToken()

        base_url = f"https://api.fitbit.com/1/user/{self.user_id}/activities/heart/date/"
        self.fetch_and_store_data(base_url, detail_level, start_time, end_time, dates, 
                                f"app/apiData/{self.user_id}/heart_rate_data_{datetime.today().month}.csv", 
                                ['Id', 'Date', 'Time', 'HeartRate'])

    def getCaloriesDistanceStepsData(self, detail_level, start_time, end_time, dates):
        self.checkRefreshToken()

        data_sources = ["calories", "distance", "steps"]
        for source in data_sources:
            base_url = f"https://api.fitbit.com/1/user/{self.user_id}/activities/{source}/date/"
            self.fetch_and_store_data(base_url, detail_level, start_time, end_time, dates, 
                                      f"app/apiData/{self.user_id}/{source}_data_{datetime.today().month}.csv", 
                                      ['Id', 'Date', 'Time', source.capitalize()])

    def storeFitbitUserInfo(self, user_id, access_token, refresh_token, expires_in):
        
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    def generate_code_verifier(self, length=64):
        code_verifier = base64.urlsafe_b64encode(os.urandom(length)).rstrip(b'=').decode('utf-8')
        self.code_verifier = code_verifier
        return self.code_verifier

    def generate_code_challenge(self):
        sha256_hash = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('utf-8')
        self.code_challenge = code_challenge
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
        return (f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={self.client_id}"
                f"&scope={scope_string}&code_challenge={self.code_challenge}&code_challenge_method=S256"
                f"&state={self.state}&redirect_uri={redirect_uri}")

    def get_access_token(self, code, state, redirect_uri="http://localhost:5000"):
        url = "https://api.fitbit.com/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
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
            self.storeFitbitUserInfo(response_data["user_id"], response_data["access_token"], 
                                        response_data["refresh_token"], response_data["expires_in"])
            return response_data["access_token"], response_data["refresh_token"], response_data["user_id"]
        else:
            print(f"Error getting access token: {response.status_code}")
            print(response.text)
            return None

    def refresh_access_token(self, refresh_token):
        url = "https://api.fitbit.com/oauth2/token"
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}"
        }
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            response_data = response.json()

            #Store token info
    
            self.access_token = response_data["access_token"]
            self.refresh_token = response_data["refresh_token"]
            self.expires_in =  response_data["expires_in"]
            self.user_id = response_data["user_id"]

            return response_data["access_token"], response_data["refresh_token"], response_data["expires_in"], response_data["user_id"]
        else:
            print(refresh_token)
            print(f"Error refreshing access token: {response.status_code}")
            print(response.text)
            return
