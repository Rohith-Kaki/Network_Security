import pandas as pd
import numpy as np 
import os 
import sys

""" DEFINING COMMON CONSTANT VARIABLES FOR THE TRAINING PIPELINE"""
TARGET_COLUMN = "Result"
PIPELINE_NAME = "Network_Security"
ARTIFACT_DIR = "Artifacts"
FILE_NAME = "Website_Phishing.csv"
TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME = "test.csv"


""" DATA INGESTION CONSTANTS """
DATA_INGESTION_COLLECTION_NAME: str = "NetworkData" 
DATA_INGESTION_DATABASE_NAME: str = "Rohith"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2
