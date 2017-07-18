from datetime import timedelta
import json
import multiprocessing
import os
import warnings

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan
from elasticsearch.exceptions import ConnectionTimeout

import lib
import tags

class SigTermsSentiment:

    def __init__(self, endpoint='http://localhost:9200/', limit=10000, from_date=None, to_date=None):
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
        #self.date = date
        self.from_date = from_date
        self.to_date = to_date
        if from_date and not to_date:
            self.to_date = from_date + timedelta(days=1)
        if from_date:
            self.query['query']['bool']['filter']['bool']['must'] = [{
              "range": {
                "date_disseminated": {
                  "gte": self.from_date.strftime('%Y-%m-%d'),
                  "lt": self.to_date.strftime('%Y-%m-%d'),
                  "format": "yyyy-MM-dd"
                }
              }
            }]

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

    def tag_positive_terms(self):
        '''
            get documents without a sentiment tag that match phrase with slop:
              - protect|support|keep|need net neutrality
              - let the new neutrality stand
            for a broader result set than regex in analyze
        '''
        query = {
          "_source": "text_data",
          "query": {
            "bool": {
              "filter": {
                "bool": {
                  "should": [
                  ],
                  "must": [
                    {
                      "term": {
                        "analysis.source": "unknown"
                      }
                    }
                  ],
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

        phrases = [
            'essential net neutrality',
            'keep net neutrality',
            'maintain net neutrality',
            'need net neutrality',
            'preserve net neutrality'
            'protect net neutrality',
            'save net neutrality',
            'support net neutrality',
            'support title 2',
            'support title II',
            'let the new neutrality stand',
            'net neutrality rules are extremely important'
            'net neutrality is important'
        ]
        for phrase in phrases:
            subq = {
              "match_phrase": {
                "text_data": {
                  "query": phrase,
                  "slop": 3
                }
              }
            }
            query['query']['bool']['filter']['bool']['should'].append(subq)
        print(json.dumps(query))
        resp = self.es.search(index='fcc-comments', body=query, size=0)
        total = resp['hits']['total']
        print('tagging %s / %s matches' % (self.limit, total))
        docs = []
        for doc in scan(self.es, index='fcc-comments', query=query, size=1000):
            docs.append(lib.bulk_update_doc(doc['_id'], {'source': 'es_terms_positive'}))
            if not len(docs) % 1000:
                print('\tfetched %s\n%s\t%s' % (len(docs), doc['_id'], doc['_source']['text_data'][:400]))
            if len(docs) == self.limit:
                break

        print('indexing %s' % (len(docs)))
        tagged = lib.bulk_update(self.es, docs)
        print('tagged %s / %s matches' % (tagged, total))
        return tagged



    def preview(self, fraction=0.1):
        fetched = 0
        scores = []
        while fetched < self.limit:
            '''
                use search instead of scan because keeping an ordered scan cursor
                open negates the performance benefits
            '''
            resp = self.es.search(index='fcc-comments', body=self.query, size=self.limit)
            mod_print = int(1 / fraction)
            print('total=%s mod_print=%s' % (resp['hits']['total'], mod_print))
            for doc in resp['hits']['hits']:
                fetched += 1
                scores.append(doc['_score'])
                if not fetched % mod_print:
                    print('\n--- comment %s\t%s\t%s\t%s' % (fetched, doc['_id'],
                        doc['_score'], doc['_source']['text_data'][:1000]))


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
                'doc': {'analysis.sentiment_sig_terms_ordered': True},
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

if __name__ == '__main__':
    terms = SigTermsSentiment(endpoint=os.environ['ES_ENDPOINT'], limit=50000)
    terms.tag_positive_terms()
