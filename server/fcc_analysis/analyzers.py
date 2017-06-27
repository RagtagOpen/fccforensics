import re

WORDSPLIT_PATTERN = re.compile("['-]+", re.UNICODE)
NON_CHAR_PATTERN = re.compile('[^a-z ]+', re.UNICODE)


# I know...now I have two problems...
OLIVER_PATTERNS = [
    re.compile('(strong )?net neutrality( rules)? backed by title (ii|2|two|ll)', flags=re.IGNORECASE),
    re.compile('i( specifically| strongly)? support( strong)? net neutrality backed by title', flags=re.IGNORECASE),
    re.compile('i( specifically| strongly)? support( strong)? net neutrality,?( oversight)?( backed)? by title (ii|2|two|ll) oversight', flags=re.IGNORECASE),
]

PRO_TITLE_II_PATTERNS = [
    re.compile('(preserve|keep|maintain|uphold|continue|protect)( net)? neutral(ity)?', flags=re.IGNORECASE),
    re.compile('(preserve|keep|maintain|uphold|continue|protect) title (ii|2|two|ll)?', flags=re.IGNORECASE),
    re.compile('I( strongly)? support title (2|ii|two|ll)', flags=re.IGNORECASE),
    re.compile('I( strongly| specifically)? support( strong)? net neutrality', flags=re.IGNORECASE),
    re.compile('(strongly|specifically) support (net neutrality|title (ii|2|two|ll))', flags=re.IGNORECASE),
    re.compile('do not (repeal|revoke|remove)', flags=re.IGNORECASE)
]

ANTI_TITLE_II_PATTERNS = [
    re.compile('obama\'?s internet takeover', flags=re.IGNORECASE),
    re.compile('please reverse the (2014|2015)', flags=re.IGNORECASE),
    re.compile('please roll ?back', flags=re.IGNORECASE),
]

SMART_BOT_PATTERNS = [
    re.compile("It (undid|broke|disrupted|stopped|reversed|ended) a (market-based|pro-consumer|free-market|hands-off|light-touch) (policy|approach|system|framework) that (performed|functioned|worked) (fabulously|exceptionally|very, very|very|supremely|remarkably) (smoothly|successfully|well) for (many years|a long time|two decades|decades) with (Republican and Democrat|bipartisan|both parties'|nearly universal|broad bipartisan) (consensus|approval|backing|support)")
]


def ingestion_method(comment):

    if comment.get('browser', '').startswith('OpenCSV'):
        return 'csv'

    for proceeding in comment['proceedings']:
        if '_index' in proceeding:
            return 'direct'

    return 'api'


def source(comment):
    '''Returns a string identifying the "source" of this comment, if possible.

    For example:

      - bot.unprecedented
      - johnoliver
      - form.battleforthenet

    '''
    if 'text_data' not in comment:
        return

    if comment['text_data'].startswith('The unprecedented regulatory power the Obama Administration imposed on the internet'):
        return 'bot.unprecedented'

    if comment['text_data'].startswith('I was outraged by the Obama/Wheeler FCC'):
        return 'bot.outraged'

    # This one is interesting, because it appends the Submitter's first name to the text_data, making the fingerprint unreliable...
    if comment['text_data'].startswith('The FCC Open Internet Rules (net neutrality rules) are extremely important to me'):
        return 'form.battleforthenet'

    if 'my understanding that the FCC Chairman intends to reverse net neutrality rules' in comment['text_data']:
        return 'reddit.technology'

    if 'i support the existing net neutrality rules, which classify internet service providers under the title i' in comment['text_data'].lower():
        return 'blog.venturebeat'

    if comment['text_data'].startswith('Obama’s Title II order has diminished broadband investment'):
        return 'form.diminished-investment'

    if 'passed rules treating the internet as a government regulated public utility for the first time in history' in comment['text_data'].lower():
        return 'form.freeourinternet'

    if comment['text_data'].startswith('In 2015, wealthy leftist billionaires and powerful Silicon Valley monopolies took the internet'):
        return 'form.freeourinternet'

    if 'Dear Express Restoring Internet Freedom,' in comment['text_data']:
        return 'form.fwact'

    if comment['text_data'].startswith('Obama\'s Federal Communications Commission (FCC) forced regulations on the internet that put the government'):
        return 'form.tpa'

    if 'These rules have cost taxpayers, slowed down broadband infrastructure investment, and hindered competition and choice for Americans' in comment['text_data']:
        return 'form.tpa'

    if "The FCC should throw out Chairman Ajit Pai's proposal to give the ISP monopolies" in comment['text_data']:
        return 'bot.internetuser'

    if 'The FCC needs to stand up for Internet users like me and keep the net neutrality rules that are already in effect.' in comment['text_data']:
        return 'form.dearfcc'

    if comment['text_data'].startswith('This illogically named "restoring internet freedom" filing is aimed squarely at the freedom of the internet'):
        return 'bot.illogically-named'

    if comment['text_data'].startswith('Don\'t kill net neutrality. We deserve a free and open Internet'):
        return 'form.signforgood'

    if comment['text_data'].startswith('Net Neutrality is not negotiable'):
        return 'form.freepress'

    if comment['text_data'].startswith('A free and open internet is critical for Americans to connect with their friends and family, exercise their freedom of speech'):
        return 'form.demandprogress'

    try:
        last_sentence = comment['text_data'].split('.')[-2].strip()
    except IndexError:
        pass
    else:
        for pattern in SMART_BOT_PATTERNS:
            if pattern.match(last_sentence):
                return 'bot.recursive'

    # This is the text that John Oliver suggested. Many people seemed to follow his suggestion.
    for pattern in OLIVER_PATTERNS:
        if pattern.search(comment['text_data']):
            return 'johnoliver'

    return 'unknown'


def titleii(comment):

    if 'text_data' not in comment:
        return None

    for pattern in PRO_TITLE_II_PATTERNS:
        if pattern.search(comment['text_data']):
            return True

    for pattern in ANTI_TITLE_II_PATTERNS:
        if pattern.search(comment['text_data']):
            return False

    return None


def capsemail(comment):
    if comment.get('contact_email'):
        return comment['contact_email'] == comment['contact_email'].upper()


def fulladdress(comment):

    address = comment.get('addressentity', {})
    for key in ('address_line_1', 'city', 'state', 'zip_code'):
        if not address.get(key):
            return False
    return True


def fingerprint(comment):
    '''Get a text fingerprint--useful for looking for duplicate text'''

    text = comment.get('text_data', '').lower()
    text = WORDSPLIT_PATTERN.sub('', text)
    text = NON_CHAR_PATTERN.sub(' ', text)
    words = list(set(text.split()))
    words.sort()
    return " ".join(words)[:1000]  # Some people are assholes...


def proceeding_keys(comment):
    if 'proceedings' not in comment:
        return
    keys = []
    for proceeding in comment['proceedings']:
        sorted_keys = sorted(list(proceeding.keys()))
        keys.extend(sorted_keys)
    return ' '.join(keys)


def onsite(comment):
    if 'proceedings' not in comment:
        return
    for proceeding in comment['proceedings']:
        if '_index' in proceeding:
            return True
    return False


def analyze(comment):

    analysis = {
        'fingerprint': fingerprint(comment),
        'fulladdress': fulladdress(comment),
        'capsemail': capsemail(comment),
        # 'titleii': titleii(comment),
        'source': source(comment),
        'proceedings_keys': proceeding_keys(comment),
        'onsite': onsite(comment),
        'ingestion_method': ingestion_method(comment)
    }

    source_mapping = {
        'bot.unprecedented': False,
        'bot.outraged': False,
        'form.diminished-investment': False,
        'form.freeourinternet': False,
        'form.fwact': False,
        'form.tpa': False,
        'bot.recursive'

        'johnoliver': True,
        'form.battleforthenet': True,
        'reddit.technology': True,
        'blog.venturebeat': True,
        'form.dearfcc': True,
        'form.signforgood': True,
        'form.demandprogress': True
    }
    if analysis['source'] in source_mapping:
        analysis['titleii'] = source_mapping[analysis['source']]

    if 'titleii' not in analysis:

        titleii_sent = titleii(comment)
        if titleii_sent is not None:
            analysis['titleii'] = titleii_sent

    return analysis
