from app.models.ML.XGBoost import XGBoost
from app.models.ML.LightGBM import LightGBM
from datetime import datetime, timedelta, timezone
from app.models.FitBit.FitBitAuth import FitBitAuth
from app.models.FitBit.FitBitDataHandler import FitBitDataHandler

class FitbitAPI:
    def __init__(self, client_id, client_secret, mongo):
        
        """Fitbit Information"""
        self.client_id = client_id
        self.client_secret = client_secret

        self.auth = FitBitAuth(client_id, client_secret)
        self.dataHandler = FitBitDataHandler()

        """MongoDB"""
        self.mongo = mongo

        """Dynamic User Information""" 
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.expires_in = None
        self.expires_at = None
        
        """URL for OAuthClient with Fitbit"""
        self.authentification_url = self.generate_authorization_url()


        """XGBoost"""
        self.boost = XGBoost()


        """LightGBM ML model"""
        self.light = LightGBM()
        

    """
        Predict with XGBoost model

        Returns:
        - list : Predictions by ML XGBoost for every minuted selected by user.
    
    """
    def predictions(self):
        return self.boost.predictions()
    
    
    """
        Getter previous real HeartRate data before user predicting.

        Returns:
        - list : A list with user HeartRate data before predicting.
    """
    def datosReales(self):
        return self.boost.datosReales()

    """
        Obtains last minute available from user fitbit data

        Returns
        -last (datetime): last minute of user data retrieved from Fitbit
    """
    def lastUpdate(self):
        return self.dataHandler.lastUpdate(user_id=self.user_id)
    
    """
        Deletes all contents/data related to recent deleted user.
    """
    def deleteUserFitBitData(self):
        return self.dataHandler.deleteUserFitBitData(self.user_id)

    """
        Store FitBit info access, refresh tokens and other info
    
    """
    def storeFibitInfo(self, new_access_token, new_refresh_token, new_expires_in, user_id):
        
        self.access_token = new_access_token
        self.refresh_token = new_refresh_token
        self.user_id = user_id

        self.setExpiresIn(new_expires_in)
        self.storeMongoTokens(self.access_token, self.refresh_token, self.expires_in, self.user_id)

    """
        Method to copy new expires_in value from new access,refresh tokens
    """
    def setExpiresIn(self, new_expires_in):
        if isinstance(new_expires_in, datetime):
            self.expires_in = new_expires_in
        else:
            self.expires_in = datetime.now(timezone.utc) + timedelta(seconds=int(new_expires_in))

    """
        Combines all 'base_filename' existing csv`s from January to December into one csv 
    """    
    def combine_monthly_data(self, base_filename, output_filename):
       return self.dataHandler.combine_monthly_data(base_filename, output_filename, self.user_id)

    def access_token_is_expired(self, access_token, expires_in):
        return self.auth.access_token_is_expired(access_token, expires_in)

    """
        Combines all calories,distance, heartRate, steps merged csv into final csv 'test_train_data_api_merged.csv'
    """
    def dataPreprocess(self):
        return self.dataHandler.dataPreprocess(self.user_id)
       

    """
        Converts [`Time'] from test_train_data_api_merged['Time'] & test_train_data_api_merged['Date'] into DateTime 

        Returns:
        - csv : Converted data['Time'] & data['Date'] into one DateTime column data['Time].
    """
    def dateParser(self, datos_combinados_final):
        return self.dataHandler.dateParser(datos_combinados_final)


    """
        Prepares data for model prediction requirements, such as non-Nan values on dataset
        and train XGboost model.
        
    """
    def perfectDataForPrediction(self,steps):  
       datos_train, future_exog = self.dataHandler.perfectDataForPrediction(steps, self.user_id)
       self.boost.fit(datos_train, future_exog, steps)
   
    """
        Checks whether token is expirede and needed ReAuth from client

        Parameters:
        -access_token (str) : Contains the user last access token.
        -expires_in (datetime) : Contains in DateTime object when the access_token expires at.
        
        Returns:
        -(boolean) : if access token is expired or not.
    """
    def access_token_is_expired(self, access_token, expires_in):   
        return self.auth.access_token_is_expired(access_token, expires_in)
        
    """
        Checks whether token is expirede and needed ReAuth from client
        
        Parameters:
        -fitObject : (Object) Contains FitBit User Data such as, access_token, refresh token, and expires_in value.

        Returns:
        - (boolean) : Indicated whether access_token is expired or not.

    """  
    def checkRefreshToken(self,fitObject):
         return self.access_token_is_expired(fitObject.get("access_token"), fitObject.get("expires_in"))
           
    """
        Stores Fitbit Tokens and other info onto MongoDB user account
    """
    def storeMongoTokens(self, access_token, refresh_token, expires_in, user_id):
        
        self.mongo.update_data("usuarios", query = {"fitbit.user_id" : user_id}, field="fitbit.access_token", value=access_token)
        self.mongo.update_data("usuarios", query = {"fitbit.user_id" : user_id}, field="fitbit.refresh_token", value=refresh_token)
        self.mongo.update_data("usuarios", query = {"fitbit.user_id" : user_id} , field="fitbit.expires_in", value=expires_in)
        
    """
        Simple Getter for User Profile from FitBit API

        Returns:
        - (json) : Returns a json with all user profile data given by FitBit API.
    """
    def getUserProfile(self):
       return self.dataHandler.getUserProfile(self.access_token)


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
    def fetchData(self, base_url, detail_level, start_time, end_time, dates):
      return self.dataHandler.fetchData(base_url, detail_level, start_time, end_time, dates, self.access_token)
    
    """
        Stores HeartRate data into a csv.

        Parameters:
        -data (json) : Json file with HeartRate data
        -csv_filename (str) : The filename where data will be stored
        -csv_headers (list) : list with csv Headers e.g. HeartRate, user_id ... etc
    
    """
    def store_HeartRate_csv(self, data, csv_filename, csv_headers):
       return self.dataHandler.store_HeartRate_csv( data, csv_filename, csv_headers, self.user_id)

    """
        Gets HeartRate data from FitBit API.

        Parameters:
        -detail_level (str) : 1min
        -start_time (str) : Normally 00:00
        -end_time (str) : Normally 23:59
        -dates (list) : List of dates where HeartRate data will be fetch e.g [2024-07-01,2024-07-02...etc]
    
    """    
    
    def getHeartRateData(self, detail_level, start_time, end_time, dates):
        return self.dataHandler.getHeartRateData(detail_level, start_time, end_time, dates, self.access_token, self.user_id)
      
    """
        Stores all csv Calories, Distance, Steps into a single csv

        Parameters:
        -source (str) : could be [Distance, Steps, Calories], stands for the elected csv source_filename.
        -source_data (json) : [Distance, Steps, Calories] CSV data.
        -csv_headers (list) : all headers of the resulted CSV.
    """  
   
    def store_CaloriesDistanceSteps_csv(self,source, source_data, csv_filename, csv_headers):
       return self.dataHandler.store_CaloriesDistanceSteps_csv(source, source_data, self.user_id)      
    
    """
        Fetch Calories, Distance, Steps Data from fitbit API and stores it into user_logged API data folder.

        Parameters:
        -detail_level (str) : 1min
        -start_time (str) : Normally 00:00
        -end_time (str) : Normally 23:59
        -dates (list) : List with the days where data will be fetch e.g [2024-07-01,2024-07-02...etc]
    
    """
    def getCaloriesDistanceStepsData(self, detail_level, start_time, end_time, dates):
       return self.dataHandler.getCaloriesDistanceStepsData(detail_level, start_time, end_time, dates, self.access_token, self.user_id)
    
    """
        Get remainig request for user logged in.
        Maximun request per user per hour is 150.

        Returns:
        -Remaining request (int)
    """   
    def get_remaining_requests(self):
        return self.dataHandler.get_remaining_requests(self.access_token, self.user_id)
     
    """
        Generated code verifier using base64 to encoded it.

        Returns:
            code_verifier (str) : Used for OAuth2.0 with FitBit API.
    """
    def generate_code_verifier(self, length=64):
        return self.auth.generate_code_challenge()

    """
        Generates Code challenge using sha256 and base 64.

        Returns:
            code_challenge (str) : Used for OAuth2.0 with FitBit API.
    """
    def generate_code_challenge(self):
       return self.auth.generate_code_challenge()


    """
        Generates Authentification URL for user to accept terms.

        Returns:
            URL (str) : Genetated URL.
    """
    def generate_authorization_url(self, redirect_uri='http://localhost:5000', scopes=None):
       return self.auth.generate_authorization_url( redirect_uri='http://localhost:5000', scopes=None)


    """
        Getter for user logged in access token and stores it on MongoDB user account.

        Parameters:
        -code (str) : Code generated by Fitbit API in response of succesful Authentification process.
        state (str) : State generated by Fitbit API in response of succesful Authentification process.

        Returns:
        -response_data["access_token"] (str) : Access token used for fetching data.
        -response_data["refresh_token"] (str) : Refresh Token in case of ReAuth needed.
        -response_data["user_id"] (str) : Fitbit User id that identifies it.

    """
    def get_access_token(self, code, state, redirect_uri="http://localhost:5000"):
        return self.auth.get_access_token( code, state, redirect_uri="http://localhost:5000")

    """
        Refresh access token in case of ReAuth needed.

        Parameters:
        -refresh_token (str) : Refresh Token used to get new access_tokens and new refresh_tokens.

        Returns:
        -response_data["access_token"] (str) : Access_token for fetch data.
        -response_data["refresh_token"] (str) : Refresh Token for getting new access_tokens
        -response_data["expires_in"] (DateTime) : Expires in.
        -response_data["user_id"] (str) : FitBit User id 
        -boolean : Returns whether user needs to ReAuth Again because access_token expired.

    """
    def refresh_access_token(self, refresh_token):
        access_token, refresh_tk, expires_in, user_id, reAuth = self.auth.refresh_access_token(refresh_token)

        if reAuth == False :
            self.access_token = access_token
            self.refresh_token = refresh_tk
            expires_in =  expires_in
            self.user_id = user_id

       
       











