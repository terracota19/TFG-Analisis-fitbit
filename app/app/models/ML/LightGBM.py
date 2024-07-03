

import lightgbm as lgb
from app.models.ML.BaseForecaster import BaseForecaster

class LightGBM (BaseForecaster) :

    def __init__(self):
        self.model = lgb.LGBMRegressor(random_state=123)
        super().__init__(self.model)
      