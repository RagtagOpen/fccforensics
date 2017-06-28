import json
import multiprocessing
from tqdm import tqdm
import requests
import warnings
import io

from .analyzers import analyze


class CommentAnalyzer:

    def __init__(self, endpoint='http://localhost:9200/', verify=True):
        self.endpoint = endpoint
        self.verify = verify

    def run(self):
        in_queue = multiprocessing.Queue(maxsize=1000)
        out_queue = multiprocessing.Queue()
        tagging_processes = []

        for _ in range(5):
            process = multiprocessing.Process(target=self.tagging_worker, args=(in_queue, out_queue))
            process.start()
            tagging_processes.append(process)

        index_process = multiprocessing.Process(target=self.index_worker, args=(out_queue,))
        index_process.start()

        try:
            for comment in self.iter_comments(size=100):
                in_queue.put(comment)
        except KeyboardInterrupt:
            pass

        for _ in range(5):
            in_queue.put(None)

        for p in tagging_processes:
            p.join()

        out_queue.put(None)

        index_process.join()

    def tagging_worker(self, in_queue, out_queue):

        while True:
            comment = in_queue.get()
            if comment is None:
                break
            analysis = analyze(comment)
            out_queue.put((comment['id_submission'], analysis))

    def index_worker(self, queue, size=250):

        url = '{}{}/filing/{}'.format(
            self.endpoint,
            'fcc-comments',
            '_bulk'
        )

        payload = io.StringIO()
        counter = 0
        while True:
            item = queue.get()
            if item is None:
                print('exiting...')
                break
            id_submission, analysis = item

            index = {"update": {"_id": id_submission}}
            payload.write(json.dumps(index))
            payload.write('\n')
            payload.write(json.dumps({'doc': {'analysis': analysis}}))
            payload.write('\n')

            counter += 1
            if counter % size == 0:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    response = requests.post(url, data=payload.getvalue(), verify=self.verify)
                    if 'items' not in response.json():
                        print(response.json())
                    else:
                        for item in response.json()['items']:
                            if 'update' in item and item['update'].get('result') not in ('updated', 'noop'):
                                print(json.dumps(item, indent=2))
                                raise Exception('Failure!')
                    if response.status_code != 200:
                        print(response.text)
                        return
                payload = io.StringIO()
                counter = 0

    def iter_comments(self, timeout='5m', size=100, progress=True):
        start_url = '{}fcc-comments/filing/_search?scroll={}'.format(
            self.endpoint, timeout
        )
        scroll_url = '{}_search/scroll'.format(self.endpoint)
        headers={'Content-Type': 'application/json'}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = requests.post(start_url, verify=self.verify, headers=headers, data=json.dumps({
                'size': size,
                'query': {
                    'match_all': {}
                },
                'sort': [
                    '_doc'
                ]
            }))
        scroll_id = response.json()['_scroll_id']
        progress = tqdm(total=response.json()['hits']['total'])
        hits = response.json()['hits']['hits']
        idx = 0
        while hits:

            for hit in hits:
                yield hit['_source']
                progress.update(1)

            if not scroll_id:
                break
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                response = requests.post(scroll_url, headers=headers, verify=self.verify, data=json.dumps({
                    'scroll': timeout,
                    'scroll_id': scroll_id
                }))

            idx += 1
            data = response.json()
            scroll_id = data.get('_scroll_id', None)
            hits = data.get('hits', {}).get('hits', [])

        progress.close()

