import os
import csv
import shutil
import requests
import pandas as pd

from datetime import datetime
from app.exceptions.PredictionError import PredictionError
from app.exceptions.SyncronizedError import SyncronizedError

class FitBitDataHandler :
    def __init__(self):
        super().__init__()
        pass


    """
        Combines all 'base_filename' existing csv`s from January to December into one csv 
    """    
    def combine_monthly_data(self, base_filename, output_filename, user_id):
        combined_data = pd.DataFrame()
        for month in range(1, 13):
            filename = f"app/DataAPI/{user_id}/{base_filename}_{month}.csv"
            try:
                monthly_data = pd.read_csv(filename)
                combined_data = pd.concat([combined_data, monthly_data])
            except FileNotFoundError:
                continue
        
        self.createDirectory(output_filename)

        combined_data.to_csv(output_filename, index=False)


    """
        Deletes all contents/data related to deleted user.

        Parameters:
        -user_id (str): user fitbit id
    """
    def deleteUserFitBitData(self, user_id):
        path = f"app/DataAPI/{user_id}"
        try :
           shutil.rmtree(path)
        except OSError as e:
            print(e)

    
    """
        Combines all calories,distance, heartRate, steps merged csv into final csv 'test_train_data_api_merged.csv'
    """
    def dataPreprocess(self, user_id):
    
        self.combine_monthly_data("calories_data", f"app/DataAPI/{user_id}/calories_merged.csv", user_id)
        self.combine_monthly_data("distance_data", f"app/DataAPI/{user_id}/distance_merged.csv",user_id)
        self.combine_monthly_data("heart_rate_data", f"app/DataAPI/{user_id}/heart_rate_merged.csv",user_id)
        self.combine_monthly_data("steps_data", f"app/DataAPI/{user_id}/steps_merged.csv",user_id)

       
        merged_files = [
            f"app/DataAPI/{user_id}/calories_merged.csv",
            f"app/DataAPI/{user_id}/distance_merged.csv",
            f"app/DataAPI/{user_id}/heart_rate_merged.csv",
            f"app/DataAPI/{user_id}/steps_merged.csv"
        ]

        
        combined_final_data = None

        for file in merged_files:
            try:
                 data = pd.read_csv(file)    
            except FileNotFoundError:
                continue
           
            if combined_final_data is None:
                combined_final_data = data
            else:
                combined_final_data = pd.merge(combined_final_data, data, on=["Id", "Date", "Time"], how="outer")
        

        combined_file_path = f"app/DataAPI/{user_id}/test_train_data_api_merged.csv"
        combined_final_data =  self.dateParser(combined_final_data)
        
        combined_final_data.bfill(inplace = True)
        combined_final_data.dropna(inplace=True)
        
        combined_final_data.to_csv(combined_file_path, index=False)


    """
        Converts [`Time'] from test_train_data_api_merged['Time'] & test_train_data_api_merged['Date'] into DateTime 

        Returns:
        - csv : Converted data['Time'] & data['Date'] into one DateTime column data['Time].
    """
    def dateParser(self, datos_combinados_final):
    
        datos_combinados_final['Time'] = pd.to_datetime(datos_combinados_final['Date'] + ' ' + datos_combinados_final['Time'])
        datos_combinados_final.drop(columns='Date', inplace=True)
        return datos_combinados_final

    """
        Last minute user api data syncronized.

        Parameters:
        -user_id (str) : String identifying user with FitBit on HeartPred'it app.
        
        Returns:
        - (Datetime) : Last minute user api data syncronized.
    """
    def lastUpdate(self,user_id):
        
        combined_file_path = f"app/DataAPI/{user_id}/test_train_data_api_merged.csv"
        self.createDirectory(combined_file_path)
        
        try:
            data = pd.read_csv(combined_file_path)
            if len(data) > 1:
                return pd.to_datetime(data['Time'].iloc[-1])
            else :
                raise SyncronizedError("Error en la sincronización, prueba a sincronizar datos con Fitbit a través de su App")
        except FileNotFoundError:
           pass

       
    """
        Prepares data for model prediction requirements, such as non-Nan values on dataset

        Parameters:
        -steps (int) : Number of minutes to predict into future.
        -user_id (str) : Identifies user with Fitbit Account.

        Returns:
        - (json) : CSV with train data for ML models,
             and CSV with random Exog variables['Calories', 'Distance','Steps'] for model to use 
    
    """
    def perfectDataForPrediction(self,steps, user_id):


        combined_file_path = f"app/DataAPI/{user_id}/test_train_data_api_merged.csv"
        self.createDirectory(combined_file_path)
        data = pd.read_csv(combined_file_path)
        
        if len(data) > 1:
           
            data['Time'] = pd.to_datetime(data['Time'])
            data.set_index('Time', inplace=True)  
             
            # This removes possibles duplicated index rows
            data = data[~data.index.duplicated(keep='first')]
               
            data = data.asfreq('min')
            
            last_time = data.index[-1]

            future_index = pd.date_range(start=last_time, periods= steps + 1, freq='min')[1:]
            
            last_calories = data['Calories'].iloc[-1]
            last_steps = data['Steps'].iloc[-1]
            last_distance = data['Distance'].iloc[-1]

            future_exog = pd.DataFrame({
                'Calories': [last_calories] * len(future_index),
                'Steps': [last_steps] * len(future_index),
                'Distance': [last_distance] * len(future_index)
            }, index=future_index)

            datos_train = data.iloc[:] 
            datos_train = datos_train.bfill()

            return datos_train, future_exog
        else :
            raise PredictionError("Hubo un error en la predicción, sincroniza de nuevo los datos.")
          

    """
        Fetches data for the user logged in, for every date where the user has not synchronized with the app 
        within the specified time range [start_time -- end_time].

        Parameters:
        - base_url (str): The base URL for the API endpoint.
        - detail_level (str): The level of detail for the data.
        - start_time (str): The start time for the data fetch in the format 'HH:MM'.
        - end_time (str): The end time for the data fetch in the format 'HH:MM'.
        - dates (list): A list of dates (as strings) for which data needs to be fetched.
        - csv_filename (str): The name of the CSV file to save the data.
        - csv_headers (list): The headers for the CSV file.

        Returns:
        - list: A list of data fetched from the API for the specified dates.
    
    """
    def fetchData(self, base_url, detail_level, start_time, end_time, dates,  access_token):
        
        headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
        all_data = []

        for date in dates:
            url = f"{base_url}{date}/1d/{detail_level}/time/{start_time}/{end_time}.json"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                all_data.append(response.json())
            else:
                if(response.status_code == 429):
                    raise SyncronizedError("Error en la sincronización (Too many Requests), inténtelo más tarde dentro de 1 hora.")
                print(f"Error obteniendo datos para {date}: {response.status_code}")
                print(response.text)
        
        return all_data
    """
        Stores HeartRate data into a csv.

        Parameters:
        -data (json) : Json file with HeartRate data
        -csv_filename (str) : The filename where data will be stored
        -csv_headers (list) : list with csv Headers e.g. HeartRate, user_id ... etc
    
    """
    def store_HeartRate_csv(self, data, csv_filename, csv_headers, user_id):
        csv_data = []
        for day_data in data:
            date = day_data['activities-heart'][0]['dateTime']
            intraday_data = day_data['activities-heart-intraday']['dataset']
            for entry in intraday_data:
                time = entry['time']
                value = entry['value']
                csv_data.append([user_id, date, time, value])

        
        self.createDirectory(csv_filename)

        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_headers)
            writer.writerows(csv_data)


    """
        Gets HeartRate data from FitBit API.

        Parameters:
        -detail_level (str) : 1min
        -start_time (str) : Normally 00:00
        -end_time (str) : Normally 23:59
        -dates (list) : List of dates where HeartRate data will be fetch e.g [2024-07-01,2024-07-02...etc]
    
    """    
    def getHeartRateData(self, detail_level, start_time, end_time, dates, access_token, user_id):

        base_url = f"https://api.fitbit.com/1/user/{user_id}/activities/heart/date/"
        all_heart_data =  self.fetchData(base_url, detail_level, start_time, end_time, dates, access_token)
        
        self.store_HeartRate_csv(all_heart_data,
                                 csv_filename=f"app/DataAPI/{user_id}/heart_rate_data_{datetime.today().month}.csv" ,
                                 csv_headers= ['Id', 'Date', 'Time', 'HeartRate'], user_id=user_id)
        
    """
        Stores all csv Calories, Distance, Steps into a single csv

        Parameters:
        -source (str) : could be [Distance, Steps, Calories], stands for the elected csv source_filename.
        -source_data (json) : [Distance, Steps, Calories] CSV data.
        -csv_headers (list) : all headers of the resulted CSV.
    """  
    def store_CaloriesDistanceSteps_csv(self,source, source_data,user_id):
        csv_data = []
        for data in source_data:
                activities_key = f"activities-{source}"
                if activities_key in data:
                    date = data[activities_key][0]['dateTime']
                    intraday_key = f"{activities_key}-intraday"
                    if intraday_key in data:  
                        intraday_data = data[intraday_key]['dataset']
                        for entry in intraday_data:
                            time = entry['time']
                            value = entry['value']
                            csv_data.append([user_id, date, time, value])

        csv_file_path = f"app/DataAPI/{user_id}/{source}_data_{datetime.today().month}.csv"

        self.createDirectory(csv_file_path)
           

        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Id', 'Date', 'Time', source.capitalize()])
            writer.writerows(csv_data)
 


    """
        Creates specified 'output_filename' directory if not exists.

    """
    def createDirectory(self, output_filename):
        directory = os.path.dirname(output_filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

    """
        Fetch Calories, Distance, Steps Data from fitbit API and stores it into user_logged API data folder.

        Parameters:
        -detail_level (str) : 1min
        -start_time (str) : Normally 00:00
        -end_time (str) : Normally 23:59
        -dates (list) : List with the days where data will be fetch e.g [2024-07-01,2024-07-02...etc]
    
    """
    def getCaloriesDistanceStepsData(self, detail_level, start_time, end_time, dates,access_token, user_id):
        
        data_sources = ["calories", "distance", "steps"]

        for source in data_sources:
            base_url = f"https://api.fitbit.com/1/user/{user_id}/activities/{source}/date/"
            source_data = self.fetchData(base_url, detail_level, start_time, end_time, dates, access_token)

            self.store_CaloriesDistanceSteps_csv(source,source_data,user_id)
    """
        Get remainig request for user logged in.
        Maximun request per user per hour is 150.

        Returns:
        -Remaining request (int)
    """   
    def get_remaining_requests(self, access_token, user_id):

        url = f"https://api.fitbit.com/1/user/{user_id}/profile.json"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            rate_limit_remaining = response.headers.get('fitbit-rate-limit-remaining')
            return int(rate_limit_remaining) if rate_limit_remaining is not None else 0
        else:
            print(f"Error obteniendo el límite de peticiones: {response.status_code}")
            return 0

        