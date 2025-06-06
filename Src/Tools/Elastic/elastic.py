import logging
import json
import os
import sys
from pathlib import Path
from elasticsearch import Elasticsearch
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv


def setup_logging():
    """
    This function is used to create logs. 
    """
    project_root = Path(__file__).parent.parent.parent
    sys.path.append(str(project_root))
    log_path = project_root / "logs" / "elastic-logger.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5*1024*1024,
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Set up main logger
    logger = logging.getLogger("suricata-alert-uploader")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    # Set Elasticsearch client logging to WARNING to reduce noise
    logging.getLogger('elasticsearch').setLevel(logging.WARNING)
    
    return logger
logger = setup_logging()

class Elasticsearch_up:
    def __init__(self):
        """
        This class upload, update, search and identifier the datas in elasticsearch. With this class, the project don't work, it is the centralizer.
        """
        load_dotenv()
        try:
            self.client = Elasticsearch(hosts=os.getenv("elastic_endpoint"), api_key=os.getenv("elasticsearch_apikey"))
            logger.info("Connected sucessfully to elasticsearch")
        except Exception:
            raise logger.critical("Error to connect in the elasticsearch")

    def upload(self, datas: dict) -> None:
        """
        This class upload the datas in elasticsearch.

        Datas >>> dict
        """
        if type(datas) == list:
            """
            If the -upload argument is passed, all the eve.json will be uploaded, and this if statament will be initialized.
            """
            for data in datas:
                try:
                    docs = data.get("_raw")
                    docs = json.loads(docs)
                    doc = {"timestamp" : docs.get("timestamp"),
                        "event_type": docs.get("event_type"),
                        "src_ip" :  docs.get("src_ip"),
                        "src_port": docs.get("src_port"),
                        "dest_ip": docs.get("dest_ip"),
                        "flow_id": int(docs.get("flow_id")),
                        "verified": False
                        }
                    self.client.index(index="suricata-datas", document=doc)
                    logger.info("Data is being uploaded to elasticsearch")
                except Exception:
                    raise logger.critical("Erro to parse the data to collect from the tools")
        else:
            """
            If the -upload argument isn't passed as argument, will be identifier that the eve.json isn't being uploaded and will be utilezid the id_identifier function to verify the alert are in the elasticsearch.
            This 
            """
            try:

                doc = {"timestamp" : datas.get("timestamp"),
                    "event_type": datas.get("event_type"),
                    "src_ip" :  datas.get("src_ip"),
                    "src_port": datas.get("src_port"),
                    "dest_ip": datas.get("dest_ip"),
                    "flow_id": int(datas.get("flow_id")),
                    "verified": False
                    }
                self.client.index(index="suricata-datas", document=doc)
                logger.info("Data is being uploaded to elasticsearch")
            except Exception:
                raise logger.critical("Erro to parse the data to collect from the tools")
                
    def id_identifier(self, flow_id) -> bool:
        """
        This function is used to verify if the alert are in the elasticsearch. If the alert are, will be returned True, else will be returned False 
        """
        try:
            datas = self.client.search(index="suricata-datas",body={"size": 1,"query": {"term": {"flow_id": flow_id}}})
            datas["hits"].get("hits")[0].get("_source").get("flow_id") == flow_id
            return True
        except:
            return False

    @property
    def searcher(self) -> dict:
        """
        This function is used to search a query KQL in elasticsearch.
        """
        response = self.client.search(
            index="suricata-datas",
            scroll="2m",
            size=100,
            query={
                "term": {
                    "verified": False
                }
            }
        )

        if "_scroll_id" not in response:
            logger.critical("No data returned from the elasticsearch")
            return

        all_hits_dict = {}
        for hit in response["hits"]["hits"]:
            all_hits_dict[hit["_id"]] = hit

        return all_hits_dict
    
    def updater(self, id : str) -> None:
        """
        This function is used to update the verified field in elasticsearch, with this function, the field will be transformed in True 
        """
        self.client.update(index="suricata-datas",id=id,body={"doc": {"verified": True}})