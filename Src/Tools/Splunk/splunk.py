import splunklib
import os
import json
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
import logging
from pathlib import Path
import sys
import splunklib.client



def setup_logging():
    """
    This function is used to create logs. 

    """
    project_root = Path(__file__).parent.parent.parent
    sys.path.append(str(project_root))
    log_path = project_root / "logs" / "splunk_uploader.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
    log_path,
    maxBytes=5*1024*1024,
    backupCount=3
)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger("splunk-logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

class Splunk_up:
    """
    This class connect in a client and upload and search data in the splunk
    """
    def __init__(self):
        load_dotenv()
        try:
            self.client = splunklib.client.connect(host=os.getenv("splunk_endpoint"), token=os.getenv("splunk_token"))
            logger.info("Connected sucessfully to splunk")
            return
        except Exception:
            logger.info("Error to connect in Splunk")
            raise

    @property
    def suricata_alerts_upload(self):
        """
        This function open a .json file and upload to splunk in the suricata_datas index
        """
        with open("eve.json", 'r') as files:
            for file in files:
                try:
                    indexes = self.client.indexes["suricata-datas"]
                    event_data = json.loads(file)
                    event_data["verified"] = False
                    event_str = json.dumps(event_data)
                    indexes.submit(event_str, sourcetype="suricata_json")
                except Exception:
                    logger.error(f"Failed to upload JSON to splunk - timestamp alert {file.get("timestamp")}")
                    raise
            logger.info("JSON uploaded to Splunk")

    
    @property
    def searcher(self):
        """
        This function search in splunk , the query is the _query()
        """
        try:
            job = self.client.jobs.create(self._query())
            resultado = job.results(output_mode='json')
            data = json.loads(resultado.read().decode("utf-8"))
            if data["results"]:
                logger.info("Data has been collect from splunk successfully")
                return data["results"]
            else:
                logger.warning("No alert found")

        except Exception:
            raise logger.error("Error to create job in the splunk")


    def _query(self) -> str:
        """
        This is a query to splunk.
        """
        return """search 
        index=suricata_rules
        """