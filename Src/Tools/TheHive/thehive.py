import sys
from logging.handlers import RotatingFileHandler
import logging
import os
import time
import uuid
from typing import Dict, Any 
from dotenv import load_dotenv
from pathlib import Path
from thehive4py.api import TheHiveApi
from thehive4py.models import Alert, AlertArtifact

def setup_logging():
    project_root = Path(__file__).parent.parent
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
    logger.addHandler(logging.StreamHandler())
    
    return logger
logger = setup_logging()

class Thehive:

    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        load_dotenv()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.api = os.getenv("thehive_api")
        self.endpoint = os.getenv("thehive_endpoint")
        self.client = self.thehive_conector
        
    @property
    def thehive_conector(self):
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

    def create_alert_function(self, elastic_datas: Dict[str, Any]) -> None:
        """
        Create an alert in TheHive based on event data pulled from Splunk.

        Args:
            splunk_datas (dict): Dictionary containing keys like EventCode, host, _time, and SourceName.
            
        Raises:
        Exception: If there's an error creating the alert in TheHive
        """
        try:
            if not elastic_datas:
                logger.warning("No data provided to create alert")
                return
            
            for data in elastic_datas:
                print(data)
                print()
                alert = Alert(
                    title=f"Ip source {data.get('_source')['src_ip']}",
                    type="external",
                    source="Suricata",
                    description=f"The event_type is: {data.get('_source')['event_type']}",
                    sourceRef=f"suricata alert: uuid: {uuid.uuid4()}",
                    artifacts=[
                        AlertArtifact(dataType="host", data=data.get('_source')['src_ip']),
                        AlertArtifact(dataType="datetime", data=data.get('_source')['timestamp']),
                        AlertArtifact(dataType="SourceName", data="Suricata"),
                        AlertArtifact(dataType="Destination", data=data.get('_source')['dest_ip'])
                    ]
                )
                response = self.client.create_alert(alert)
                logger.info(f"Alert creation response: {response}")
                logger.info(f"Successfully created alert")

        except Exception as e:
            logger.error(f"Error creating alert in TheHive: {str(e)}")
            raise 