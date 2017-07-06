import json
import multiprocessing
from tqdm import tqdm
import requests
import warnings
import io

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan
from elasticsearch.exceptions import ConnectionTimeout

class SigTermsSentiment:

    def __init__(self, endpoint='http://localhost:9200/', limit=10000):
        self.endpoint = endpoint
        self.es = Elasticsearch(self.endpoint)
        self.limit = int(limit)
        self.indexed = 0

    def run(self):
        '''
            get documents without a sentiment tag that match significant terms:
            - significant terms from postive regex tagged vs others
            - extra multi match clause for stronger terms (in multiple term sets:
                positive vs negative, untagged, and all
            - phrase match net neutrality since both terms score high
        '''
        query = {
          "_source": "text_data",
          "query": {
            "bool": {
              "minimum_should_match": 1,
              "should": [
                {
                  "multi_match": {
                    "query": "action cannot current despise escape isps job keep place protect stand tell trusted users",
                    "type": "most_fields",
                    "fields": [
                      "text_data",
                      "text_data.english"
                    ]
                  }
                },
                {
                  "multi_match": {
                    "query": "keep stand tell net neutrality",
                    "type": "most_fields",
                    "fields": [
                      "text_data",
                      "text_data.english"
                    ]
                  }
                },
                {
                  "match_phrase": {
                    "text_data": "net neutrality"
                  }
                }
              ],
              "filter": {
                "bool": {
                  "must_not": [
                    {
                      "exists": {
                        "field": "analysis.titleii"
                      }
                    },
                    {
                      "exists": {
                        "field": "analysis.sentiment_manual"
                      }
                    },
                    {
                      "exists": {
                        "field": "analysis.sentiment_sig_terms"
                      }
                    }
                  ]
                }
              }
            }
          }
        }
        index_queue = multiprocessing.Queue()

        bulk_index_process = multiprocessing.Process(
            target=self.bulk_index, args=(index_queue,),
        )
        bulk_index_process.start()

        fetched = 0
        try:
            for doc in scan(self.es, index='fcc-comments', query=query, size=100):
                index_queue.put(doc['_id'])
                fetched += 1
                if not fetched % 250:
                    print('fetched %s/%s\t%s%%' % (fetched, self.limit, int(fetched/self.limit*100)))
                if fetched == self.limit:
                    break
        except ConnectionTimeout:
            print('error fetching: connection timeout')

        index_queue.put(None)
        bulk_index_process.join()

    def bulk_index(self, queue, size=200):

        actions = []
        indexed = 0
        while True:
            item = queue.get()
            if item is None:
                break
            doc_id = item

            doc = {
                '_index': 'fcc-comments',
                '_type': 'document',
                '_op_type': 'update',
                '_id': doc_id,
                'doc': { 'analysis.sentiment_sig_terms': True },
            }
            actions.append(doc)

            if len(actions) == size:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    try:
                        response = bulk(self.es, actions)
                        indexed += response[0]
                        print('\tindexed %s/%s\t%s%%' % (indexed, self.limit,
                            int(indexed / self.limit * 100)))
                        actions = []
                    except ConnectionTimeout:
                        print('error indexing: connection timeout')

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            response = bulk(self.es, actions)
            indexed += response[0]
            print('indexed %s' % (indexed))
