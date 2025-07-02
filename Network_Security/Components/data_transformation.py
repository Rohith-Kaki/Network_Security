from Network_Security.Constants.training_pipeline import TARGET_COLUMN, DATA_TRANSFORMATION_IMPUTER_PARAMS
from Network_Security.Entity.config_entity import DataTransformationConfig
from Network_Security.Entity.artifact_entity import DataValidationArtifact, DataTransformationArtifact
from Network_Security.Utils.main_utils.utils import save_numpy_array, save_object
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging
from sklearn.pipeline import Pipeline
from sklearn.impute import KNNImputer
import numpy as np
import pandas as pd
import sys, os

class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
        except Exception as e:
            raise CustomException(e, sys)
        

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CustomException(e, sys)
    
    def get_data_transformer_obj(cls) -> Pipeline:
        logging.info("Entered get_data_transformer_obj in DataTransformation Class")
        try:
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"Initialized an KNN imputer with params {DATA_TRANSFORMATION_IMPUTER_PARAMS}")
            processor = Pipeline(
                [
                    ("imputer", imputer)
                ]
            )
            return processor
        except Exception as e:
            raise CustomException(e, sys)
        
    def initate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Entered initate data transformation step")
        try:
            logging.info("Started initate data transformation step")
            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)

            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1, 0)

            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1,0)

            processor = self.get_data_transformer_obj()
            transformed_input_train_feature = processor.fit_transform(input_feature_train_df)
            transformed_input_test_feature = processor.transform(input_feature_test_df)

            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            save_numpy_array(self.data_transformation_config.transformed_train_file_path, train_arr)
            save_numpy_array(self.data_transformation_config.transformed_test_file_path, test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path, processor)
            save_object('final_model/preprocessor.pkl', processor)

            data_transformation_artifact = DataTransformationArtifact(transformed_object_file_path=self.data_transformation_config.transformed_object_file_path, transformed_test_file_path=self.data_transformation_config.transformed_test_file_path, transformed_train_file_path=self.data_transformation_config.transformed_train_file_path)
            return data_transformation_artifact
        except Exception as e:
            raise CustomException(e, sys)