import sys
from Network_Security.Components.data_ingestion import DataIngestion
from Network_Security.Entity.config_entity import DataIngestionConfig, TrainingPipelineConfig
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging



if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        logging.info("Initiating data ingestion")
        data_ingestion_obj = DataIngestion(data_ingestion_config)
        file_paths = data_ingestion_obj.initiate_data_ingestion()
        logging.info("data ingestion completed")
        print(file_paths.test_file_path, file_paths.train_file_path)
        print(file_paths)
    except Exception as e:
        raise CustomException(e, sys)