from sklearn.neural_network import MLPRegressor
from app.models.ML.BaseForecaster import BaseForecaster

class MLP (BaseForecaster):

    def __init__(self):
        self.model = MLPRegressor(random_state=123)
        super().__init__(self.model)
       