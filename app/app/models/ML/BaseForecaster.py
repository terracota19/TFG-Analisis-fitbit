
from skforecast.ForecasterAutoreg import ForecasterAutoreg

class BaseForecaster :

    def __init__(self, model):

        "Forecaster Information"
        self.steps = None
        self.lags =  None

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
    
    def fit(self, datos_train, future_exog, steps):

        self.steps = steps
        # TODO LAG  mirar logica para seleccionar el lag
        self.lags = 7

        self.forecaster = ForecasterAutoreg(
            regressor = self.model,
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
