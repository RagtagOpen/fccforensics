import json

sources = {
    'positive': [
        "form.battleforthenet", "reddit.technology", "blog.venturebeat",
        "bot.internetuser", "form.dearfcc", "bot.illogically-named", "form.signforgood",
        "form.freepress", "form.demandprogress", "bot.maga", "bot.dissapear",
        "bot.telecommunications_act", "bot.thenewsearchengine"],
    'negative': [
        "bot.american-jobs", "bot.unprecedented", "bot.outraged",
        "form.diminished-investment", "form.freeourinternet", "form.fwact",
        "form.tpa", "bot.best_cop", "bot.economics_free_zone", "bot.corrupt_result",
        "bot.recursive"]
}
sources = {
    'positive': [
        "form.battleforthenet", "reddit.technology", "blog.venturebeat", "bot.internetuser",
        "form.dearfcc", "bot.illogically-named", "form.signforgood", "form.freepress",
        "form.demandprogress", "bot.maga", "bot.dissapear", "bot.telecommunications_act",
        "bot.thenewsearchengine", "es_terms_positive", "form.aclu"],
    'negative': [
        "bot.american-jobs", "bot.unprecedented", "bot.outraged",
        "form.diminished-investment", "form.freeourinternet", "form.fwact", "form.tpa",
        "bot.best_cop", "bot.economics_free_zone", "bot.corrupt_result", "bot.recursive",
        "form.att", "bot.telephone_monopoly", "bot.titleii_takeover", "es_terms_negative"]
}

clusters = {
    'positive': [
        "1070716784137", "10707215368462", "10707899924781", "1070776003187",
        "10711874306044", "10707195721037", "1071141320641", "1070509290734",
        "10705304876386", "1070582875194", "1070332270088", "10702015723088",
        "10703294387511", "1070324671992", "10702904327391", "10703278645373",
        "1070233724746", "10703281901293", "107032192222724", "106301472510887",
        "1071162047564", "1071132812147", "1071187695044", "1070109348420",
        "1071007072655", "1071137256523", "1070231995193", "10701743109988",
        "107021773230200", "1070586119275", "1071230742496", "107122699505722",
        "1071236700048", "107122001717563", "1071274112278", "10712267103147",
        "10712021008392"],
    'negative': ["1071290443881"],
}

queries = {
    'positive': {
        'query': {
            'bool': {
                'filter': {
                    'bool': {
                        'minimum_should_match': 1,
                        'should': [
                            {'term': {'analysis.sentiment_manual': True}},
                            {'term': {'analysis.titleii': True}},
                            {'term': {'analysis.sentiment_sig_terms_ordered': True}},
                            {'terms': {'analysis.source': sources['positive']}},
                            {'terms': {'analysis.more_like_this.src_doc_id': clusters['positive']}}
                        ]
                    }
                }
            }
        }
    },
    'negative': {
        'query': {
            'bool': {
                'filter': {
                    'bool': {
                        'minimum_should_match': 1,
                        'should': [
                            {'term': {'analysis.sentiment_manual': False}},
                            {'term': {'analysis.titleii': False}},
                            {'term': {'analysis.sentiment_sig_terms_ordered': False}},
                            {'terms': {'analysis.source': sources['negative']}},
                            {'terms': {'analysis.more_like_this.src_doc_id': clusters['negative']}}
                        ]
                    }
                }
            }
        }
    },
    'untagged': {
        'query': {
            'bool': {
                'filter': {
                    'bool': {
                        'must': [
                            {'term': {'analysis.source': 'unknown'}},
                        ],
                        'must_not': [
                            {'exists': {'field': 'analysis.sentiment_manual'}},
                            {'exists': {'field': 'analysis.titleii'}},
                            {'exists': {'field': 'analysis.sentiment_sig_terms_ordered'}},
                            {'terms': {'analysis.more_like_this.src_doc_id': clusters['negative'] +
                                                                             clusters['positive']}}
                        ]
                    }
                }
            }
        }
    }
}

if __name__ == '__main__':
    for key in queries:
        print('%s\t%s\n' % (key, json.dumps(queries[key])))
