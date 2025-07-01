from Network_Security.Constants.training_pipeline import MODEL_FILE_NAME, SAVED_MODEL_DIR
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging
import os, sys

class NetworkModel:
    """ Making prediction for the new data after training the model. """
    def __init__(self, preprocessor, model):
        try:
            self.preprocessor = preprocessor
            self.model = model
        except Exception as e:
            raise CustomException(e, sys)
    
    def predict(self, x):
        try:
            x_transformed = self.preprocessor.transform(x)
            y_hat = self.model.predict(x_transformed)
            return y_hat
        except Exception as e:
            raise CustomException(e, sys)
