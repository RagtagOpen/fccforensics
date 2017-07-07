import os
import sys

import argparse
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan

parser = argparse.ArgumentParser(description='Tag by query')
parser.add_argument(
    '--endpoint', dest='endpoint',
    default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
)
parser.add_argument(
    '--limit', dest='limit', type=int, default=5000
)
args = parser.parse_args(args=sys.argv[1:])

'''
    tag negative sentiment by query
'''
es = Elasticsearch(args.endpoint)

query = {
  "query": {
    "bool": {
      "must": [
        {
          "match_phrase": {
            "text_data": "Save American jobs by repealing Net Neutrality"
          }
        },
        {
          "bool": {
            "must_not": [
              {
                "exists": {
                  "field": "analysis.titleii"
                }
              }
            ]
          }
        }
      ]
    }
  }
}

ids = []
remaining = True
indexed = 0
fetched = 0
while fetched < args.limit and remaining:
    resp = es.search(index='fcc-comments', body=query, size=250)
    for doc in resp['hits']['hits']:
        ids.append(doc['_id'])
        fetched += 1
        if not fetched % 100:
            print('%s\t%s\t%s' % (fetched, doc['_score'], doc['_source']['text_data']))
    remaining = resp['hits']['total'] - len(ids)
    print('%s matches remaining' % (remaining))

    for i in range(0, len(ids), 25):
        actions = []
        for doc_id in ids[i:(i+25)]:
            actions.append({
                '_index': 'fcc-comments',
                '_type': 'document',
                '_op_type': 'update',
                '_id': doc_id,
                'doc': { 'analysis.titleii': False },
            })
        resp = bulk(es, actions)
        indexed += resp[0]
    ids = []
    print('indexed %s' % indexed)
