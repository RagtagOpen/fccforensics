from datetime import timedelta, datetime
import json
import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

import lib

TAG = 'more_like_this'

class MLTClusterer:

    def __init__(self, endpoint='http://localhost:9200/', limit=100, date=None):
        self.endpoint = endpoint
        self.es = Elasticsearch(self.endpoint, timeout=30)
        self.limit = int(limit)
        '''
            get 80% more like this documents that:
            - have the analysis field
            - are not the source document
            - don't already have a more like this source document
        '''
        self.mlt_query = {
          "_source": [""],
          "query": {
            "bool": {
              "filter": {
                "bool": {
                  "must_not": [
                    {
                      "term": {
                        "analysis.untaggable": True
                      }
                    }
                  ],
                  "must": [
                    {
                      "exists": {
                        "field": "text_data"
                      }
                    }
                  ]
                }
              },
              "must": {
                  "more_like_this": {
                    "min_term_freq": 1,
                    "like": [{
                      "_index" : "fcc-comments",
                      "_type" : "document",
                      "_id" : ""
                    }],
                    "max_query_terms": 40,
                    "minimum_should_match": "80%",
                    "fields": [
                      "text_data"
                    ],
                    "min_doc_freq": 100
                  }
                }
            }
          }
        }
        '''
            aggregations for more like this query
            calculate these on the first query but don't need to get them for subsequent fetches
            - count by source
            - couny by src_doc_id
        '''
        self.mlt_aggs = {
          "aggs": {
            "source": {
              "terms": {
                "field": "analysis.source"
              }
            },
            "mlt": {
              "terms": {
                "field": "analysis.%s.src_doc_id.keyword" % TAG
              }
            }
          }
        }
        '''
            get a document from an unknown source and unknown sentiment
            that does not have a more like this field
        '''
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
                  "exists": {"field": "analysis.%s" % TAG},
                },
                {
                  "exists": {"field": "analysis.titleii"},
                },
              ]
            }
          }
        }
        self.date = date
        if date:
            # add single-day date range to more untagged query
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
        # get one untagged document
        print(json.dumps(self.untagged_query))
        resp = self.es.search(index='fcc-comments', body=self.untagged_query, size=1)
        untagged_total = resp['hits']['total']
        print('\nmore like this for %s limit %s / %s' % (self.date, self.limit, untagged_total))
        while tagged < self.limit and resp['hits']['total']:
            hit = resp['hits']['hits'][0]
            text = hit['_source']['text_data']
            print('\n--- %s/%s more like %s\n%s\n----' % (
                tagged, resp['hits']['total'], hit['_id'], text[:400]))
            mlt = {}

            # only run more like this for comments of at least 20 words
            terms = len(text.split(' '))
            if terms >= 50:
                mlt_matches = self.tag_mlt(text, hit['_id'])
                mlt = {
                    'is_source': True,
                    'src_doc_id': hit['_id'],
                    'matches': mlt_matches,
                }
                print(json.dumps(mlt))
                if mlt_matches > 1000:
                    print('---- cluster size %s on %s' % (mlt_matches, hit['_id']))
            else:
                mlt = {
                    'too_short': terms,
                }
                print('too short')
            doc = {'doc': {'analysis': {}}}
            doc['doc']['analysis'][TAG] = mlt
            # update the untagged source document with analysis.more_like_this
            print('update source doc %s: doc=%s' % (hit['_id'], mlt))
            self.es.update(index='fcc-comments', doc_type='document', id=hit['_id'],
                body=doc, refresh=True)
            tagged += 1
            # get another untagged
            resp = self.es.search(index='fcc-comments', body=self.untagged_query, size=1)

    def tag_mlt(self, text, src_doc_id, min_cluster_size=100):
        # first run a count
        query = {}
        query.update(self.mlt_query)
        query['query']['bool']['must']['more_like_this']['like'][0]['_id'] = src_doc_id
        terms = min([40, len(text.split(' '))])
        query['query']['bool']['must']['more_like_this']['max_query_terms'] = terms

        print('mlt query=%s' % json.dumps(query))
        resp = self.es.count(index='fcc-comments', body=query)
        if not resp['count']:
            return 0
        # add aggregations
        query.update(self.mlt_aggs)
        print('mlt query=%s' % json.dumps(query))

        # get page of like this results; not all because want to check for existing clusters
        resp = self.es.search(index='fcc-comments', body=query, size=10)
        mlt_matches = resp['hits']['total']
        # only need aggs for the first query
        del query['aggs']
        print('%s more like this' % mlt_matches)
        print('aggregations=%s' % resp['aggregations'])

        # if matching documents have a source other than unknown, use that
        src = 'unknown'
        source_buckets = resp['aggregations']['source']['buckets']
        if source_buckets:
            src = source_buckets[0]['key']
            print('using source %s' % src)
        # mlt aggregation result is a count of documents per cluster
        mlt_buckets = resp['aggregations']['mlt']['buckets']

        # if the MLT returns an existing cluster, join it if either:
        # - it's bigger than the current MLT result
        # - it's bigger than the minimum interesting cluster size
        join_cluster = False
        cluster_size = mlt_buckets[0]['doc_count'] if mlt_buckets else 0
        if cluster_size:
            join_cluster = cluster_size >= min([min_cluster_size, mlt_matches])
        if join_cluster:
            # add these results to the existing cluster
            src_doc_id = mlt_buckets[0]['key']
            print('found existing cluster from %s (%s docs)' % (src_doc_id, cluster_size))
            # update query to exclude docs already in this cluster
            query['query']['bool']['filter']['bool']['must_not'] = [
                {'term': {'analysis.%s.src_doc_id' % TAG: src_doc_id}}
            ]
            if src != 'unknown':
                # no need to re-tag docs that already have this source
                query['query']['bool']['filter']['bool']['must_not'].append(
                    {'term': {'analysis.source': src}})
            print('updated mlt query=%s' % json.dumps(query))
            # query to get new size
            resp = self.es.search(index='fcc-comments', body=query, size=0)
            mlt_matches = resp['hits']['total']

        # fetch matching untagged docs
        if not mlt_matches:
            return 0
        print('fetching %s' % mlt_matches)
        docs = []
        for doc in scan(self.es, index='fcc-comments', query=query, size=500):
            mlt = {}
            mlt[TAG] = {
                'src_doc_id': src_doc_id,
                'matches': mlt_matches,
            }
            if src != 'unknown':
                mlt[TAG]['source'] = src
            docs.append(lib.bulk_update_doc(doc['_id'], mlt))
            if not len(docs) % 1000:
                print('\tfetched %s / %s' % (len(docs), mlt_matches))

        # update with analysis.more_like_this
        if not docs:
            return 0
        print('indexing %s' % (len(docs)))
        return lib.bulk_update(self.es, docs)


if __name__ == '__main__':
    cluster = MLTClusterer(endpoint=os.environ['ES_ENDPOINT'], limit=1000)
    cluster.run()
