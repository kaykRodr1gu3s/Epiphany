import json
from Tools.Elastic.elastic import Elasticsearch_up
from Tools.Splunk.splunk import Splunk_up
from Tools.TheHive.thehive import Thehive
from Tools.Server.server_connector import Server


if __name__ == "__main__":

    server = Server()
    server.suricata_datas
    splunk = Splunk_up()
    elasticsearch_up = Elasticsearch_up()
    splunk.suricata_alerts_upload()

    for docs in splunk.searcher:
        
        doc = docs.get("_raw")
        doc = json.loads(doc)
        verification = elasticsearch_up.id_identifier(doc.get("flow_id"))

        if verification == False:
            elasticsearch_up.upload(doc)


    elasticsearch_up.searcher
    thehive_client = Thehive()
    thehive_client.create_alert_function(elasticsearch_up.searcher)
