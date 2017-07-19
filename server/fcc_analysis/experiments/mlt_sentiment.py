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

'''
notes

https://www.elastic.co/blog/text-classification-made-easy-with-elasticsearch
    "min_term_freq":1,
    "max_query_terms":20
    index with analyzer = english
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
# https://www.elastic.co/guide/en/elasticsearch/guide/current/stopwords.html, minus "not"
english_stop_words = ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is", "it", "no", "of", "on", "or", "such", "that", "the", "their", "then", "there", "these"]
"they", "this", "to", "was", "will", "with"
stop_words = english_stop_words + ["chairman", "ajit", "pai", "obama", "wheeler", "internet", "broadband", "isp", "fcc", "telecommunication", "title"]

'''
encourage request suggest implore urge
overturn reverse repeal undo
rather than unelected bureaucrats rather than Washington not big government not the FCC Enforcement Bureau
control Internet power grab take over broadband regulate broadband
exploitation distortion betrayal corruption perversion
pro-consumer framework light-touch approach hands-off free-market system policy
performed fabulously successfully worked very well performed supremely well functioned fabulously well functioned remarkably well performed very smoothly functioed very smoothly
two decades many years decades both parties support bipartisan backing universal consensus bipartisan approval
'''
mlt_query = {
    "_source": ["text_data", "date_received"],
    "query": {
        "bool": {
            "must": [
                {
                    "more_like_this": {
                        "minimum_should_match": "80%",
                        "like": "With respect to net neutrality and Title II. I encourage the commission to overturn Tom Wheeler's order to control the Internet. Internet users, rather than unelected bureaucrats, deserve to purchase whichever products we choose. Tom Wheeler's order to control the Internet is a exploitation  of net neutrality. It undid a pro-consumer framework that performed fabulously successfully for two decades with both parties' support.",
                        "min_term_freq": 1,
                        "max_query_terms": 25,
                        "min_doc_freq": 100,
                        "min_word_length": 3,
                        "fields": ["text_data"],
                        "analyzer": "english",
                        "stop_words": ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is", "it", "no", "of", "on", "or", "such", "that", "the", "their", "then", "there", "these"]
                    }
                }
            ],
            "filter": {
                "bool": {
                    "must_not": [
                        { "exists": { "field": "analysis.titleii" } },
                        { "exists": { "field": "analysis.sentiment_manual" } },
                        { "exists": { "field": "analysis.sentiment_sig_terms_ordered" } }
                    ]
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
        analysis = mlt_hit['_source']['analysis']
        sentiment_regex = analysis.get('titleii', None)
        sentiment_manual = analysis.get('sentiment_manual', None)
        score += 1 if sentiment_regex or sentiment_manual else -1
        matches.append({
            'value': '%s\t%s' % (sentiment_regex, sentiment_manual),
            'score': mlt_hit['_score'],
            'text': re.sub(r'\n+', ' ', mlt_hit['_source']['text_data'][:500])
        })
        total += 0
    print('\n----- uncategorized comment ------------------------------------------\n%s' % text)
    print('----- score %s/%s' % (score, mlt_size))
    print('----- hits=%s max_score=%s' % (mlt_response['hits']['total'], mlt_response['hits']['max_score']))
    print('----------------------------------------------------------------------')
    for match in matches:
        print('\t*%s*\t%s\t%s' % (match['value'], match['score'], match['text']))
