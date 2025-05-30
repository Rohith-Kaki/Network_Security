## setup.py is used to define the configuratio of the project, such as metadata, dependencies, and more....

from setuptools import find_packages, setup
from typing import List

def get_requirements() -> List[str]:
    requirements_lst: List[str] = []
    try:
        with open("requirements.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                # exclude empty line and -e .
                if line and line != "-e .":
                    requirements_lst.append(line)
    except FileNotFoundError:
        print("requirements.txt file not found")
    return requirements_lst

setup(
    name= "Network_Security",
    version="0.0.1",
    author="Rohith",
    author_email="rohithkaki11@gmail.com",
    packages=find_packages(),
    install_requires = get_requirements()
)