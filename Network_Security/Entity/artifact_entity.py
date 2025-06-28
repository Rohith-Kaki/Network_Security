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