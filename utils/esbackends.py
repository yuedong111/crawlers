# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch


class EsBackends(object):
    def __init__(self, index_name):
        self.es = Elasticsearch(hosts=["127.0.0.1:9200"])
        self.index_name = index_name
        if self.es.indices.exists(index=self.index_name) is not True:
            self.create_index()

    def create_index(self):
        _index_mappings = {
            "mappings": {
                "properties": {
                    "link": {"type": "text", "index": True, "analyzer": "standard"},
                    "date": {"type": "text", "index": True},
                    "status": {"type": "text"}
                }
            }
        }
        _index_map2 = {
            "mappings": {
                "properties": {
                    "link": {
                        "type": "text",
                        "index": True,
                    },
                    "status": {"type": "text"},
                    "date": {"type": "text", "index": True}
                }
            }
        }
        if self.index_name == "meituan":
            res = self.es.indices.create(index="meituan", body=_index_mappings)
            if res["acknowledged"] is not True:
                print("the index have existed")
        else:
            res = self.es.indices.create(index=self.index_name, body=_index_map2)
            if res["acknowledged"] is not True:
                print("the index have existed")

    def index_data(self, data):
        try:
            self.es.index(index=self.index_name, body=data)
        except Exception as e:
            print("Insert error:{}".format(e))
            pass

    def search_data(self, body):
        res = self.es.search(index=self.index_name, body=body)
        return res

    def update_data(self, id, body):
        script = {
            "script": {
                "source": "ctx._source.status = params.status",
                "lang": "painless",
                "params": body
            }
        }
        self.es.update(index=self.index_name, id=id, body=script)


def es_search(index, url):
    es = EsBackends(index)
    body = {
        "query": {
            "multi_match": {
                "query": url,
                "type": "phrase",
                "slop": 0,
                "fields": [
                    "link"
                ],
                # "analyzer": "charSplit",
                "max_expansions": 1
            }
        }
    }
    res = es.search_data(body)
    if res.get("hits").get("hits"):
        for item in res.get("hits").get("hits"):
            if url.strip() == item.get("_source").get("link").strip():
                status = item.get("_source").get("status")
                return True, status, item.get("_id")
    return False, 0, None
