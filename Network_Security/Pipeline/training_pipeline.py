import os, sys
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging
from Network_Security.Components.data_ingestion import DataIngestion
from Network_Security.Components.data_transformation import DataTransformation
from Network_Security.Components.data_validation import DataValidation
from Network_Security.Components.model_trainer import ModelTrainer
from Network_Security.Constants.training_pipeline import TRAINING_BUCKET_NAME
from Network_Security.Cloud.s3_syncer import s3sync

from Network_Security.Entity.config_entity import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
from Network_Security.Entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact, DataValidationArtifact, ModelTrainerArtifact

class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
        self.s3_sync = s3sync()

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
    
    #uploading local artifact folder to s3
    def sync_artifact_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder= self.training_pipeline_config.artifact_dir, aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise CustomException(e, sys)
        
    # uploading local model folder to s3
    def sync_model_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/model/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder=self.training_pipeline_config.model_dir, aws_bucket_url=aws_bucket_url)
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

            self.sync_artifact_dir_to_s3()
            self.sync_model_to_s3()
            logging.info("local -> s3 Bucket")
            return self.model_training_artifact
        except Exception as e:
            raise CustomException(e, sys)