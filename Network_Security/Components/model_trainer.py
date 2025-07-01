import os
import sys
import mlflow
from Network_Security.Entity.config_entity import ModelTrainerConfig
from Network_Security.Entity.artifact_entity import ClassificationMetricArtifact, ModelTrainerArtifact, DataTransformationArtifact
from Network_Security.Utils.main_utils.utils import save_numpy_array, load_numpy_array, save_object, load_object, evaluate_models
from Network_Security.Exception.CustomException import CustomException
from Network_Security.Logging.logger import logging
from Network_Security.Utils.ml_utils.metric.classification_metric import get_classification_score
from Network_Security.Utils.ml_utils.model.estimator import NetworkModel
from sklearn.metrics import r2_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier


class ModelTrainer:
    def __init__(self, data_transformation_artifact: DataTransformationArtifact, model_trainer_config: ModelTrainerConfig):
        try:
            self.data_transformation_artifact = data_transformation_artifact
            self.model_trainer_config = model_trainer_config
        except Exception as e:
            raise CustomException(e, sys)
        
    def track_mlflow(self, best_model, classification_metric):
        with mlflow.start_run():
            f1_score = classification_metric.f1_score
            precision_score = classification_metric.precision_score
            recall_score = classification_metric.recall_score

            mlflow.log_metric("fl_score", f1_score)
            mlflow.log_metric("recall_score", recall_score)
            mlflow.log_metric("precision_score", precision_score)
            mlflow.sklearn.log_model(best_model,"best_model")
            

    def train_model(self, X_train, y_train, X_test, y_test):
        models = {
            "Decision Tree": DecisionTreeClassifier(),
            "Random Forest": RandomForestClassifier(verbose=1),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier(),
            # "KNeighbors": KNeighborsClassifier()
        }
        params = {
            "Decision Tree":{
                'criterion': ['gini', 'entorpy', 'log_loss'],
                # 'splitter': ['best', 'random'],
                # 'max_features': ['sqrt', 'log2']
            },
            "Random Forest":{
                # 'max_features': ['sqrt', 'log2']
                # 'criterion': ['gini', 'entorpy', 'log_loss'],
                'n_estimators':[8,16,32,64,128,256]
            },
            "Gradient Boosting":{
                # 'loss': ['log_loss','exponential'],
                'criterion':['squared_error','friedman_mse'],
                'learning_rate': [0.1,0.01,0.05,0.001],
                'subsample': [0.6,0.7,0.75,0.8,0.85,0.9],
                'max_features':['auto','sqrt','log'],
                'n_estimators':[8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'n_estimators':[8,16,32,64,128,256],
                'learning_rate': [0.1,0.01,0.05,0.001]
            }
        }
        model_report: dict = evaluate_models(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, models=models, params=params)
        
        #to get the best model score
        best_score = max(sorted(model_report.values()))
        #to get the best model name
        best_model_name = list(model_report.keys())[list(model_report.values()).index(best_score)]
        best_model = models[best_model_name]

        y_train_pred = best_model.predict(X_train)
        classification_train_metric: ClassificationMetricArtifact = get_classification_score(y_true=y_train, y_pred=y_train_pred)

        # Track the mlflow
        self.track_mlflow(best_model, classification_train_metric)

        y_test_pred = best_model.predict(X_test)
        classification_test_metric: ClassificationMetricArtifact = get_classification_score(y_true=y_test, y_pred=y_test_pred)

        self.track_mlflow(best_model, classification_test_metric)

        preprocessor = load_object(self.data_transformation_artifact.transformed_object_file_path)
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)
        network_model = NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path, network_model)

        #model trainer artifact
        model_trainer_artifact = ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path, train_metric_artifact=classification_train_metric, test_metric_artifact=classification_test_metric)
        return model_trainer_artifact

    def initate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #laoding training and testing numpy arrays
            train_arr = load_numpy_array(train_file_path)
            test_arr = load_numpy_array(test_file_path)
            
            #splitting the data
            X_train, X_test, y_train, y_test = (train_arr[:,:-1], test_arr[:,:-1], train_arr[:,-1], test_arr[:,-1])

            model_trainer_artifact: ModelTrainerArtifact = self.train_model(X_train, y_train, X_test, y_test)
            return model_trainer_artifact
        except Exception as e:
            raise CustomException(e, sys)
