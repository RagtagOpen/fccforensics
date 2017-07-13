from datetime import datetime, timedelta
import os
import sys

import argparse

from index import CommentIndexer
from analyze import CommentAnalyzer
from sentiment import SigTermsSentiment
from cluster import MLTClusterer

yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

parser = argparse.ArgumentParser(description='Fetch, index, and tag comments')
parser.add_argument(
    '--endpoint', dest='endpoint',
    default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
)
parser.add_argument(
    '--date', dest='date', help='Date in yyyy-mm-dd format', default=yesterday
)
args = parser.parse_args(args=sys.argv[1:])

print('process comments for %s' % args.date)

# index
print('---- indexing')

indexer = CommentIndexer(lte=args.date, gte=args.date, endpoint=args.endpoint, start_offset=0)
total = indexer.run()
print('\nindexed %s comments\n' % total)

# analyze
print('---- analyzing')
dt = datetime.strptime(args.date, '%Y-%m-%d')

analyzer = CommentAnalyzer(endpoint=args.endpoint, date=dt, limit=total)
analyzed = analyzer.run()
print('\nanalyzed %s comments\n' % analyzed)

# preview sig terms
print('---- previewing sig terms')
terms = SigTermsSentiment(endpoint=args.endpoint, from_date=dt, to_date=(dt + timedelta(days=1)), limit=min([5000, total]))
terms.preview(fraction=0.1)

# cluster
print('---- find clusters')
cluster = MLTClusterer(endpoint=args.endpoint, date=dt)
cluster.run()
