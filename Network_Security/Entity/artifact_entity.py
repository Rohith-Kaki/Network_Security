from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    train_file_path: str
    test_file_path: str

# class DataIngestionArtifact:
#     def __init__(self, train_file_path: str, test_file_path: str):
#         self.train_file_path = train_file_path
#         self.test_file_path = test_file_path

# It’s used to create lightweight "classes" that mainly store "data".
# these both mean the same @dataclass is a decorator that helps you to skip this code.


@dataclass
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str

@dataclass
class DataTransformationArtifact:
    transformed_object_file_path: str
    transformed_test_file_path: str
    transformed_train_file_path: str

@dataclass
class ClassificationMetricArtifact:
    f1_score: float
    precision_score: float
    recall_score: float
    
@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    train_metric_artifact: ClassificationMetricArtifact
    test_metric_artifact: ClassificationMetricArtifact