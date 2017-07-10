from datetime import timedelta
import json
import multiprocessing
import requests
import warnings
import io
from math import sqrt

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan
from elasticsearch.exceptions import ConnectionTimeout

import tags

class SigTermsSentiment:

    def __init__(self, endpoint='http://localhost:9200/', limit=10000, date=None):
        self.endpoint = endpoint
        self.es = Elasticsearch(self.endpoint)
        self.limit = int(limit)
        self.indexed = 0
        self.query = {
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
                        "field": "analysis.sentiment_sig_terms_ordered"
                      }
                    }
                  ]
                }
              }
            }
          }
        }
        must_not_terms = []
        for term in tags.sources['positive'] + tags.sources['negative']:
            must_not_terms.append({'term': {'analysis.source': term}})
        self.query['query']['bool']['filter']['bool']['must_not'] += must_not_terms
        self.date = date
        if date:
            self.query['query']['bool']['filter']['bool']['must'] = [{
              "range": {
                "date_disseminated": {
                  "gte": self.date.strftime('%Y-%m-%d'),
                  "lt": (self.date + timedelta(days=1)).strftime('%Y-%m-%d'),
                  "format": "yyyy-MM-dd"
                }
              }
            }]
        #print(json.dumps(self.query))

    def run(self):
        '''
            get documents without a sentiment tag that match significant terms:
            - significant terms from postive regex tagged vs others
            - extra multi match clause for stronger terms (in multiple term sets:
                positive vs negative, untagged, and all
            - phrase match net neutrality since both terms score high
        '''

        index_queue = multiprocessing.Queue()

        bulk_index_process = multiprocessing.Process(
            target=self.bulk_index, args=(index_queue,),
        )
        bulk_index_process.start()
        fetched = 0
        ids = []
        try:
            while fetched < self.limit:
                '''
                    use search instead of scan because keeping an ordered scan cursor
                    open negates the performance benefits
                '''
                resp = self.es.search(index='fcc-comments', body=self.query, size=self.limit)
                for doc in resp['hits']['hits']:
                    index_queue.put(doc['_id'])
                    fetched += 1
                    if not fetched % 100:
                        print('%s\t%s\t%s' % (fetched, doc['_score'],
                            doc['_source']['text_data']))
        except ConnectionTimeout:
            print('error fetching: connection timeout')

        index_queue.put(None)
        bulk_index_process.join()

    def preview(self, fraction=0.1):
        fetched = 0
        scores = []
        while fetched < self.limit:
            '''
                use search instead of scan because keeping an ordered scan cursor
                open negates the performance benefits
            '''
            resp = self.es.search(index='fcc-comments', body=self.query, size=self.limit)
            total = resp['hits']['total']
            mod_print = int(1 / fraction)
            print('total=%s mod_print=%s' % (resp['hits']['total'], mod_print))
            for doc in resp['hits']['hits']:
                fetched += 1
                scores.append(doc['_score'])
                if not fetched % mod_print:
                    print('\n--- comment %s\t%s\t%s' % (fetched, doc['_score'], doc['_source']['text_data']))


    def bulk_index(self, queue, size=20):

        actions = []
        indexed = 0
        ids = set()
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
                'doc': { 'analysis.sentiment_sig_terms_ordered': True },
            }
            actions.append(doc)
            ids.add(doc_id)

            if len(actions) == size:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    try:
                        response = bulk(self.es, actions)
                        indexed += response[0]
                        if not indexed % 200:
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
        ids = list(ids)
        #print('%s\n%s' % (len(ids), ' '.join(ids))
