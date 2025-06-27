import os 
import sys
from dotenv import load_dotenv
import certifi
import pandas as pd
import numpy as np
import json
import pymongo
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
ca = certifi.where()

class NetworkDataExtract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise CustomException(e,sys)
    def csv_to_json(self, file_path:str):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise CustomException(e,sys)
    def insert_data_to_mongodb(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)
            return len(self.records)
        except Exception as e:
            raise CustomException(e, sys)
if __name__ == "__main__":
    file_path = "Network_Data\Website Phishing.csv"
    extract = NetworkDataExtract()
    records = extract.csv_to_json(file_path)
    print(records)
    len_records = extract.insert_data_to_mongodb(records, "Rohith", "NetworkData")
    print(len_records)