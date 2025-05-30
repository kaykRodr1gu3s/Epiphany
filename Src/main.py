from Tools.Elastic.elastic import Elasticsearch_up
from Tools.Splunk.splunk import Splunk_up
from Tools.TheHive.thehive import Thehive
from Tools.Server.server_connector import Server


if __name__ == "__main__":
    server = Server()
    server.suricata_datas
    splunk = Splunk_up()
    elasticsearch_up = Elasticsearch_up()
    thehive_client = Thehive()
    thehive_client.create_alert_function(elasticsearch_up.searcher)    