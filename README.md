# FCC Forensics
Determine public opinion on net neutrality issue via sourcing and sentiment analysis of FCC comments.

Based on https://github.com/csinchok/fcc-comment-analysis, plus more from Ragtag volunteers

Uses [Elasticsearch](https://www.elastic.co/) to get data from [FCC's public API](https://www.fcc.gov/ecfs/public-api-docs.html)

## Setup

Make sure you have python3

Set up a local Elasticsearch server: https://www.elastic.co/downloads/elasticsearch

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

Set up a local Kibana server: https://www.elastic.co/downloads/kibana

Play in Kibana:
- go to http://localhost:5601
- go to Management / Configure an index pattern
  - Index name or pattern: `fcc-comments`
  - [x] Index contains time-based events
  - Time-field name: `date_dissemenated`
  - Create

[Contribute!](https://ragtag.org/connect)

