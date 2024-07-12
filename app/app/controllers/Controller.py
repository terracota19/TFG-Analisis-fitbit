import re
import os
import pymongo
import webbrowser
from flask import request
from dotenv import load_dotenv
from app.models.Mongo import Mongo
from app.utils.Hashing import HashSHA_256
from app.utils.OAuthServer import OAuthServer
from app.models.FitBit.Fitbit import FitbitAPI

#Exceptions
from app.exceptions.UserLogInError import UserLogInError
from app.exceptions.UserRegistrationError import UserRegistrationError
from app.exceptions.UserFitbitAccountAlreadyInUseError import UserFitbitAccountAlreadyInUseError

class Controller:
    def __init__(self, view):

        """Gui view"""
        self.view = view
        
        """MongoDB"""
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongo = Mongo("tfg_fitbit", self.mongo_client)
        
        """User info"""
        self.logged_in_user = None
        self.login_frame = None 
    
        """API Fitbit"""
        load_dotenv()

        juan_fitbit_client_id = os.getenv("JUAN_FITBIT_CLIENT_ID")
        juan_fitbit_client_secret = os.getenv("JUAN_FITBIT_CLIENT_SECRET")

        javi_fitbit_client_id = os.getenv("JAVI_FITBIT_CLIENT_ID")
        javi_fitbit_client_secret = os.getenv("JAVI_FITBIT_CLIENT_SECRET")

        #self.fitbitAPI = FitbitAPI(juan_fitbit_client_id, juan_fitbit_client_secret, self.mongo)
        self.fitbitAPI = FitbitAPI(javi_fitbit_client_id, javi_fitbit_client_secret, self.mongo)
    
        """OAuthServer""" 
        self.oauth_server = OAuthServer(self.fitbitAPI)
        
    """
        Logic that returns predictions made by ML model
    """
    def  predictions(self):
        return self.fitbitAPI.predictions()
    
    """
        Logic that validates whether user register email is correctly formatted example example@gmail.com
        
        Parameters:
        -email (str) : String that contains user register email.

        Returns:
        - (boolean) : True when is valid, example (example@gmal.com) . False otherwise.
    """
    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email)
        
    """
        Getter for real HeartRate data plotting.
    """
    def datosReales(self):
        return self.fitbitAPI.datosReales()

    """
        Logic for user acound erase
    """
    def deleteUserAccount(self):
        user_id = self.logged_in_user.get("_id")
        if user_id:
            self.fitbitAPI.deleteUserFitBitData()
            self.mongo.delete_data("usuarios", {"_id": user_id})

            self.view.create_login_frame() 
            self.view.heartpred_frame = self.view.app_frame
            self.view.heartpred_frame.destroy()

    """
        Validates whether input 's' s a String and non-empty string that contains at least non-whitespace character.

        Parameters:
        -s (str) : Input String

        Returns:
        (Boolean) : True : when input 's' s a String and non-empty string that contains at least non-whitespace character : False otherwise

    """
    def validate_string(self, s):
        return isinstance(s, str) and bool(s.strip())
    
    """
        Validates whether 'value' is a numeric instance

        Parameters:
        -value (int) : Input Integer.

        Returns:
        - (boolean) : True if  'value' is a numeric instance: False otherwise
    """
    def validate_numeric(self, value):
        return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
    
    """
        Logic for sanatizing any type of input string to evade XSS attacks

        Parameters:
        -input_string (str) : Input String to be sanatized.

        Returns:
        - (str) : The sanatized string without potentially harmaful caracters.

        Example:
        Non Sanatized : <script>alert('XSS');</script>
        Sanatized : scriptalert('XSS');/script".

    """
    def sanitize_input(self, input_string):
        return re.sub(r'[<>]', '', input_string)

    """
        Logic for user logOut from App.
    """
    def logout(self):
        self.logged_in_user = None

    """
        Logic that stores on MongoDB all user fitbit data.

        Parameters:
        -access_token (str) : Access token used for fetching user data.
        -refresh_token (str) : Refresh token used for refreshing new valid user access_tokens.
        -expires_in (Datetime) : Datetime indicating when user access_token expires.
        -user_id (str) : String that identifies fitbit user account. 
        
    """ 
    def storeMongoTokens(self, access_token, refresh_token, expires_in, user_id):
        
        self.mongo.update_data("usuarios", query = {"fitbit.user_id" : user_id}, field="fitbit.access_token", value=access_token)
        self.mongo.update_data("usuarios", query = {"fitbit.user_id" : user_id}, field="fitbit.refresh_token", value=refresh_token)
        self.mongo.update_data("usuarios", query = {"fitbit.user_id" : user_id} , field="fitbit.expires_in", value=expires_in)
        
    """
        Logic that updates user 'last_update' into MongoDB

        Parameters:
        -last_update (Datetime) : Input Datetime when user last syncronized with Fitbit.

    """
    def updateApiLastUpdate(self,last_update):
        
        if self.logged_in_user:
            user_id = self.logged_in_user.get("_id")
            if user_id:
                query = {"_id": user_id}
                self.mongo.update_data("usuarios", query, "ult_act" , last_update)        
                
    """
        Logic that stores User Fitbit Token info into Fitbit App instance and into MongoDB

        Parameters:
        -email (str) :  User email previously registered in HeartPred'It app.
        -user_id (str) : User Fitbit Id
        -new_access_token (str) : New valid access_token given by FitBit.
        -new_refresh_token (str) : New valid Refresh_token given by Fitbit
        -new_expires_in (Datetime) : New Datetime given by Fitbit, when new_access_token will expire.

        Returns:
        - (new_acess_token, new_refresh_token, new_expires_in )  (str, str, Datetime ) : Return all user fitbit tokens and expires date.   

    """
    def storeTokenInfo(self,email, user_id, new_access_token, new_refresh_token, new_expires_in):
        self.fitbitAPI.storeFibitInfo(new_access_token, new_refresh_token, new_expires_in,user_id)

        self.mongo.update_data("usuarios", query = {"correo" : email}, field="fitbit.access_token", value= new_access_token)
        self.mongo.update_data("usuarios", query = {"correo" : email}, field="fitbit.refresh_token", value= new_refresh_token)
        self.mongo.update_data("usuarios", query = {"correo" : email} , field="fitbit.expires_in", value= new_expires_in)
        
        return new_access_token, new_refresh_token, new_expires_in
        
    """
        Fetches user data identified with unique email from mongoDB and stores it into Fitbit instance.

        Parameters:
        -email (str) : User HeartPred'it email.
        
        Returns:
        - True if user data was not found.
    """
    def findTokenInfo(self, email):
        user_data = self.mongo.find_one_data("usuarios", query={"correo": email})

        if not user_data:
            return None, None, None, None, True

        fitbit_data = user_data.get("fitbit")
        if not fitbit_data:
            return None, None, None, None, True
        
        access_token = fitbit_data["access_token"]
        refresh_token = fitbit_data["refresh_token"]
        expires_in = fitbit_data["expires_in"]
        user_id = fitbit_data["user_id"]

        self.fitbitAPI.storeFibitInfo(access_token, refresh_token, expires_in,user_id)
           
    """
        Getter for User Token info from MongoDB, identified with Email

        Parameters:
        -email (str) : String that identifies user in MongoDB'users collection'
    """
    def getFitbitUserInfo(self, email):
        self.findTokenInfo(email)
        
    """
        Getter for last Fitbit Update/Syncronize

        Returns:
        -last Update syncronized with Fitbit.
    """
    def lastFitBitDataUpdate(self):
        return self.fitbitAPI.lastUpdate()
    
    """
        Getter for last update stored in MongoDB.
        Returns (Datetime/str) : Datetime if value stored in not null, "Nunca" otherwise.
    """
    def last_update(self) :
        ult_act = self.lastMongoUpdate()
        if ult_act:
            return ult_act
        else:
            return "Nunca"
       
    """
        Getter for user info.

        Returns
        -user info (json) : User info if user is currently logged, None Otherwise.
    """
    def user_info(self):
        if self.logged_in_user and "usuario" in self.logged_in_user:
            return self.logged_in_user["usuario"]
        else:
            return None
        
    """
        Validates whether password input from user is strong enough to surpass HeartPred'It requirements.

        Requirements:
            -Password length MUST be 8 or more characters:
            -Password MUST contain at least a Capital letter.
            -Password MUST contain at least a Non-Capital letter.
            -Password MUST contain at least a number.
            -Password MUST contain at least a Special character, example "@"

        Parameters:
        - password (str) : Secret User Password 
        
        Returns:
        - (boolean / Exception (UserRegistrationError)) : True if password input surpass all requirements : UserRegistrationError Otherwise.
    """
    def validate_pass_strength(self, password):
        
        if len(password) < 8:
            raise UserRegistrationError("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r"[A-Z]", password):
            raise UserRegistrationError("La contraseña debe contener al menos una letra mayúscula.")
        
        if not re.search(r"[a-z]", password):
            raise UserRegistrationError("La contraseña debe contener al menos una letra minúscula.")
        
        if not re.search(r"[0-9]", password):
            raise UserRegistrationError("La contraseña debe contener al menos un número.")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise UserRegistrationError("La contraseña debe contener al menos un carácter especial.")
        
        return True
    """
        User Register Logic.
        
        Parameters:
        -user (str) : User id .
        -email (str (unique) ) : User register email.
        -password (str) :  User register password.
        -edad (int) : User register age.

        Returns:
        - (boolean) True if MongoDB acknowledge = True. False Otherwise. 
    """
    def register(self, user, email, password, edad):

        if not (user and email and password and edad):
            raise UserRegistrationError("Upss...Todos los campos son obligatorios (*).")
        
        if not self.validate_numeric(edad):
            raise UserRegistrationError("La edad debe ser un valor numérico.")
        
        if not self.validate_email(email):
            raise UserRegistrationError("El formato del correo electrónico no es válido ej : (example@gmail.com).")
        
        if not self.validate_string(user):
            raise UserRegistrationError("El nombre de usuario no es válido.")
        
        self.validate_pass_strength(password)
        
        
        user = self.sanitize_input(user)
        email = self.sanitize_input(email)
        password = self.sanitize_input(password)
        edad = int(self.sanitize_input(edad))
    
        hashed_password, salt = HashSHA_256.hash_password(password)
        
        access_token, refresh_token , expires_in, user_id = self.fitbitAPI.getTokens()
        
        
        user_data = {
            "usuario": user,
            "password": hashed_password,
            "edad": edad,
            "salt": salt,
            "correo": email,
            "ult_act": None,
            "fitbit": {
                "user_id":  user_id,
                "access_token":  access_token,
                "refresh_token":  refresh_token,
                "expires_in":  expires_in
            }
        }
        
        return self.mongo.insert_data("usuarios", user_data)
    
    """
        Logic for user authorize with FitBit in register process.

        Parameters:
        -user (str) : User id .
        -email (str (unique) ) : User register email.
        -password (str) :  User register password.
        -edad (int) : User register age.

        Returns:
        - (boolean/ UserRegistrationError ) : False if any user input is empty : True Otherwise.  
       
    """
    def authorize_with_fitbit(self):
            webbrowser.open(self.fitbitAPI.authentification_url)
            return True
    """
        Last user 'ult_act' in MongoDB

        Returns:
        - (Datetime) : Last user 'ult_act' in MongoDB
    """
    def lastMongoUpdate(self):
        user_id = self.logged_in_user.get("_id")
        if user_id:
            query = {"_id": user_id}
            return self.mongo.find_one_data("usuarios", query).get("ult_act")
        else :
            return None
   
    """
        Checks whether user with email (unique) existe in MongoDB.

        Parameters:
        -email (str) : User Email.

        Returns:
        -True : if user with email = email exists. False Otherwise.
    """
    def checkIfUserExistsByEmail(self, email):
        user_data_by_email = self.mongo.find_one_data("usuarios", query={"correo": email})
        if user_data_by_email:
            return True
        else : return False

    """
        Logic that checks whether user need ReAuth OAuth2.0 process, because access_token expired.

        Parameters:
        - user_data (json) : User HeartPre'it data.
    """
    def checkReAuth(self, user_data):
        if self.fitbitAPI.checkRefreshToken(user_data.get("fitbit")):
            self.view.reauthorizationPopup()

    """
        Logic that checks whether User login input is correct,

        Parameters:
        -email (str (Unique)) : User login email.
        -password (str) : User secret login Password.


        Returns:
        - (UserLogInError) If user login data is empty, email format is incorrect, not valid password for user 'email'.
        - (True) : if user input is correct.

     """   
    def check_login(self, email, password):

        if not (email and password):
            raise UserLogInError("Upss...Todos los campos de inicio de sesión son obligatorios (*).")
        
        if not self.validate_email(email):
            raise UserLogInError("El formato del correo electrónico no es válido.")
        
        if not self.validate_string(password):
            raise UserLogInError("La contraseña no es válida.")
        
      
        email = self.sanitize_input(email)
        password = self.sanitize_input(password)
        
        user_data = self.mongo.find_one_data("usuarios", query={"correo": email})
        
        if user_data and user_data.get("correo") == email:
            
            self.checkReAuth(user_data)

            if HashSHA_256.verify_password(password, user_data["password"], user_data["salt"]):
                self.logged_in_user = user_data
                return True
            else:
                raise UserLogInError("¡Usuario no identificado!, chequea la contraseña")
        else:
            raise UserLogInError("¡Usuario no identificado!, chequea el campo correo")
    """
        Logic that stops Flask server when closed App.
    """
    def stop_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
        
