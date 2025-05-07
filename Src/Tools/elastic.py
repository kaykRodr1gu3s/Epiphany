import dotenv
import os
from elasticsearch import Elasticsearch

class test:
    def __init__(self):
        self.client = Elasticsearch(cloud_id=os.getenv("cloud_id"), api_key=os.getenv("elasticsearch_api"))

    @property
    def searcher(self):
        print(self.client.search(index="index-name"))



if __name__ == "__main__":
    dotenv.load_dotenv()
    elastic_integration = test()
    elastic_integration.searcher