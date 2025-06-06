import sys
from logging.handlers import RotatingFileHandler
import logging
import os
import time
from dotenv import load_dotenv
from pathlib import Path
from thehive4py.api import TheHiveApi
from thehive4py.models import Alert, AlertArtifact
from Tools.Elastic.elastic import Elasticsearch_up


def setup_logging():
    """
    This function is used to create logs. 
    """
    project_root = Path(__file__).parent.parent.parent
    sys.path.append(str(project_root))
    log_path = project_root / "logs" / "TheHive.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
    log_path,
    maxBytes=5*1024*1024,
    backupCount=3
)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger("TheHive.log")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    return logger
logger = setup_logging()

class Thehive:
    """
    This class create a connection and create alert in the Thehive 
    """
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        load_dotenv()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.api = os.getenv("thehive_api")
        self.endpoint = os.getenv("thehive_endpoint")
        self.client = self.thehive_conector
        
    @property
    def thehive_conector(self) -> None:
        """
        This function create a client in Thehive
        """

        if not self.api or not self.endpoint:
            raise ValueError("TheHive API key or endpoint not found in environment variables")
            

        for attempt in range(self.max_retries):
            try:
                self.client = TheHiveApi(self.endpoint, self.api)
                logger.info("Successfully initialized TheHive client")
                return self.client
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to initialize TheHive client after {self.max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Connection attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

    def create_alert_function(self, elastic_datas) -> None:
        """
        This function create alerts in Thehive.

        elastic_datas >>> Dict
        """
        elastic_update = Elasticsearch_up()
        try:
            if not elastic_datas:
                logger.warning("No data provided to create alert")
                return
            for elastic_id in elastic_datas:

                datas = elastic_datas[elastic_id]
                alert = Alert(
                    title=f"Ip source {datas["_source"]['src_ip']}",
                    type="external",
                    source="Suricata",
                    description=f"The event_type is: {datas["_source"]["event_type"]}",
                    sourceRef=elastic_id,
                    artifacts=[
                        AlertArtifact(dataType="host", data=datas["_source"]["src_ip"]),
                        AlertArtifact(dataType="datetime", data=datas["_source"]["timestamp"]),
                        AlertArtifact(dataType="SourceName", data="Suricata"),
                        AlertArtifact(dataType="Destination", data=datas["_source"]["dest_ip"])
                    ]
                )
                response = self.client.create_alert(alert)
                logger.info(f"Alert creation response: {response}")
                logger.info(f"Successfully created alert")
                elastic_update.updater(id=elastic_id)



        except Exception as e:
            logger.error(f"Error creating alert in TheHive: {str(e)}")
            pass