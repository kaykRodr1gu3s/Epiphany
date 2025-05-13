import dotenv
import logging
import os
from pathlib import Path
from elasticsearch import Elasticsearch
from logging.handlers import RotatingFileHandler



class test:
    def __init__(self):
        self.client = Elasticsearch(cloud_id=os.getenv("cloud_id"), api_key=os.getenv("elasticsearch_apikey"))

    def setup_log():
        # log_path = 
        pass

    @property
    def searcher(self):
        print(self.client.search(index="test2"))



if __name__ == "__maain__":
    dotenv.load_dotenv()
    elastic_integration = test()
    elastic_integration.searcher

# __file__ c:\Users\kaykc\Documents\GitHub\Epiphany\Src\Tools\elastic.py

project_root = Path(__file__).parent
print(project_root)