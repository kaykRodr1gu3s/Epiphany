import logging
import json
import os
import sys
from pathlib import Path
from elasticsearch import Elasticsearch
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv


def setup_logging():
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    log_path = project_root / "logs" / "elasticsearch.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
    log_path,
    maxBytes=5*1024*1024,
    backupCount=3
)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger("suricata-alert-uploader")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(logging.StreamHandler())
    
    return logger
logger = setup_logging()

class Elasticsearch_up:
    def __init__(self):
        load_dotenv()
        try:
            self.client = Elasticsearch(hosts=os.getenv("elastic_endpoint"), api_key=os.getenv("elasticsearch_apikey"))
            logger.info("Connected sucessfully to elasticsearch")
        except Exception:
            raise logger.critical("Error to connect in the elasticsearch")

    def upload(self, datas):
        if datas:
            for data in datas:
                try:
                    docs = data.get("_raw")
                    docs = json.loads(docs)
            
                    doc = {"timestamp" : docs.get("timestamp"),
                        "event_type": docs.get("event_type"),
                        "src_ip" :  docs.get("src_ip"),
                        "src_port": docs.get("src_port"),
                        "dest_ip": docs.get("dest_ip"),
                        "metadata": docs.get("alert").get("category"),
                        "verified": False
                        }
                    self.client.index(index="main", document=doc)
                    logger.info("Data is being uploaded to elasticsearch")
                except Exception:
                    raise logger.critical("Erro to parse the data to collect from the tools")

    @property
    def searcher(self):
        response = self.client.search(
        index="main",
        scroll="2m",
        size=100,
        query={
            "match_all": {}
        }
        )

        if "_scroll_id" not in response:
            logger.critical("No data returned from the elasticsearch")
            return

        scroll_id = response["_scroll_id"]
        all_hits = response["hits"]["hits"]

        while True:
            scroll_response = self.client.scroll(scroll_id=scroll_id, scroll="2m")
            hits = scroll_response["hits"]["hits"]
            if not hits:
                break
            all_hits.extend(hits)
        logger.info("All datas from elasticsearch was colected")
        return all_hits