# server scripts

Ingest, update, and analyze comments from https://www.fcc.gov/ecfs/public-api-docs.html

Based on https://github.com/csinchok/fcc-comment-analysis

Set up `fcc-comment-analysis`:

    $ cd server
    $ pip install -e .
    $ python setup.py test

Create the index with mappings:

    $ fcc create

Fetch and index some data from the FCC API:

    $ fcc index --endpoint=http://localhost:9200/ -g 2017-06-01

Analyze data and add to `analysis` section of documents:

    $ fcc analyze --endpoint=http://localhost:9200/
