
import numpy as np
from skforecast.ForecasterAutoreg import ForecasterAutoreg

class BaseForecaster :

    def __init__(self, model):

        "Forecaster Information"
        self.steps = None
        self.lags =  None
        
        """Data """
        self.datos_train = None
        self.future_exog = None
        
        """ML model"""
        self.model = model
        
        """Forecaster AutoReg"""
        self.forecaster = None 
    
    """
        Getter for HearRate User Data.
    """
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
    def fitModel(self, datos_train, future_exog, data_pred_title, steps, best_lags):

        self.steps = steps
        self.lags = best_lags

        self.forecaster = ForecasterAutoreg(
            regressor = self.model,
            lags      = best_lags
        )
        
        self.datos_train = datos_train        
        self.future_exog = future_exog
            
        self.forecaster.fit(y=self.datos_train[data_pred_title], exog=self.getExogVariables(data_pred_title))
       
    """
        Obtiene las columnas menos el valor a predecir (data_title)
    """
    def getExogVariables(self, data_title):
        return self.datos_train.drop(columns=[data_title, 'Id'])
    
    
    """
        Para predecir a x minutos en el futuro
    """
    def forecast(self):
        
        self.predicciones = self.forecaster.predict(steps=self.steps, exog=self.future_exog)
        result = np.floor(self.predicciones * 100) / 100
        return np.maximum(result, 0)
