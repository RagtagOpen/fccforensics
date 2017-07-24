from datetime import datetime
import json
import time

import requests

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import FunctionScore, SF

import lib

class BreachChecker:

    def __init__(self, endpoint='http://localhost:9200/', source=None, limit=100):
        self.es = Elasticsearch(endpoint)
        self.last_call = time.time()
        self.source = source
        self.limit = limit

    def is_breached(self, email):
        # We can only call the API once every 1.5 seconds
        sleep_time = self.last_call + 1.5 - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

        endpoint = 'https://haveibeenpwned.com/api/v2/breachedaccount/{}'.format(email)

        response = requests.get(endpoint, headers={
            'User-Agent': 'RagTag FCC Forensics (https://github.com/RagtagOpen/fccforensics)'
        })
        self.last_call = time.time()

        print('\t%s\t%s' % (email, response))
        if response.status_code == 404:
            return False

        for breach in response.json():
            if 'Physical addresses' in breach['DataClasses']:
                return True
        return True

    def tag_by_email(self, emails, breached):
        docs = []
        s = Search(using=self.es).\
            filter(Q({'terms': {'contact_email.keyword': emails}})).\
            source(['id_submission'])
        print('%s emails breached=%s' % (len(emails), breached))
        for hit in s.scan():
            docs.append(lib.bulk_update_doc(hit['id_submission'], {'breached': breached}))
            if not len(docs) % 500:
                print('\tfetched %s' % len(docs))
        print('\t%s matches' % len(docs))
        return docs

    def run(self):
        emails = {
            'breached': set(),
            'unbreached': set(),
        }
        # contact_email exists
        must = [Q('exists', field='contact_email')]
        # matches source if specified
        if self.source:
            must.append(Q({'term': {'analysis.source': self.source}}))
        # not already tagged with breached
        s = Search(using=self.es).\
            query(FunctionScore(
                  query=Q('bool',
                          must=must,
                          must_not=[Q('exists', field='analysis.breached')]),
                  functions=[SF('random_score', seed=int(time.time()))]
            )).\
            source(['contact_email'])
        print('%s breached: source=%s limit=%s' % (datetime.now().isoformat(), self.source,
            self.limit))
        print('query=\n%s' % json.dumps(s.to_dict()))
        for filing in s[:self.limit]:
            email = filing['contact_email']
            if not email or email in emails['breached'] or email in emails['unbreached']:
                continue
            breached = self.is_breached(email)
            emails['breached' if breached else 'unbreached'].add(email)
        docs = []
        print('done source=%s' % self.source)
        if emails['breached']:
            docs += self.tag_by_email(list(emails['breached']), True)
        if emails['unbreached']:
            docs += self.tag_by_email(list(emails['unbreached']), False)
        try:
            lib.bulk_update(self.es, docs)
        except Exception as e:
            print('error indexing: %s' % e)
