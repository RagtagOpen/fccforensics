import json
import os

from elasticsearch import Elasticsearch

import tags

def query_by_source(event=None, context=None):
    es = Elasticsearch(os.environ['ES_ENDPOINT'])
    query = {
      "_source": "date_disseminated",
      "size": 1,
      "sort": [
        {
          "date_disseminated": "desc"
        }
      ]
    }
    resp = es.search(index='fcc-comments', body=query)
    total = resp['hits']['total']
    latest = resp['hits']['hits'][0]['_source']['date_disseminated']
    # positive
    query = {
      "size": 0,
      "query": {
        "bool": {
          "should": [
            {
              "term": {
                "analysis.sentiment_manual": True
              }
            },
            {
              "term": {
                "analysis.titleii": True
              }
            },
            {
              "term": {
                "analysis.sentiment_sig_terms_ordered": True
              }
            }
          ]
        }
      },
      "aggs": {
        "source": {
          "terms": {
            "field": "analysis.source"
          }
        },
        "sigterms": {
          "terms": {
            "field": "analysis.sentiment_sig_terms_ordered"
          }
        }
      }
    }
    query['query']['bool']['should'].append({
        'terms': {'analysis.source': tags.sources['positive']}
    })
    resp = es.search(index='fcc-comments', body=query)
    by_source = {}
    for src in resp['aggregations']['source']['buckets']:
        if src['key'] == 'unknown':
            continue
        by_source[src['key']] = src['doc_count']
    by_source['sig_terms'] = resp['aggregations']['sigterms']['buckets'][0]['doc_count']
    rval = {
        'total': total,
        'latest': latest,
        'total_positive': resp['hits']['total'],
        'positive_by_source': by_source
    }

    # negative
    query = {
      "size": 0,
      "query": {
        "bool": {
          "should": [
            {
              "term": {
                "analysis.sentiment_manual": False
              }
            },
            {
              "term": {
                "analysis.titleii": False
              }
            },
            {
              "term": {
                "analysis.sentiment_sig_terms_ordered": False
              }
            }
          ]
        }
      },
      "aggs": {
        "source": {
          "terms": {
            "field": "analysis.source"
          }
        }
      }
    }
    query['query']['bool']['should'].append({
        'terms': {'analysis.source': tags.sources['negative']}
    })
    resp = es.search(index='fcc-comments', body=query)
    by_source = {}
    for src in resp['aggregations']['source']['buckets']:
        if src['key'] == 'unknown':
            continue
        by_source[src['key']] = src['doc_count']
    rval.update({
        'total_negative': resp['hits']['total'],
        'negative_by_source': by_source
    })
    return rval


if __name__ == '__main__':
    print(json.dumps(query_by_source(), indent=2))
