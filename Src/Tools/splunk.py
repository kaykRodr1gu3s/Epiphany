import os
import json
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
import logging
from pathlib import Path
import sys
import splunklib.client
import json

load_dotenv()
def setup_logging():
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    log_path = project_root / "logs" / "splunk_searcher.log"
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


class test:
    def __init__(self):
        try:
            self.client = splunklib.client.connect(host=os.getenv("splunk_endpoint"), token=os.getenv("splunk_token"))

            logger.info("Connected sucessfully to splunk")
            return
        except Exception:
            logger.info("Error to connect in Splunk")
            raise
    def searcher(self):

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
        return """search 
        index=suricata_rules event_type=alert
        """

if __name__ == "__main__":
    a = test()
    a.searcher()
