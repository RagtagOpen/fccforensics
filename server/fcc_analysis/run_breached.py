import os

from breached import BreachChecker
import tags

endpoint = os.environ['ES_ENDPOINT']
for source in tags.sources['positive'] + tags.sources['negative']:
    b = BreachChecker(endpoint=endpoint, source=source, limit=100)
    b.run()
