
import numpy as np
import skforecast
import lightgbm as lgb
from skforecast.ForecasterAutoreg import ForecasterAutoreg

class LightGBM :

    def __init__(self):

        "Forecaster Information"
        self.steps = None
        self.lags =  None
        self.datos_train = None
        self.future_exog = None
        

        """LightGBM Regressor ML model"""
        self.light = lgb.LGBMRegressor(objective='regression', random_state=123)
        
        """Forecaster AutoReg"""
        self.forecaster = None 
        
    def datosReales(self):
        return self.datos_train['HeartRate'][-self.steps:]
        
    """
        Predice en el futuro para dentro de "minutes" minutos
    """
    def predictions(self):
        return self.forecast()
    
    """
        Entrenamos el modelo con los datos de entrenamiento y variables exogenenas
    """
    
    def fitLight(self, datos_train, future_exog, steps):

        self.steps = steps
        # TODO LAG  mirar logica para seleccionar el lag
        self.lags = 7

        self.forecaster = ForecasterAutoreg(
            regressor = self.light,
            lags      = self.lags
        )
        
        self.datos_train = datos_train        
        self.future_exog = future_exog
        
        self.forecaster.fit(y=self.datos_train['HeartRate'], exog=self.datos_train[['Calories','Steps','Distance']])
       
    """
        Para predecir a x minutos en el futuro
    """
    def forecast(self):
        self.predicciones = self.forecaster.predict(steps=self.steps, exog=self.future_exog)
        return self.predicciones
