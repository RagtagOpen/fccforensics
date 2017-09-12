from datetime import timedelta
import json
import multiprocessing

import warnings

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan
from elasticsearch.exceptions import ConnectionTimeout

from .analyzers import analyze


class CommentAnalyzer:

    def __init__(self, endpoint='http://localhost:9200/', verify=True, limit=10000, date=None):
        self.endpoint = endpoint
        self.verify = verify
        self.es = Elasticsearch(self.endpoint)
        self.limit = int(limit)
        self.indexed = 0
        self.date = date

    def run(self):
        in_queue = multiprocessing.Queue(maxsize=10000)
        out_queue = multiprocessing.Queue()
        tagging_processes = []

        for _ in range(5):
            process = multiprocessing.Process(target=self.tagging_worker, args=(in_queue, out_queue))
            process.start()
            tagging_processes.append(process)

        index_process = multiprocessing.Process(target=self.index_worker, args=(out_queue,))
        index_process.start()

        fetched = 0
        if self.date:
            query = {
              "query": {
                "range": {
                  "date_disseminated": {
                    "gte": self.date.strftime('%Y-%m-%d'),
                    "lt": (self.date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    "format": "yyyy-MM-dd"
                  }
                }
              }
            }
        else:
            query = {
              "query": {
                "bool": {
                    "must": [
                        {"term": {"analysis.source": "unknown"}}
                    ],
                  # "must_not": {
                  #   "exists": {
                  #     "field": "analysis"
                  #   }
                  # }
                }
              }
            }
        print(json.dumps(query))
        try:
            for doc in scan(self.es, index='fcc-comments', query=query, size=100):
                in_queue.put(doc['_source'])
                fetched += 1
                if not fetched % 250:
                    print('fetched %s/%s\t%s%%' % (fetched, self.limit, int(fetched/self.limit*100)))
                if fetched == self.limit:
                    break
        except ConnectionTimeout:
            print('error fetching: connection timeout')
        for _ in range(5):
            in_queue.put(None)

        for p in tagging_processes:
            p.join()

        out_queue.put(None)

        index_process.join()
        return fetched

    def tagging_worker(self, in_queue, out_queue):
        while True:
            comment = in_queue.get()
            if comment is None:
                break
            analysis = analyze(comment)
            # don't overwite existing analyis values
            # analysis.update(comment.get('analysis', {}))
            out_queue.put((comment['id_submission'], analysis))

    def index_worker(self, queue, size=200):
        actions = []
        indexed = 0
        while True:
            item = queue.get()
            if item is None:
                break
            id_submission, analysis = item

            doc = {
                '_index': 'fcc-comments',
                '_type': 'document',
                '_op_type': 'update',
                '_id': id_submission,
                'doc': {'analysis': analysis},
            }
            actions.append(doc)

            if len(actions) == size:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    try:
                        response = bulk(self.es, actions)
                        indexed += response[0]
                        print('\tanalyzed %s/%s\t%s%%' % (indexed, self.limit,
                            int(indexed / self.limit * 100)))
                        actions = []
                    except ConnectionTimeout:
                        print('error indexing: connection timeout')

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            response = bulk(self.es, actions)
            indexed += response[0]
            print('indexed %s' % (indexed))
