import os

from breached import BreachChecker
import tags

endpoint = os.environ['ES_ENDPOINT']
failed = []
for source in tags.sources['positive'] + tags.sources['negative']:
    b = BreachChecker(endpoint=endpoint, source=source, limit=1000)
    try:
        b.run()
    except:
        failed.append(source)
print('Failed sources: {}'.format(failed))
