import os

from elasticsearch import Elasticsearch

def query_positive_by_date(event=None, context=None):
    query = {
      "size": 0,
      "query": {
        "term": {
          "analysis.titleii": "true"
        }
      },
      "aggs": {
        "by_week": {
          "date_histogram": {
            "field": "date_received",
            "interval": "week"
          }
        }
      }
    }
    es = Elasticsearch(os.environ['ES_ENDPOINT'])
    resp = es.search(index='fcc-comments', body=query)
    by_week = {}
    for week in resp['aggregations']['by_week']['buckets']:
        by_week[week['key_as_string']] = week['doc_count']
    return {
        'total': resp['hits']['total'],
        'by_week': by_week
    }

if __name__ == '__main__':
    print(query_positive_by_date())
