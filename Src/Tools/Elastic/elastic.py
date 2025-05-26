import dotenv
import logging
import json
import os
from pathlib import Path
from elasticsearch import Elasticsearch
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv


class Elasticsearch_up:
    def __init__(self):
        load_dotenv()
        self.client = Elasticsearch(hosts=os.getenv("elastic_endpoint"), api_key=os.getenv("elasticsearch_apikey"))

    def upload(self, datas):
        for data in datas:
            docs = data.get("_raw")
            print(docs)
            docs = json.loads(docs)
            print(type(docs))

            doc = {"timestamp" : docs.get("timestamp"),
                   "event_type": docs.get("event_type"),
                   "src_ip" :  docs.get("src_ip"),
                   "src_port": docs.get("src_port"),
                   "dest_ip": docs.get("dest_ip"),
                   "metadata": docs.get("alert").get("category"),
                   "verified": False
                   }
            self.client.index(index="main", document=doc)
            
    @property
    def searcher(self):
        response = self.client.search(
        index="main",
        scroll="2m",
        size=100,
        query={
            "match_all": {}
        }
        )

        if "_scroll_id" not in response:
            # colocar log - Erro: scroll_id não encontrado na resposta
            return

        scroll_id = response["_scroll_id"]
        all_hits = response["hits"]["hits"]

        while True:
            scroll_response = self.client.scroll(scroll_id=scroll_id, scroll="2m")
            hits = scroll_response["hits"]["hits"]
            if not hits:
                break
            all_hits.extend(hits)
        #colocar log - todos os dados coletados
        return all_hits