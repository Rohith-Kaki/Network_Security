import os
import sys
import pymongo
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from typing import List
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging
#configuration of the data ingestion config
from Network_Security.Entity.config_entity import DataIngestionConfig
from Network_Security.Entity.artifact_entity import DataIngestionArtifact
from dotenv import load_dotenv
load_dotenv()

MONG_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise CustomException(e, sys)
        
    def collection_to_dataframe(self):
        """
        Read Data from mongodb and convert it into a DataFrame
        """
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONG_DB_URL)
            collection = self.mongo_client[database_name][collection_name]
            df = pd.DataFrame(list(collection.find()))
            # by default a column will be added we are removing that column
            if "_id" in df.columns.to_list():
                df.drop(columns=["_id"], inplace=True)
            df.replace({"na":np.nan}, inplace=True)
            return df
        except Exception as e:
            raise CustomException(e, sys)
        
        
    def export_data_into_feature_store(self,dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe
        except Exception as e:
            raise CustomException(e, sys)
    
    def export_data_into_ingested(self, dataframe: pd.DataFrame):
        # Ingested folder will contain the training and the testing data
        try:
            train_set, test_set = train_test_split(dataframe, test_size=self.data_ingestion_config.train_test_ratio, random_state=42)
            logging.info("Perfomed train test split on the dataframe")
        
            dir_path = os.path.dirname(self.data_ingestion_config.testing_file_path)
            os.makedirs(dir_path, exist_ok=True)

            logging.info("Exporting train and test data")
            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)            
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)            
            logging.info("Exported train and test data to file path")

        except Exception as e:
            raise CustomException(e, sys)
        
    def initiate_data_ingestion(self):
        try:
            dataframe = self.collection_to_dataframe()
            dataframe = self.export_data_into_feature_store(dataframe)
            self.export_data_into_ingested(dataframe)
            # return self.data_ingestion_config.testing_file_path, self.data_ingestion_config.training_file_path
            #you can do this too but, in production level we do as below.Below are drawbacks of above code
            # the calling fuction should know which is test and train _,_ = function()
            # Instead of doing this "result[0]" we can do this ->"data_ingestion_artifact.test_file_path" more better than using tuples
            #In production level pipelines (like ML, ETL, etc.), every stage often returns an artifact object.
            data_ingestion_artifact =  DataIngestionArtifact(train_file_path=self.data_ingestion_config.training_file_path, test_file_path = self.data_ingestion_config.testing_file_path)
            return data_ingestion_artifact
        except Exception as e:
            raise CustomException(e, sys)