from elasticsearch.helpers import bulk

def bulk_update(es, actions, batch_size=250):
    indexed = 0
    for i in range(0, len(actions), batch_size):
        resp = bulk(es, actions[i:(i+batch_size)])
        indexed += resp[0]
        print('\tindexed %s / %s' % (indexed, len(actions)))
    return indexed


def bulk_update_doc(doc_id, analysis):
    return {
        '_index': 'fcc-comments',
        '_type': 'document',
        '_op_type': 'update',
        '_id': doc_id,
        'doc': { 'analysis': analysis }
    }

