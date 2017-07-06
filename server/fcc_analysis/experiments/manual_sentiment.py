import json
import os
import re
import sys

import argparse
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

'''
to bootstrap MLT sentiment, manually add sentiment to bot-generated comments like these that are too varied for regex sentiment

Dear Mr. Pai,  I'm a voter worried about Internet Freedom. I would like to advocate the FCC to overturn Barack Obama's order to control broadband. Individual citizens, as opposed to big government, should be free to purchase which services they want. Barack Obama's order to control broadband is a perversion of net neutrality. It disrupted a free-market framework that performed exceptionally successfully for two decades with Republican and Democrat consensus.

Dear Commissioners:  I'm a voter worried about Network Neutrality. I strongly request the government to overturn Barack Obama's power grab to control Internet access. Individual citizens, not so-called experts, deserve to enjoy which products we want. Barack Obama's power grab to control Internet access is a betrayal of the open Internet. It ended a free-market framework that performed supremely successfully for two decades with Republican and Democrat support.

FCC:  I am concerned about Internet Freedom. I would like to recommend you to overturn Barack Obama's order to regulate Internet access. Individuals, not big government, should buy which applications we choose. Barack Obama's order to regulate Internet access is a betrayal of net neutrality. It stopped a market-based framework that worked very successfully for two decades with Republican and Democrat consensus.
'''

parser = argparse.ArgumentParser(description='Add analysis.sentiment_manual to specified ids')
parser.add_argument(
    '--endpoint', dest='endpoint',
    default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
)
parser.add_argument('--pro', dest='sentiment', action='store_true')
parser.add_argument('--con', dest='sentiment', action='store_false')
parser.set_defaults(sentiment=True)
parser.add_argument(
    '--ids', dest='ids', nargs='+')
args = parser.parse_args(args=sys.argv[1:])

actions = []
for doc_id in args.ids:
    doc = {
        '_index': 'fcc-comments',
        '_type': 'document',
        '_op_type': 'update',
        '_id': doc_id,
        'doc': { 'analysis': { 'sentiment_manual': args.sentiment } },
    }
    actions.append(doc)

es = Elasticsearch(args.endpoint)
#print(actions)
print(bulk(es, actions))
