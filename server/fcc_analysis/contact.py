import csv
import json
import os
import time

from elasticsearch import Elasticsearch

import tags

'''
get 200 randomly chosen email address fom each source

write to csv: sentiment_source.csv: email, name, date, comment, and url
'''
es = Elasticsearch(os.environ['ES_ENDPOINT'], timeout=30)

query = {
  "_source": [
    "date_received",
    "contact_email",
    "text_data",
    "filers.name"
  ],
  "query": {
    "function_score": {
      "query": {
        "bool": {
          "must_not": [
            {
              "term": {
                "contact_email.keyword": ""
              }
            }
          ],
          "must": [
            {
              "term": {
                "analysis.source": ""
              }
            },
            {
              "exists": {
                "field": "contact_email"
              }
            }
          ]
        }
      },
      "random_score": {
        "seed": int(time.time())
      }
    }
  }
}

def run_query(src, fn, rows=200):
    print('writing data for %s to %s' % (source, fn))
    query['query']['function_score']['query']['bool']['must'][0]['term']['analysis.source'] = source
    emails = set()
    batches = 0
    print(json.dumps(query))
    total = None
    with open(fn, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['email', 'name', 'date', 'comment', 'url'])
        while len(emails) < rows and batches < 10:
            offset = batches * 100
            if total and offset > total:
                break
            resp = es.search(index='fcc-comments', body=query, size=100, from_=offset)
            if batches == 0:
                total = resp['hits']['total']
                print('\t%s matches' % (total))
            else:
                print('\tbatch %s: have %s' % (batches+1, len(emails)))
            batches += 1
            for doc in resp['hits']['hits']:
                if len(emails) == rows:
                    break
                data = doc['_source']
                if data['contact_email'] in emails:
                    continue
                emails.add(data['contact_email'])
                writer.writerow([data['contact_email'], data['filers'][0]['name'],
                    data['date_received'], data['text_data'],
                    'https://www.fcc.gov/ecfs/filing/%s' % doc['_id']
                ])

if __name__ == '__main__':
    '''
    for source in tags.sources['positive']:
        run_query(source, 'positive_%s.csv' % source.replace('.', '_'))

    for source in tags.sources['negative']:
        run_query(source, 'negative_%s.csv' % source.replace('.', '_'))
    '''
    sources = ['form.freepress', 'bot.illogically-named', 'form.aclu', 'form.aclu']
    for source in sources:
      run_query(source, 'contact_%s.csv' % source.replace('.', '_'))
