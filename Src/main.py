from Tools.Elastic.elastic import Elasticsearch_up
from Tools.Splunk.splunk import Splunk_up

if __name__ == "__main__":
    splunk = Splunk_up()
    elasticsearch_up = Elasticsearch_up()
    elasticsearch_up.upload(splunk.searcher())