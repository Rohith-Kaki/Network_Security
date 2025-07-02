import os, sys
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging
from Network_Security.Components.data_ingestion import DataIngestion
from Network_Security.Components.data_transformation import DataTransformation
from Network_Security.Components.data_validation import DataValidation
from Network_Security.Components.model_trainer import ModelTrainer

from Network_Security.Entity.config_entity import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
from Network_Security.Entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact, DataValidationArtifact, ModelTrainerArtifact

class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()

    def start_data_ingestion(self):
        try:
            self.data_ingestion_config = DataIngestionConfig(self.training_pipeline_config)
            logging.info("data ingestion started")
            self.data_ingestion_component = DataIngestion(self.data_ingestion_config)
            self.data_ingestion_artifact: DataIngestionArtifact = self.data_ingestion_component.initiate_data_ingestion()
            logging.info(f"data ingestion completed and artifact: {self.data_ingestion_artifact}")
        except Exception as e:
            raise CustomException(e, sys)
        
    def start_data_validation(self):
        try:
            self.data_validation_config = DataValidationConfig(self.training_pipeline_config)
            logging.info("data validation started")
            self.data_validation_component = DataValidation(self.data_ingestion_artifact, self.data_validation_config)
            self.data_validation_artifact: DataValidationArtifact = self.data_validation_component.initiate_data_validation()
            logging.info(f"data validation completed and artifact: {self.data_validation_artifact}")
        except Exception as e:
            raise CustomException(e, sys)
    
    def start_data_transformation(self):
        try:
            self.data_transformation_config = DataTransformationConfig(self.training_pipeline_config)
            logging.info("data transformation started")
            self.data_transformation_component = DataTransformation(self.data_validation_artifact, self.data_transformation_config)
            self.data_transformation_artifact: DataTransformationArtifact = self.data_transformation_component.initate_data_transformation()
            logging.info(f"data transformation completed and artifact: {self.data_transformation_artifact}")
        except Exception as e:
            raise CustomException(e, sys)
        
    def start_model_training(self):
        try:
            logging.info("started model training")
            self.model_training_config =  ModelTrainerConfig(self.training_pipeline_config)
            self.model_training_component = ModelTrainer(self.data_transformation_artifact, self.model_training_config)
            self.model_training_artifact: ModelTrainerArtifact = self.model_training_component.initate_model_trainer()
            logging.info("completed model training")
        except Exception as e:
            raise CustomException(e, sys)
        
    def run_pipeline(self) -> ModelTrainerArtifact:
        try:
            logging.info("Started pipeline")
            self.start_data_ingestion()
            self.start_data_validation()
            self.start_data_transformation()
            self.start_model_training()
            logging.info("successfully executed the pipeline")
            return self.model_training_artifact
        except Exception as e:
            raise CustomException(e, sys)