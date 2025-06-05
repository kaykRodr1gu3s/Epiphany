import argparse
import json
from Tools.Elastic.elastic import Elasticsearch_up
from Tools.Splunk.splunk import Splunk_up
from Tools.TheHive.thehive import Thehive
from Tools.Server.server_connector import Server

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Which SIEM do you want to collect the datas ?")

    parser.add_argument('SIEM', type=str, choices=['splunk'], help='Choose the SIEM to collect data from')
    parser.add_argument("-upload", action="store_true", help="upload the data after collecting")

    args = parser.parse_args()

    print(f"Selected SIEM: {args.SIEM}")
    elasticsearch_up = Elasticsearch_up()

    if args.SIEM == "splunk":
        splunk = Splunk_up()
        if args.upload:

            server = Server()
            server.suricata_datas
            
            splunk.suricata_alerts_upload()


        for docs in splunk.searcher:

            doc = docs.get("_raw")
            doc = json.loads(doc)
            verification = elasticsearch_up.id_identifier(doc.get("flow_id"))

            if verification == False:
                elasticsearch_up.upload(doc)


        thehive_client = Thehive()
        thehive_client.create_alert_function(elasticsearch_up.searcher)
