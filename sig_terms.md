# Signifcant terms sentiment

with sample of comment data from 6/7-7/4 (~113K comments)
using comments tagged by [regex patterns](https://github.com/RagtagOpen/fccforensics/blob/master/server/fcc_analysis/analyzers.py#L14), stored in `analysis.titleii`

Run [signifcant terms query](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-significantterms-aggregation.html) with tagged comments:

## queries

### significant in comments regex-tagged positive vs negative

["neutrality", "net", "not", "do", "be", "protect", "by", "isps", "it", "keep"]

```
GET _search
{
  "size": 0,
  "query": {
    "term": {
      "analysis.titleii": true
    }
  },
  "aggregations": {
    "significantTerms": {
      "significant_terms": {
        "field": "text_data",
        "mutual_information": {
          "include_negatives": false,
          "background_is_superset": false
        },
        "background_filter": {
          "term": {
            "analysis.titleii": false
          }
        }
      }
    }
  }
}
```

### significant in comments regex-tagged negative vs positive

["bipartisan", "consensus", "obstructing", "smothering", "overreach", "bureaucratic", "obama's", "damaging", "unprecedented", "restore"]

### significant in comments regex-tagged positive vs untagged

["trusted", "tell", "neutrality", "job", "net", "stand", "despise", "escape", "cannot", "action"]

```
GET _search
{
  "size": 0,
  "query": {
    "term": {
      "analysis.titleii": true
    }
  },
  "aggregations": {
    "significantTerms": {
      "significant_terms": {
        "field": "text_data",
        "mutual_information": {
          "include_negatives": false,
          "background_is_superset": false
        },
        "background_filter": {
          "bool": {
            "must_not": {
              "exists": {
                "field": "analysis.titleii"
              }
            }
          }
        }
      }
    }
  }
}
```

### significant in comments regex-tagged negative vs untagged?

["obstructing", "smothering", "obama's", "unprecedented", "damaging", "imposed", "light", "20", "grab", "positive"]

### significant in comments regex-tagged positive vs all?

["neutrality", "net", "trusted", "tell", "stand", "keep", "cannot", "current", "place", "users"]

```
GET _search
{
  "size": 0,
  "query": {
    "term": {
      "analysis.titleii": true
    }
  },
  "aggregations": {
    "significantTerms": {
      "significant_terms": {
        "field": "text_data",
        "mutual_information": {
          "include_negatives": false
        }
      }
    }
  }
}
```

### significant in comments regex-tagged negative vs all?

["obstructing", "smothering", "obama's", "unprecedented", "damaging", "light", "imposed", "20", "grab", "positive"]

### all positive terms

['action', 'be', 'by', 'cannot', 'cannot', 'current', 'despise', 'do', 'escape', 'isps', 'it', 'job', 'keep', 'keep', 'net', 'net', 'net', 'neutrality', 'neutrality', 'neutrality', 'not', 'place', 'protect', 'stand', 'stand', 'tell', 'tell', 'trusted', 'trusted', 'users']

popular: keep, "net neutrality", stand, tell, trusted

## all negative

['20', '20', 'bipartisan', 'bureaucratic', 'consensus', 'damaging', 'damaging', 'damaging', 'grab', 'grab', 'imposed', 'imposed', 'light', 'light', "obama's", "obama's", "obama's", 'obstructing', 'obstructing', 'obstructing', 'overreach', 'positive', 'positive', 'restore', 'smothering', 'smothering', 'smothering', 'unprecedented', 'unprecedented', 'unprecedented']

popular: 20, damaging, grab, imposed, light, obama, obstructing, positive, smothering, unprecedented

## testing

Run [test_sig_terms.py](https://github.com/RagtagOpen/fccforensics/blob/master/server/fcc_analysis/experiments/test_sig_terms.py) and inspect results:

`python test_sig_terms.py --http://127.0.0.1:9200/ --order desc --limit 1000`
- get 1000 best matches
- write document id, text, and score to `test_desc.csv`

`python test_sig_terms.py --http://127.0.0.1:9200/ --order asc --limit 1000`
- get 1000 worst matches
- write document id, text, and score to `test_asc.csv`

## tagging

`fcc tag_sigterms --endpoint http://localhost:9200/ --limit 50000 `
- set sentiment to true for documents matching [query for significant terms](https://github.com/RagtagOpen/fccforensics/blob/master/server/fcc_analysis/sentiment.py#L12) which don't already have `analysis.sentiment_sig_terms_ordered` set




