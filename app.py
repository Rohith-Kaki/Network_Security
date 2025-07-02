import os, sys
import certifi
import pymongo
import uvicorn
import pandas as pd 
from dotenv import load_dotenv
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging
from Network_Security.Utils.ml_utils.model.estimator import NetworkModel
from Network_Security.Pipeline.training_pipeline import TrainingPipeline
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import Response
from starlette.responses import RedirectResponse
from Network_Security.Utils.main_utils.utils import load_object
from Network_Security.Constants.training_pipeline import DATA_INGESTION_DATABASE_NAME, DATA_INGESTION_COLLECTION_NAME


ca = certifi.where()
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
print(mongo_db_url)
client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True, 
    allow_methods = ["*"],
    allow_headers = ["*"]
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory = "./templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url='/docs')

@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise CustomException(e, sys)
    
@app.post("/predict")
def predict(request:Request, file:UploadFile=File(...)):
    try:
        df = pd.read_csv(file.file)
        preprocessor = load_object('final_model\preprocessor.pkl')
        model = load_object('final_model\model.pkl')    
        network_model = NetworkModel(preprocessor=preprocessor, model=model)
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse("table.html", {"request":request, "table":table_html})
    except Exception as e:
        raise CustomException(e, sys)
    
if __name__ == "__main__":
    uvicorn.run(app, host= "localhost", port = 8000)