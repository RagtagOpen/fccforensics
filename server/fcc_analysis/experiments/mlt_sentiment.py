import json
import os
import re
import sys

import argparse
from elasticsearch import Elasticsearch

'''
python mlt_sentiment.py  --endpoint https://user@pass:hostname:port

try to categorize comments by asking ES for more documents like the comment

- get 10 randomly chosen docs without analysis.titleii (regex-based sentiment)
- for each, get 10 more like this results with analysis.titleii
- print uncategoriezed doc, more like this matches
- score = +1 for positive (true) sentiment match, -1 for negative (false) sentiment match
'''

parser = argparse.ArgumentParser(description='Test sentiment by more-like-this')
parser.add_argument(
    '--endpoint', dest='endpoint',
    default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
)
args = parser.parse_args(args=sys.argv[1:])

es = Elasticsearch(args.endpoint)

# double quotes for cut and paste to ES console

query = {
    "query": {
        "function_score": {
            "query": {
                "bool": {
                    "must_not": {
                        "exists" : { "field" : "analysis.titleii" }
                    }
                }
            },
            "functions": [{"random_score": {}}]
        }
    }
}
# ignore these for relevance
stop_words = ["chairman", "ajit", "pai", "obama", "wheeler", "internet", "broadband",
    "isp", "fcc", "telecommunication"]
mlt_query = {
    "_source": ["text_data", "analysis.titleii"],
    "query": {
        "bool": {
            "must": [
                {
                    "more_like_this": {
                        "fields": ["text_data"],
                        "like": "",
                        "min_term_freq": 1,
                        "max_query_terms": 20,
                        "stop_words": stop_words
                    }
                }
            ],
            "filter" : {
                "bool": {
                    "must": {
                        "exists" : { "field" : "analysis.titleii" }
                    }
                }
            }
        }
    }
}

mlt_size = 10
response = es.search(index='fcc-comments', body=query, size=10)
for hit in response['hits']['hits']:
    score = 0
    total = 0
    text = hit['_source']['text_data']
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    mlt_query['query']['bool']['must'][0]['more_like_this']['like'] = text
    #print(json.dumps(mlt_query, indent=2))
    mlt_response = es.search(index='fcc-comments', body=mlt_query, size=mlt_size)
    matches = []
    for mlt_hit in mlt_response.get('hits', {}).get('hits', []):
        score += 1 if mlt_hit['_source']['analysis']['titleii'] else -1
        matches.append({
            'value': mlt_hit['_source']['analysis']['titleii'],
            'text': re.sub(r'\n+', ' ', mlt_hit['_source']['text_data'])
        })
        total += 0
    print('\n----- uncategorized comment ------------------------------------------\n%s' % text)
    print('----- score %s/%s' % (score, mlt_size))
    print('----------------------------------------------------------------------')
    for match in matches:
        print('\t*%s*\t%s' % (match['value'], match['text']))
