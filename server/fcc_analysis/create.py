import json
import os
import sys

from elasticsearch import Elasticsearch

from . import mappings

sys.path.append(os.path.join(os.path.dirname(__file__)))

class IndexCreator:
    def __init__(self, endpoint='http://127.0.0.1:9200'):
        self.endpoint = endpoint

    def run(self):
        es = Elasticsearch(self.endpoint)
        es.indices.create(index='fcc-comments', body=mappings.MAPPINGS)
        print('created fcc-comments index')

