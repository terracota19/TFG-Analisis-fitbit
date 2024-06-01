
import numpy as np
import skforecast
import lightgbm as lgb
from skforecast.ForecasterAutoreg import ForecasterAutoreg


class LightGBM :


    def __init__(self, datos_train, datos_test):

        #Informacion para el forecaster
        self.steps = 5
        self.lags =  5 * self.steps
        self.datos_train = datos_train
        self.datos_test = datos_test
        self.minutes= None

        #modelo 
        self.light = lgb.LGBMRegressor(objective='regression', random_state=123)
        
        #forecaster
        self.forecaster = ForecasterAutoreg(
                regressor = self.light,
                lags      = self.lags
        )



    def predictions(self):
        if self.predicciones :
            return self.predicciones
        return 
    
    """
        Entrenamos el modelo con los datos de entrenamiento y variables exogenenas
    """
    def fitLight(self, datos_train, datos_test):
        
        self.datos_train = datos_train
        self.datos_test = datos_test

        self.forecaster.fit(y=self.datos_train['HeartRate'], exog=self.datos_train[['Calories','Steps','Distance']])

    """
        Para predecir a x minutos en el futuro
    """
    def forecast(self, minutes):
        #Entrenamos al modelo
        self.minutes = minutes

        self.predicciones = self.forecaster.predict(steps=self.steps,  exog=self.datos_test[['Calories', 'Steps', 'Distance']])
        return self.predicciones
