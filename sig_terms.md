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

## misses

matched by query, but should be negative

About 300k into sig terms relevance, 62k identical comments, tagged `bot.american-jobs`

> The free-market Internet was an incredible engine of economic growth, innovation, and job creation since the 1990s and has already been substantially slowed by the 2015 Net Neutrality rules. The slowdown in investment is destroying jobs and risks a big future tax hike to make up for lost private investment. Save American jobs by repealing Net Neutrality

10603304789399  460k in, tagged `bot.best_cop`

> The Title II order created a gaping gap in privacy protections by taking the best cop, the FTC, off the beat. That is reason enough to support Chairman Pai's proposal to restore Internet freedom. Restore privacy by repealing Net Neutrality.

1060351723564, tagged `bot.economics_free_zone`

> The FCC's Net Neutrality rules were written in the Obama White House by political staff and Tech Industry special interests who overruled the FCC's own experts. The FCC's own chief economist Tim Brennan called the rules "an economics-free zone." They should be repealed.

tagged `bot.corrupt_result`

> Obama's Net Neutrality order was the corrupt result of a corrupt process controlled by Silicon Valley special interests. It gives some of the biggest companies in the world a free ride at the expense of consumers and should be immediately repealed!


## tagging

    export ES_ENDPONT="http://localhost:9200/"
    cd server/fcc_analysis

review 1%:

    cd experiments
    python print.py --limit 5000 --sample 1 | more
    cd ..

set `analysis.sentiment_sig_terms_ordered` to true for top matches of [query for significant terms](https://github.com/RagtagOpen/fccforensics/blob/master/server/fcc_analysis/sentiment.py#L12)

    fcc tag_sigterms --limit 5000

repeat



