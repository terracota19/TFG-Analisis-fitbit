from xgboost import XGBRegressor
from app.models.ML.BaseForecaster import BaseForecaster

class XGBoost(BaseForecaster) :

    def __init__(self):
        self.model = XGBRegressor(random_state = 123)
        super().__init__(self.model)
       