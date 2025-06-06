import argparse
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Optional

from Tools.Elastic.elastic import Elasticsearch_up
from Tools.Server.server_connector import Server
from Tools.Splunk.splunk import Splunk_up
from Tools.TheHive.thehive import Thehive


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Src/logs/siem_processor.log')
    ]
)
logger = logging.getLogger(__name__)
@dataclass
class SIEMProcessor:
    """Initialize the SIEM processor.
    
    Args:
        siem_type (str): Type of SIEM to process (e.g., 'splunk')
        upload (bool): Whether to upload data to the SIEM
    """
    siem_type: str
    upload: bool
    elasticsearch: Optional[Elasticsearch_up] = field(default=None, init=False)
    splunk: Optional[Splunk_up] = field(default=None, init=False)
    thehive: Optional[Splunk_up] = field(default=None, init=False)
    server: Optional[Server] = field(default=None, init=False)

    def initialize_components(self) -> None:
        """
        Initialize all requirements components.
        """

        try:
            self.elasticsearch = Elasticsearch_up()
            logger.info("Elasticsearch initialized successfully")

            if self.siem_type == "splunk":
                self.splunk = Splunk_up()
                logger.info("Splunk initialized successfully")
            
            self.thehive = Thehive()
            logger.info("Thehive initialized succesffully")

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    def process_suricata_data(self) -> None:
        """Process Suricata data if upload is enabled."""
        if not self.upload:
            return
        
        try:
            self.server = Server()
            self.server.suricata_datas
            self.splunk.suricata_alerts_upload
            logger.info("Successfully processed Suricata data")

        except Exception as e:
            logger.error(f"Failed to process Suricata data: {e}")
            raise


    def process_splunk_data(self) -> None:
        
        if not self.splunk:
            return
        try:
            for doc in self.splunk.searcher:
                try:
                    raw_data = doc.get("_raw")
                    if not raw_data:
                        continue
                    data = json.loads(raw_data) 
                    flow_id = data.get("flow_id")

                    if not flow_id:
                        continue

                    if not self.elasticsearch.id_identifier(flow_id):
                        self.elasticsearch.upload(data)
                        logger.debug(f"Uploaded document with flow_id: {flow_id}")

                    
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON data, skipping")
                except Exception as e:
                    logger.error(f"Error processing document: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to process Splunk data: {e}")
            raise


    def create_alerts(self):
        """Create alerts in TheHive based on processed data."""
        if not self.thehive or not self.elasticsearch:
            return 
        
        try:
            self.thehive.create_alert_function(self.elasticsearch.searcher)
            logger.info("Successfully created alerts in TheHive")

        except Exception as e:
            logger.error(f"Failed to create alerts: {e}")
            raise
        
    def run(self):
        """
        Execute the main processing workflow
        """
        try:
            self.initialize_components() #vai iniciar a função initialize_components 
            self.process_suricata_data() # se tiver o argumento true, vai executar a função
            self.process_splunk_data() #vai iniciar a função splunk
            self.create_alerts() #vai iniciar a função create_alerts
            logger.info("Processing completed successfully")

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise

def parser_arguments() -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description="SIEM data Collection and processing Tool",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument(
        "SIEM",
        type=str,
        choices=["splunk"],
        help="Choose the SIEM to collect data from"
        )

        parser.add_argument(
            "-upload",
            action="store_true",
            help="Upload"
        )
        return parser.parse_args()

def main() -> None:
    """
    Main entry point of the applicattion
    """

    try:
        args = parser_arguments()
        processor = SIEMProcessor(args.SIEM, args.upload)
        processor.run()

    except Exception as e:
        logger.error(f"Application failed: {e}")
        raise

if __name__ == "__maaain__":
    main()
    os.remove("eve.json")
