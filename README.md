# FCC Forensicso
Determine public opinion on net neutrality issue via sourcing and sentiment analysis of FCC comments.

Based on https://github.com/csinchok/fcc-comment-analysis, plus more from Ragtag volunteers

Uses [Elasticsearch](https://www.elastic.co/) to get data from [https://www.fcc.gov/ecfs/public-api-docs.html](FCC's public API)

## Setup

Make sure you have python3

Set up a local Elasticsearch server: https://www.elastic.co/downloads/elasticsearch

Set up a local Kibana server: https://www.elastic.co/downloads/kibana

Set up `fcc-comment-analysis`:

    $ cd server
    $ pip install -e .
    $ python setup.py test

Fetch and index some data from the FCC API:

    $ fcc index --endpoint=http://localhost:9200/ -g 2017-06-01

Analyze data and add to `analysis` section of documents:

    $ fcc analyze --endpoint=http://localhost:9200/

Play in Kibana/command line/your tool of choice

Contribute!
