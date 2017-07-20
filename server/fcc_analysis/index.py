from datetime import datetime
import itertools
import json
import warnings
import multiprocessing

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import requests

from . import mappings
from analyzers import analyze

class CommentIndexer:

    def __init__(self, lte=None, gte=None, limit=250, sort='date_disseminated,ASC', fastout=False, verify=True, endpoint='http://127.0.0.1/', start_offset=0):
        if gte and not lte:
            lte = datetime.now().isoformat()
        if lte and not gte:
            gte = '2000-01-01'
        self.lte = lte
        self.gte = gte
        self.limit = limit
        self.sort = sort
        self.fastout = fastout
        self.verify = verify
        self.endpoint = endpoint
        self.fcc_endpoint = 'https://ecfsapi.fcc.gov/filings'
        self.index_fields = mappings.FIELDS.keys()
        self.es = Elasticsearch(self.endpoint)
        self.start_offset = start_offset
        self.stats = {'indexed': start_offset, 'fetched': start_offset}

    def run(self):
        self.total = self.get_total() or 5000000
        if not self.total:
            print('error loading document total; using estimate')

        index_queue = multiprocessing.Queue()

        bulk_index_process = multiprocessing.Process(
            target=self.bulk_index, args=(index_queue,),
        )
        bulk_index_process.start()

        for comment in self.iter_comments():
            self.stats['fetched'] += 1
            if not self.stats['fetched'] % 100:
                print('fetched %s/%s\t%s%%\t%s' % (self.stats['fetched'], self.total,
                    int(self.stats['fetched'] / self.total * 100),
                    comment['date_disseminated']))
            index_queue.put(comment)

        index_queue.put(None)
        bulk_index_process.join()
        return self.stats['fetched']

    def build_query(self):
        query = {
            'proceedings.name': '17-108',
            'sort': self.sort
        }
        if self.lte and self.gte:
            query['date_disseminated'] = '[gte]{gte}[lte]{lte}'.format(
                gte=self.gte,
                lte=self.lte
            )
        return query

    def get_total(self):
        query = self.build_query()
        query['limit'] = 1
        print('%s?%s' % (self.fcc_endpoint, query))
        response = requests.get(self.fcc_endpoint, params=query)
        try:
            agg = response.json().get('aggregations', {})
            if not agg:
                return None
            for bucket in agg.get('proceedings_name', {}).get('buckets', []):
                if bucket['key'] == query['proceedings.name']:
                    return bucket['doc_count']
        except json.decoder.JSONDecodeError:
            return None
        return None


    def iter_comments(self, page=0):
        query = self.build_query()
        for page in itertools.count(0):
            query.update({
                'limit': self.limit,
                'offset': page * self.limit + self.start_offset,
            })
            response = requests.get(self.fcc_endpoint, params=query)
            try:
                filings = response.json().get('filings', [])
            except json.decoder.JSONDecodeError:
                print('error decoding results: %s' % response)
                break
            for filing in filings:
                # don't want to keep all of the giant proceedings array
                proceedings = []
                for proc in filing['proceedings']:
                    idx = proc.get('_index', None)
                    if idx:
                        proceedings.append({'_index': idx})
                for exclude in filing.keys() - self.index_fields:
                    filing.pop(exclude, None)
                filing['proceedings'] = proceedings
                filing.pop('_index', None)
                yield filing

            if len(filings) != self.limit:
                break

    def bulk_index(self, queue):

        actions = []

        while True:
            document = queue.get()
            if document is None:
                print('nothing in the queue')
                break

            document['analysis'] = analyze(document)
            doc = {
                '_index': 'fcc-comments',
                '_type': 'document',
                '_id': document['id_submission'],
                '_source': document
            }
            actions.append(doc)

            if len(actions) == 250:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    response = bulk(self.es, actions)
                    self.stats['indexed'] += response[0]
                    print('\tindexed %s/%s\t%s%%' % (self.stats['indexed'], self.total,
                        int(self.stats['indexed'] / self.total * 100)))
                    actions = []

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            response = bulk(self.es, actions)
            self.stats['indexed'] += response[0]
            print('\tindexed %s\t%s' % (self.stats['indexed'], self.total))

        return self.stats['indexed']
