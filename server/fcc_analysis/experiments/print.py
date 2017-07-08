import json
import os
import sys

import argparse
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
from fcc_analysis import tags

parser = argparse.ArgumentParser(description='Tag by query')
parser.add_argument(
    '--endpoint', dest='endpoint',
    default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
)
parser.add_argument(
    '--limit', dest='limit', type=int, default=1000
)
parser.add_argument(
    '--sample', dest='sample', type=int, default=100
)
args = parser.parse_args(args=sys.argv[1:])

es = Elasticsearch(args.endpoint)

query = {
  "_source": ["text_data", "analysis"],
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
query['query']['bool']['filter']['bool']['must_not'] += must_not_terms
fetched = 0
print_mod = int(args.limit * (args.sample / 100))
print(json.dumps(query))
resp = es.search(index='fcc-comments', body=query, size=args.limit)
for doc in resp['hits']['hits']:
    fetched += 1
    if not fetched % print_mod:
        analysis = doc['_source'].get('analysis', {})
        print('%s\t%s\t%s\tsource=%s analysis.titleii=%s sig_terms=%s\n%s\n' % (
            fetched, doc['_score'], doc['_id'], analysis.get('source'), analysis.get('titleii'),
            analysis.get('sentiment_sig_terms_ordered'), doc['_source'].get('text_data', None)))
