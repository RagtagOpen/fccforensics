from datetime import datetime, timedelta
import json
import os

import boto3
from elasticsearch import Elasticsearch

import tags

def query_by_source(event=None, context=None):
    es = Elasticsearch(os.environ['ES_ENDPOINT'], timeout=30)
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
          "filter": {
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
          }
        }
      },
      "aggs": {
        "source": {
          "terms": {
            "size": 25,
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
    query['query']['bool']['filter']['bool']['should'].append({
        'terms': {'analysis.source': tags.sources['positive']}
    })
    query['query']['bool']['filter']['bool']['should'].append({
        'terms': {'analysis.more_like_this.src_doc_id': tags.clusters['positive']}
    })
    print('positive query=%s' % json.dumps(query))
    resp = es.search(index='fcc-comments', body=query)
    by_source = {}
    for src in resp['aggregations']['source']['buckets']:
        if src['key'] == 'unknown':
            continue
        by_source[src['key']] = src['doc_count']
    if resp['aggregations']['sigterms']['buckets']:
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
            "size": 25,
            "field": "analysis.source"
          }
        }
      }
    }
    query['query']['bool']['should'].append({
        'terms': {'analysis.source': tags.sources['negative']}
    })
    query['query']['bool']['should'].append({
        'terms': {'analysis.more_like_this.src_doc_id': tags.clusters['negative']}
    })
    print('negative query=%s' % json.dumps(query))
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
    # count breached by source
    query = {
      "query": {
        "constant_score": {
          "filter": {
            "exists": {
              "field": "analysis.breached"
            }
          }
        }
      },
      "aggs": {
        "source": {
          "terms": {
            "size": 25,
            "field": "analysis.source"
          },
          "aggs": {
            "breached": {
              "terms": {
                "field": "analysis.breached"
              }
            }
          }
        }
      }
    }
    resp = es.search(index='fcc-comments', body=query, size=0)
    breached = {}
    for source in resp['aggregations']['source']['buckets']:
        src = source['key']
        breached[src] = {}
        for b in source['breached']['buckets']:
            breached[src]['breached' if b['key'] else 'unbreached'] = b['doc_count']
    rval['breached'] = breached
    rval['sources'] = tags.source_meta
    return rval


def query_by_source_s3(event=None, context=None):
    data = query_by_source(event, context)
    data['updated'] = datetime.now().isoformat()
    # save output to S3
    s3 = boto3.resource('s3')
    s3.Object(os.environ['S3_BUCKET'], 'by_source.json').put(
      Body=json.dumps(data),
      ContentType='application/json',
      ACL='public-read',
      Expires=(datetime.now() + timedelta(hours=6))
    )
    return data


if __name__ == '__main__':
    print(json.dumps(query_by_source(), indent=2))
