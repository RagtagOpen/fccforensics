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
              "filter": tags.queries['untagged']['query']['bool']['filter']
            }
          }
        }
        self.from_date = from_date
        self.to_date = to_date
        if from_date and not to_date:
            self.to_date = from_date + timedelta(days=1)
        if from_date:
            self.query['query']['bool']['filter']['bool']['must'].append({
              "range": {
                "date_disseminated": {
                  "gte": self.from_date.strftime('%Y-%m-%d'),
                  "lt": self.to_date.strftime('%Y-%m-%d'),
                  "format": "yyyy-MM-dd"
                }
              }
            })

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

    def tag_negative_terms(self):
        query = tags.queries['untagged']
        query['_source'] = 'text_data'
        phrases = [
            'I support Chairman Pai\'s proposal to roll back Title II',
            'remove the inappropriate, unnecessary and overly vast regulations',
            'Title II is a Depression-era regulatory framework designed for a telephone monopoly that no longer exists',
        ]
        for phrase in phrases:
            subq = {
                'match_phrase': {
                    'text_data': {'query': phrase, 'slop': 3}
                }
            }
            query['query']['bool']['filter']['bool'].setdefault('should', [])
            query['query']['bool']['filter']['bool']['should'].append(subq)
            query['query']['bool']['filter']['bool']['minimum_should_match'] = 1
            return self.tag_by_phrase(query, 'es_terms_negative')
        '''
Dear FCC Commissioner ,
 
 The Obama-era FCC regulations known as ""Title II"" enable the federal government to exert an extraordinary and unnecessary amount of regulatory control over the internet. This bureaucratic overreach impedes innovation, stifles investment and continues to create economic uncertainty for one of the largest sectors of the U.S. economy.
 
 I support Chairman Pai's proposal to roll back Title II and restore the sensible regulatory framework that enjoyed broad bipartisan consensus and enabled the internet to thrive for more than two decades.
 
 I strongly urge all of the FCC Commissioners to support the Chairman's proposal to repeal the harmful Title II internet takeover.
---        
"As a concerned taxpayer and consumer, I am writing to urge the FCC to set the internet free and remove the inappropriate, unnecessary and overly vast regulations currently holding back the full potential of the internet. Due to the grip of the utility-style regulations imposed under the previous Commission, taxpayers have been put at risk, the threat of new fees on consumer bills still looms large, investment in internet infrastructure has not realized its full potential, innovations have gone undeveloped and unrealized, and twenty years of the appropriate level of oversight of the internet has been reversed.

We must dial-back the poorly conceived application of Title II in the Open Internet Order so that American taxpayers can benefit from an unrestrained and truly open internet that scales back the unlimited power of the government, protects consumers from new taxes and encourages future investment and endless innovations.
---
Title II is a Depression-era regulatory framework designed for a telephone monopoly that no longer exists. It was wrong to apply it to the Internet and the FCC should repeal it and go back to the free-market approach that worked so well.
        '''

    def tag_positive_terms(self):
        '''
            get documents without a sentiment tag that match phrase with slop:
            for a broader result set than regex in analyze
        '''
        query = tags.queries['untagged']
        query['_source'] = 'text_data'
        phrases = [
            'afraid of pay-to-play',
            'Changing Title II requirements would adversely',
            'do not change title 2 classification',
            'essential net neutrality',
            'fast lane',
            'FCC should reject Chairman Ajit Pai\'s plan',
            'FCC should throw out Chairman Ajit Pai\'s plan',
            'I believe in strong Net Neutrality',
            'internet is NOT a communication company GOLDEN EGG LAYING GOOSE',
            'Internet service providers should treat all data that travels over their networks fairly',
            'keep net neutral',
            'keep net neutrality',
            'let the new neutrality stand',
            'maintain internet utility backed by Title 2',
            'maintain net neutrality',
            'maintain the protections of Title II',
            'maintaining net neutrality',
            'misleadingly named proceeding',
            'must remain regulated under Title II',
            'need net neutrality',
            'net neutrality important',
            'Net neutrality is essential',
            'Net neutrality is vital',
            'net neutrality protections',
            'net neutrality should be maintained',
            'preserve net neutrality',
            'preserve title 2',
            'proposal to modify the Net Neutrality rules is unwanted',
            'protect net neutrality',
            'remain as part of Title 2',
            'remain classified under Title II',
            'retain title 2',
            'retain title ii',
            'safeguard net neutrality',
            'save net neutrality',
            'should not be controlled by companies who can and will force information',
            'slow lane',
            'stand up for net neutrality',
            'strongly oppose Chairman Pai\'s proposal',
            'support classifying internet under Title II',
            'support net neutrality',
            'support title 2',
            'support title II',
            'treat all data on the internet the same',
            'upholding net neutrality protections',
        ]
        for phrase in phrases:
            subq = {
                'match_phrase': {
                    'text_data': {'query': phrase, 'slop': 3}
                }
            }
            query['query']['bool']['filter']['bool'].setdefault('should', [])
            query['query']['bool']['filter']['bool']['should'].append(subq)
            query['query']['bool']['filter']['bool']['minimum_should_match'] = 1
            print(json.dumps(query))
            return self.tag_by_phrase(query, 'es_terms_positive')

    def tag_by_phrase(self, query, source):
        print(json.dumps(query))
        resp = self.es.search(index='fcc-comments', body=query, size=0)
        total = resp['hits']['total']
        print('tagging %s / %s matches' % (self.limit, total))
        docs = []
        for doc in scan(self.es, index='fcc-comments', query=query, size=1000):
            docs.append(lib.bulk_update_doc(doc['_id'], {'source': source}))
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
        mod_print = int(1 / fraction)
        while fetched < self.limit:
            '''
                use search instead of scan because keeping an ordered scan cursor
                open negates the performance benefits
            '''
            resp = self.es.search(index='fcc-comments', body=self.query, size=self.limit)
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
    terms = SigTermsSentiment(endpoint=os.environ['ES_ENDPOINT'], limit=5000)
    terms.tag_positive_terms()
