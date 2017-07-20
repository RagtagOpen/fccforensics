import requests

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q, FunctionScore, SF

import time


class BreachChecker:

    def __init__(self, endpoint='http://localhost:9200/'):
        self.es = Elasticsearch(endpoint)
        self.last_call = time.time()

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

        if response.status_code == 404:
            return False

        for breach in response.json():
            if 'Physical addresses' in breach['DataClasses']:
                return True
        
        return True


    def run(self):
        s = Search(using=self.es)

        while True:
            s.query = FunctionScore(
                query=s.query, functions=[SF('random_score', seed=int(time.time()))]
            )
            s = s.exclude('exists', field='analysis.breached')

            for filing in s[:10]:
                
                if not filing['contact_email']:
                    breached = False
                else:
                    breached = self.is_breached(filing['contact_email'])
                
                self.es.update(
                    index='fcc-comments', doc_type='document', id=filing['id_submission'],
                    body={
                        'doc': {
                            'analysis': {'breached': breached}
                        }
                    }
                )
