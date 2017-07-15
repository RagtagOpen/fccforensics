import argparse
import json
import os
import sys

from elasticsearch import Elasticsearch

import tags

parser = argparse.ArgumentParser(description='Fetch, index, and tag comments')
parser.add_argument(
    '--endpoint', dest='endpoint',
    default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
)
args = parser.parse_args(args=sys.argv[1:])

es = Elasticsearch(args.endpoint)

query = {
  "aggs": {
    "cluster": {
      "terms": {
        "field": "analysis.more_like_this.src_doc_id.keyword"
      }
    }
  },
  "query": {
    "bool": {
      "filter": {
        "bool": {
          "must_not": [
            {
              "terms": {
                "analysis.more_like_this.src_doc_id.keyword": tags.clusters['positive']
              }
            }
          ]
        }
      }
    }
  }
}

ids_query = {
  "_source": "text_data",
    "query": {
        "ids" : {
            "type" : "document",
            "values" : []
        }
    }
}
resp = es.search(index='fcc-comments', body=query)
clusters = {}
for cluster in resp['aggregations']['cluster']['buckets']:
    clusters[cluster['key']] = cluster['doc_count']
#print('clusters=%s' % clusters)

ids = list(clusters.keys())
ids_query['query']['ids']['values'] = ids
rval = {}
resp = es.search(index='fcc-comments', body=ids_query, size=len(ids))
for doc in resp['hits']['hits']:
    print('---- %s (%s docs)\n%s\n\n' % (doc['_id'], clusters[doc['_id']],
        doc['_source']['text_data']))
    rval[doc['_id']] = {
      'size': clusters[doc['_id']],
      'text': doc['_source']['text_data']
    }

#print(json.dumps(rval, indent=2))
print(json.dumps(ids))
