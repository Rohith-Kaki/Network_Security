import sys
from Network_Security.Components.data_ingestion import DataIngestion
from Network_Security.Components.data_validation import DataValidation
from Network_Security.Components.data_transformation import DataTransformation
from Network_Security.Entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig, DataTransformationConfig
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging



if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        logging.info("Initiating data ingestion")
        data_ingestion_obj = DataIngestion(data_ingestion_config)
        data_ingestion_artifact = data_ingestion_obj.initiate_data_ingestion()
        logging.info("data ingestion completed")
        print(data_ingestion_artifact.test_file_path, data_ingestion_artifact.train_file_path)
        print(data_ingestion_artifact)

        logging.info("Started data validation")
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation_obj = DataValidation(data_ingestion_artifact, data_validation_config)
        data_validation_artifact = data_validation_obj.initiate_data_validation()
        print(data_validation_artifact)
        logging.info("Data validation completed")

        logging.info("started data transformation")
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        data_transformation_obj = DataTransformation(data_validation_artifact, data_transformation_config)
        data_transformation_artifact = data_transformation_obj.initate_data_transformation()
        print(data_transformation_artifact)
        logging.info("Data transformation completed")
    except Exception as e:
        raise CustomException(e, sys)