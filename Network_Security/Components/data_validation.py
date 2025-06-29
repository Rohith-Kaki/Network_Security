from Network_Security.Entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from Network_Security.Entity.config_entity import DataValidationConfig
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Constants.training_pipeline import SCHEMA_FILE_PATH
from Network_Security.Utils.main_utils.utils import read_yaml_file, write_yaml_file
from Network_Security.Logging.logger import logging
from scipy.stats import ks_2samp
import pandas as pd
import sys
import os


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config: dict = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise CustomException(e, sys)
        
    @staticmethod
    def read_data(file_path:str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CustomException(e, sys)
        
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        no_of_columns = len(self._schema_config)
        logging.info(f'Number of columns required {no_of_columns}')
        logging.info(f'Number of columns in dataframe: {len(dataframe.columns)}')
        if len(dataframe.columns) == no_of_columns:
            return True
        return False
    def validate_numerical_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            no_of_numerical_columns = len(self._schema_config)
            numerical_columns_dataframe = len([column for column in dataframe.columns if dataframe[column].dtype!='O'])
            logging.info(f"Requried no of numerical columns: {no_of_numerical_columns}")
            logging.info(f"No of numerical columns in dataframe: {numerical_columns_dataframe}")
            if numerical_columns_dataframe == no_of_numerical_columns:
                return True
            return False
        except Exception as e:
            raise CustomException(e, sys)
    
    def detect_data_drift(self, base_df, current_df, threshold = 0.05) ->bool:
        try:    
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1,d2)
                if threshold <= is_same_dist.pvalue:
                    drift_found = False
                else:
                    drift_found = True
                    status = False # atleast one column is drifted
                report.update(
                    {
                        column:{
                            'p_value':float(is_same_dist.pvalue),
                            'drift_stauts': drift_found
                        }
                    }
                )
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(drift_report_file_path, content=report)
            return status
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_validation(self)-> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            #read the data from the file paths
            train_dataframe = self.read_data(train_file_path)
            test_dataframe = self.read_data(test_file_path)

            # validate no of columns
            train_status = self.validate_number_of_columns(train_dataframe)
            if not train_status:
                error_message = f"Train data doesn't contain all columns.\n"
            test_status = self.validate_number_of_columns(test_dataframe)
            if not test_status:
                error_message = f"Test data doesn't contain all columns.\n"

            #validate no of numerical columns
            train_status = self.validate_numerical_columns(train_dataframe)
            if not train_status:
                error_message = "Train data doesn't contain all numerical columns.\n"
            test_status = self.validate_numerical_columns(test_dataframe)
            if not test_status:
                error_message = "Test data doesn't contain all numerical columns.\n"
            
            #data drift check
            status = self.detect_data_drift(base_df=train_dataframe, current_df=test_dataframe)
            if status:
                os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)
                train_dataframe.to_csv(
                    self.data_validation_config.valid_train_file_path, index=False, header=True
                )
                test_dataframe.to_csv(
                    self.data_validation_config.valid_test_file_path, index=False, header=True
                )
            else:
                os.makedirs(os.path.dirname(self.data_validation_config.invalid_train_file_path), exist_ok=True)
                train_dataframe.to_csv(
                    self.data_validation_config.invalid_train_file_path, index=False, header=True
                )
                test_dataframe.to_csv(
                    self.data_validation_config.invalid_test_file_path, index=False, header=True
                ) 
            data_validation_artifact =  DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.train_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            return data_validation_artifact

        except Exception as e:
            raise CustomException(e, sys)



