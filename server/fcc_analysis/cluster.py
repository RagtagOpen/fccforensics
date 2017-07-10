from datetime import timedelta, datetime
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan
from elasticsearch.exceptions import ConnectionTimeout

import os
import tags

TAG = 'more_like_this'

class MLTClusterer:

    def __init__(self, endpoint='http://localhost:9200/', limit=100, date=None):
        self.endpoint = endpoint
        self.es = Elasticsearch(self.endpoint)
        self.limit = int(limit)
        self.mlt_query = {
          "_source": [
            ""
          ],
          "query": {
            "bool": {
              "filter": {
                "bool": {
                  "must": [
                    {
                      "exists": {
                        "field": "analysis"
                      }
                    }
                  ],
                  "must_not": [
                    {
                      "term": {
                        "id_submission": ""
                      },
                    }
                  ]
                }
              },
              "must": {
                  "more_like_this": {
                    "min_term_freq": 1,
                    "like": "",
                    "max_query_terms": 50,
                    "minimum_should_match": "95%",
                    "fields": [
                      "text_data"
                    ],
                    "min_doc_freq": 100
                  }
                }
            }
          }
        }
        self.mlt_aggs = {
          "aggs": {
            "source": {
              "terms": {
                "field": "analysis.source"
              }
            },
            "mlt": {
              "terms": {
                "field": "analysis."+TAG+".src_doc_id.keyword"
              }
            }
          }
        }
        self.untagged_query = {
          "_source": [
            "text_data",
            "analyis"
          ],
          "query": {
            "bool": {
              "must": [
                {
                  "term": {
                    "analysis.source": "unknown"
                  }
                }
              ],
              "must_not": [
                {
                  "exists": {"field": "analysis."+TAG}
                }
              ]
            }
          }
        }
        self.date = date
        if date:
            self.untagged_query['query']['bool']['must'].append({
              "range": {
                "date_disseminated": {
                  "gte": self.date.strftime('%Y-%m-%d'),
                  "lt": (self.date + timedelta(days=1)).strftime('%Y-%m-%d'),
                  "format": "yyyy-MM-dd"
                }
              }
            })

    def run(self):
        tagged = 0
        print(json.dumps(self.untagged_query))
        resp = self.es.search(index='fcc-comments', body=self.untagged_query, size=1)
        print('\nmore like this for %s limit %s / %s' % (self.date, self.limit, resp['hits']['total']))
        while tagged < self.limit and resp['hits']['total']:
            hit = resp['hits']['hits'][0]
            print('\n--- more like %s\n%s\n----' % (hit['_id'], hit['_source']['text_data'][:400]))
            mlt = {'analysis': {}}
            mlt['analysis'][TAG] = {}
            text = hit['_source']['text_data']
            terms = len(text.split(' '))
            if terms >= 20:
                mlt_matches = self.tag_mlt(text, hit['_id'])
                mlt['analysis'][TAG] = {
                    'is_source': True,
                    'matches': mlt_matches,
                }
                print(json.dumps(mlt))
                if mlt_matches > 1000:
                    print('---- cluster size %s on %s' % (mlt_matches, hit['_id']))
            else:
                mlt['analysis'][TAG] = {
                    'too_short': terms,
                }
                print('too short')
            self.es.index(index='fcc-comments', doc_type='document', id=hit['_id'],
                body=mlt, refresh=True)
            tagged += 1
            resp = self.es.search(index='fcc-comments', body=self.untagged_query, size=1)

    def tag_mlt(self, text, src_doc_id, min_cluster_size=100):
        tagged = 0
        tagged_ids = [src_doc_id]
        query = {}
        query.update(self.mlt_query)
        query.update(self.mlt_aggs)
        query['query']['bool']['must']['more_like_this']['like'] = text
        terms = min([50, len(text.split(' '))])
        query['query']['bool']['must']['more_like_this']['max_query_terms'] = terms
        # exclude the doc where this text came from
        query['query']['bool']['filter']['bool']['must_not'] = [
            {'term': { 'id_submission': src_doc_id}}
        ]
        #print('mlt query=%s' % json.dumps(query))

        resp = self.es.search(index='fcc-comments', body=query, size=10)
        # only need aggs for the first query
        del query['aggs']
        print('%s more like this' % resp['hits']['total'])

        src = 'unknown'
        source_buckets = resp['aggregations']['source']['buckets']
        if source_buckets:
            src = source_buckets[0]['key']
        mlt_buckets = resp['aggregations']['mlt']['buckets']

        # found an existing cluster
        if mlt_buckets and mlt_buckets[0]['doc_count'] > min_cluster_size:
            # use the cluster's source doc
            src_doc_id = mlt_buckets[0]['key']
            print('found existing cluster from %s (%s docs)' % (
                src_doc_id, mlt_buckets[0]['doc_count']))
            # update query to exclude docs already in this cluster
            query['query']['bool']['filter']['bool']['must_not'] = [
                {'term': { 'analysis.%s.src_doc_id' % TAG: src_doc_id}}
            ]
            print('updated mlt query=%s' % json.dumps(query))
            resp = self.es.search(index='fcc-comments', body=query, size=100)
            print('%s untagged' % resp['hits']['total'])

        while resp['hits']['total']:
            actions = []
            matches = resp['hits']['total']
            for hit in resp['hits']['hits']:
                mlt = {
                    'src_doc_id': src_doc_id,
                    'matches': matches,
                }
                if not src == 'unknown':
                    mlt['source'] = src
                action = {
                    '_index': 'fcc-comments',
                    '_type': 'document',
                    '_op_type': 'update',
                    '_id': hit['_id'],
                    'doc': {'analysis': {}}
                }
                action['doc']['analysis'][TAG] = mlt
                actions.append(action)
                tagged_ids.append(hit['_id'])
            resp = bulk(self.es, actions)
            #print(actions)
            tagged += resp[0]
            # exclude docs tagged in this run because search doesn't always see the latest
            # no way to force refresh with bulk indexing
            query['query']['bool']['filter']['bool']['must_not'] = [
                {'terms': { 'id_submission': tagged_ids}}
            ]
            #print('updated query=%s' % json.dumps(query))
            resp = self.es.search(index='fcc-comments', body=query, size=100)
            print('tagged %s, %s more to go' % (tagged, resp['hits']['total']))
        if tagged:
            print('\ntagged %s' % tagged)
        return tagged


if __name__ == '__main__':
    cluster = MLTClusterer(endpoint=os.environ['ES_ENDPOINT'], limit=1000, date=datetime(2017, 7, 3))
    cluster.run()
