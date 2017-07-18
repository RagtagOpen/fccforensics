# FCC Forensics
Determine public opinion on net neutrality issue via sourcing and sentiment analysis of FCC comments.

Based on https://github.com/csinchok/fcc-comment-analysis, plus more from Ragtag volunteers

Uses [Elasticsearch](https://www.elastic.co/) to get data from [FCC's public API](https://www.fcc.gov/ecfs/public-api-docs.html)

## Queries

- `analysis.titleii` from [regex patterns](https://github.com/RagtagOpen/fccforensics/blob/master/server/fcc_analysis/analyzers.py#L14)
- `analysis.sentiment_sig_terms_ordered` from [significant terms](https://github.com/RagtagOpen/fccforensics/blob/master/sig_terms.md)
- query by source [AWS Lambda](https://github.com/RagtagOpen/fccforensics/blob/master/server/fcc_analysis/lambda.py)
- [tag_by_query.py](https://github.com/RagtagOpen/fccforensics/blob/master/server/fcc_analysis/experiements/tag_by_query.py)

## Local setup

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

[Analyze data](https://github.com/RagtagOpen/fccforensics/blob/master/server/fcc_analysis/analyzers.py) and add to `analysis` section of documents:

    $ fcc analyze --endpoint=http://localhost:9200/ --limit 40000

Set up a local Kibana server: https://www.elastic.co/downloads/kibana

Play in Kibana:
- go to http://localhost:5601
- go to Management / Configure an index pattern
  - Index name or pattern: `fcc-comments`
  - [x] Index contains time-based events
  - Time-field name: `date_dissemenated`
  - Create

[Contribute!](https://ragtag.org/connect)


## Production setup

Set up cloud-hosted Elasticsearch:
- read-only user for queries
- read-write user for ingest and analyze
- get ES_URL like https://user:password@hostname:port

Load current dataset into index:
- create index: `fcc create --endpoint=$ES_URL`
- fetch comments from FCC and add to index: `fcc index --endpoint=$ES_URL -g 2017-05-01` (restart as needed if/when API times out)
- run static analyzers, 100k at a time: `fcc analyze --endpoint=$ES_URL --limit 100000` (repeat until all docs have analyzed: `curl '$ES_URL/_count?pretty'  -H 'Content-Type: application/json' -d'{"query":{"bool":{"must_not":{"exists":{"field":"analysis"}}}}}')`

Create AWS Lambda to refresh data:
- TODO

Create AWS Lambda to proxy Elasticsearch queries:
- `cd server/fcc_analysis`
- `zip -r ../lambda.zip . --exclude experiments/*`
- `cd $VIRTUAL_ENV/lib/python3.6/site-packages`
- `zip -r path/to/server/lambda.zip .`
- upload to AWS; set handler to `lambda.query_by_source`

Create AWS API Gateway to proxy Lambda function

