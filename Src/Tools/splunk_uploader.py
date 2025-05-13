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
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    log_path = project_root / "logs" / "splunk_uploader.log"
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

class Splunk_up:
    def __init__(self):
        load_dotenv()
        try:
            self.cliente = splunklib.client.connect(host=os.getenv("splunk_endpoint"), token=os.getenv("splunk_token"))
            logger.info("Connected sucessfully to splunk")
            return
        except Exception:
            logger.info("Error to connect in Splunk")
            raise

    def splunk_upload(self):
        with open("eve.json", 'r') as files:
            for file in files:
                try:
                    indexes = self.cliente.indexes["suricata_rules"]
                    event_data = json.loads(file)
                    event_str = json.dumps(event_data)
                    indexes.submit(event_str, sourcetype="suricata_json")
                    print("Hello")
                except Exception:
                    logger.error(f"Failed to upload JSON to splunk - timestamp alert {files.get("timestamp")}")
                    raise
            logger.info("JSON uploaded to Splunk")