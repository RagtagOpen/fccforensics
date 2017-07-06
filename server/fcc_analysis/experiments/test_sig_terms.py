import os
import sys

import argparse
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan

parser = argparse.ArgumentParser(description='Test sentiment by more-like-this')
parser.add_argument(
    '--endpoint', dest='endpoint',
    default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
)
parser.add_argument(
    '--order', dest='order', default='desc'
)
parser.add_argument(
    '--limit', dest='limit', type=int, default=10000
)
args = parser.parse_args(args=sys.argv[1:])

print('sort by score %s' % args.order)

es = Elasticsearch(args.endpoint)
query = {
  "_source": [
    "text_data", "analysis.titleii", "analysis.sentiment_manual"
  ],
  "sort": [
    {
      "_score": {
        "order": args.order
      }
    }
  ],
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
          "must": [
            {
              "exists": {
                "field": "analysis.titleii"
              }
            }
          ]
        }
      }
    }
  }
}

idx = 0
match = 0
fn = 'test_%s.csv' % args.order
miss = []
for doc in scan(es, index='fcc-comments', query=query, size=250, preserve_order=True):
    if doc['_source']['analysis']['titleii']:
        match += 1
    else:
        miss.append({'id': doc['_id'], 'text': doc['_source']['text_data'],
            'score': doc['_score']})
    idx += 1
    if not idx % 500:
        print('%s/%s' % (match, idx))
    if idx >= args.limit:
        break

print('%s/%s positive' % (match, args.limit))
for m in miss:
    print('%s\t%s' % (m['id'], m['text'], m['score']))
