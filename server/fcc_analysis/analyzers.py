import re

from fcc_analysis import tags

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

    for proceeding in comment.get('proceedings', []):
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
        return 'empty'

    if 'proposal to reverse net neutrality protections because a free and open internet is vital for our democracy' in comment['text_data']:
        return 'form.aclu'

    # from http://about.att.com/sites/open_internet
    att_messages = [
        'I am writing in regard to the Commission’s work on preserving an open internet',
        'there is a right way and a wrong way to preserve the concept of an open internet',
        'While the internet has drastically changed over the years, our internet regulations remain outdated',
        'the open internet is compromised when partisan politics and regulatory uncertainty come into play',
        'overturn the existing burdensome rules at the FCC and enact lasting legislation',
        'time for Congress to provide clear direction by passing legislation that provides certainty',
        'overturn the current law designed 80 years ago, before the Internet was created, is a great first step',
        'our internet regulations remain outdated',
        'heavy-handed regulations will do more harm than good',
        'get rid of the rules that were harming the internet economy',
        'urge you to work with your fellow members of Congress and the FCC to permanently preserve an open internet by supporting bipartisan legislation',
        'believe only legislation can ensure we have permanent, enforceable open internet rules',
        'Bipartisan legislation can help end the years-long political back-and-forth',
        'get rid of the rules that unfairly and heavy-handedly enforced these principles'
    ]
    for msg in att_messages:
        if msg in comment['text_data']:
            return 'form.att'

    if 'Title II is a Depression-era regulatory framework designed for a telephone monopoly that no longer exists' in comment['text_data']:
        return 'bot.telephone_monopoly'

    if 'enable the federal government to exert an extraordinary and unnecessary amount of regulatory control' in comment['text_data']:
        return 'bot.titleii_takeover'

    if comment['text_data'].startswith('The unprecedented regulatory power the Obama Administration imposed on the internet'):
        return 'bot.unprecedented'

    if comment['text_data'].startswith('I was outraged by the Obama/Wheeler FCC'):
        return 'bot.outraged'

    if 'Open Internet Rules (net neutrality rules) are extremely important to me' in comment['text_data']:
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

    if comment['text_data'].startswith('Rapacious Silicon Valley monopolies like Amazon'):
        return 'form.freeourinternet'

    if 'Dear Express Restoring Internet Freedom,' in comment['text_data']:
        return 'form.fwact'

    if comment['text_data'].startswith('Obama\'s Federal Communications Commission (FCC) forced regulations on the internet that put the government'):
        return 'form.tpa'

    if 'enable the federal government to exert an extraordinary and unnecessary amount of regulatory control over the internet' in comment['text_data']:
        return 'form.tpa'

    if 'These rules have cost taxpayers, slowed down broadband infrastructure investment, and hindered competition and choice for Americans' in comment['text_data']:
        return 'form.tpa'

    if "The FCC should throw out Chairman Ajit Pai's proposal to give the ISP monopolies" in comment['text_data']:
        return 'bot.internetuser'

    if 'The FCC needs to stand up for Internet users like me and keep the net neutrality rules that are already in effect.' in comment['text_data']:
        return 'form.dearfcc'

    if 'plan to give the government-subsidized ISP monopolies like AT&T, Verizon, and Comcast the legal cover to throttle' in comment['text_data']:
        return 'form.dearfcc'

    if comment['text_data'].startswith('This illogically named "restoring internet freedom" filing is aimed squarely at the freedom of the internet'):
        return 'bot.illogically-named'

    if comment['text_data'].startswith('Don\'t kill net neutrality. We deserve a free and open Internet'):
        return 'form.signforgood'

    if comment['text_data'].startswith('Net Neutrality is not negotiable'):
        return 'form.freepress'

    if comment['text_data'].startswith('Cable and phone companies provide access to the internet'):
        return 'form.freepress2'

    if comment['text_data'].startswith('A free and open internet is critical for Americans to connect with their friends and family, exercise their freedom of speech'):
        return 'form.demandprogress'

    '''
        10603304789399
        The Title II order created a gaping gap in privacy protections by taking the best cop, the FTC, off the beat. That is reason enough to support Chairman Pai's proposal to restore Internet freedom. Restore privacy by repealing Net Neutrality.
    '''
    if 'Restore privacy by repealing Net Neutrality' in comment['text_data']:
        return 'bot.best_cop'

    '''
        105281371127474
        I am in favor of strong net neutrality under Title II of the Telecommunications Act. (50.4k)
    '''
    if 'I am in favor of strong net neutrality under Title II of the Telecommunications Act' in comment['text_data']:
        return 'bot.telecommunications_act'

    '''
        10524219503826
        make sure net neutrality does not dissapear. It is the only thing saving the internet at this moment. If it is removed many webservices will be at risk (28.5k)
        '''
    if 'make sure net neutrality does not dissapear' in comment['text_data']:
        return 'bot.dissapear'

    '''
    105252020204018
    We should not leave the ability for small companies to compete with large online businesses up to the whims of our internet providers. It is out responsibility to defend our right to free market competition. IF THENEWSEARCHENGINE  is better than Google, Google's wealth should not strike down the new engine if our internet providers choose not to be benevolent. Save net neutrality. (28.6k)
    '''
    if 'small companies to compete with large online businesses up to the whims of our internet providers' in comment['text_data']:
        return 'bot.thenewsearchengine'

    '''
    1060351723564
    The FCC's Net Neutrality rules were written in the Obama White House by political staff and Tech Industry special interests who overruled the FCC's own experts. The FCC's own chief economist Tim Brennan called the rules "an economics-free zone." They should be repealed. (45.6k)
    '''
    if 'own chief economist Tim Brennan called the rules' in comment['text_data']:
        return 'bot.economics_free_zone'

    '''
    10603433603879
    Obama's Net Neutrality order was the corrupt result of a corrupt process controlled by Silicon Valley special interests. It gives some of the biggest companies in the world a free ride at the expense of consumers and should be immediately repealed! (77k)
    '''
    if 'corrupt result of a corrupt process' in comment['text_data']:
        return 'bot.corrupt_result'

    if 'mesmorized by money that it jeopardizes the well-being of its citizens. Is this how we MAGA' in comment['text_data']:
        return 'bot.maga'

    if 'the Obama Administration rammed through a massive scheme that gave the federal government broad regulatory control over the internet' in comment['text_data']:
        return 'bot.rammed'

    if 'imposed restrictive Title II, utility-style regulations under the guise of an' in comment['text_data'] and 'By rolling back the misguided 2015 regulations we can restore an unrestricted and truly open internet' in comment['text_data']:
        return 'bot.wheeler'

    if 'The current FCC regulatory scheme known' in comment['text_data'] and 'The internet has flourished for decades without the heavy hand of government over-regulation' in comment['text_data'] and 'plan to return to a commonsense regulatory framework' in comment['text_data']:
        return 'bot.commonsense'

    if 'On July 12 is the Protect Net Neutrality Day of Action' in comment['text_data']:
        return 'bot.day_of_action'

    if 'Dear Ladies and Gentlemen. Net neutrality is a serious topic' in comment['text_data']:
        return 'bot.serious'

    if 'We need net neutralityto continue' in comment['text_data'] and 'control should not be at the mercy of corporations' in comment['text_data']:
        return 'bot.mercy'

    if 'Please save the internet from the corporations. Tom Wheeler was right. Let the new neutrality stand' in comment['text_data']:
        return 'bot.save_the_internet'

    if 'Paragraph 82 asks for input on whether throttling should be regulated' in comment['text_data'] and 'In the past ISPs have throttled content based on their own determination of what was lawful or permissible' in comment['text_data']:
        return 'form.techcrunch'

    if 'The free-market Internet was an incredible engine of economic growth' in comment['text_data']:
        return 'bot.free_market_internet'

    if 'As a concerned taxpayer and consumer, I am writing to urge the FCC' in comment['text_data']:
        return 'form.protecting_taxpayers'

    if 'As a freelance translator I rely on internet' in comment['text_data']:
        return 'bot.freelance'

    lower = comment['text_data'].lower()

    def and_array(input_array):
        array = [e.lower() for e in input_array]
        val = (lower.find(array[0]) >= 0)
        for e in array[1:]:
            val &= (lower.find(e) >= 0)
        return val

    def or_array(input_array):
        array = [e.lower() for e in input_array]
        val = (lower.find(array[0]) >= 0)
        for e in array[1:]:
            val |= (lower.find(e) >= 0)
        return val

    lanes = ["power to block websites",
             "slow them down",
             'split the internet into',
             'fast lanes',
             'for companies that pay',
             'slow lanes',
             'for the rest']
    if and_array(lanes):
        return 'form.battleforthenet'

    weakened = [
        'worried that the protections that are in place will be weakened if we change the way',
    ]
    if and_array(weakened):
        return 'form.techcrunch'

    unfair = [
        "Allowing broadband providers to throttle their service is unfair business",
        "Weakening protections for consumers for the sake of big business is foolish",
        "This proposal clearly gets rid of net neutrality.",
        "I am opposed to this",
        "Save net neutrality and protect consumers",
    ]
    if and_array(unfair):
        return 'bot.unfair'

    reject = [
        'The FCC should reject Chairman Ajit Pai',
        'The FCC should throw out Chairman Ajit Pai',
    ]
    stripping = [
        'stripping consumers',
        'stripping users',
        'stripping Internet users',
    ]
    of_the = [
        'of the necessary',
        'of the meaningful',
        'of the vital',
    ]
    thankfully = [
        'Thankfully, the current',
        'Thankfully, the existing',
    ]
    rules = [
        'net neutrality rules',
        'FCC regulations',
        'Open Internet rules',
    ]
    ensure = [
        'ensure that',
        'mean that',
    ]
    if or_array(reject) and or_array(stripping) and or_array(of_the) and or_array(thankfully) and or_array(rules) and or_array(ensure):
        return 'form.dearfcc'

    microbusiness = [
        "proposed plan to repeal net neutrality protections would put a huge burden on microbusinesses like mine",
        "32% of creative entrepreneurs on the platform",
        "Chairman Pai is not only taking away our livelihood, he is also putting up barriers to entrepreneurs"
    ]
    if and_array(microbusiness):
        return 'form.microbusiness'

    guarantee = [
        "Net neutrality guarantees a free and open internet",
        "Without it, internet service providers could block or censor websites, or create",
        "ISPs can't be allowed to abuse their position, potentially hurting businesses and consumers across the country, and privileging their own content over competitors",
        "Revoking net neutrality by changing the Title II classification of internet access would be bad for people, bad for competition and entrepreneurship, and it's bad for the internet",
        "I fully support keeping the current Title II classification of internet access and keeping the internet free and open",
    ]
    if and_array(guarantee):
        return 'form.ofa'


    '''
        TODO: pro templates

        huge burden on microbusinesses (5.4k) 106031636823984

        1051374845855
        MY NAME JEFF (2.2k)

        10531201619489
        "The FCC's Open Internet Rules (net neutrality rules) are extremely important to me. I urge you to protect them." (17k)

        1051877951361
        Net Neutrality is not negotiable. ItÕs essential to everything we need in our society and democracy Ñ from educational and economic opportunities to political organizing and dissent. (29.7k)
    '''

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
    if isinstance(address, list):
        address = address[0]
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
        'fulladdress': fulladdress(comment),
        'capsemail': capsemail(comment),
        'source': source(comment),
        'proceedings_keys': proceeding_keys(comment),
        'onsite': onsite(comment),
        'ingestion_method': ingestion_method(comment)
    }

    source_mapping = {}
    for key in tags.sources['positive']:
        source_mapping[key]= True
    for key in tags.sources['negative']:
        source_mapping[key]= False
    if analysis['source'] in source_mapping:
        analysis['titleii'] = source_mapping[analysis['source']]

    if 'titleii' not in analysis:
        titleii_sent = titleii(comment)
        if titleii_sent is not None:
            analysis['titleii'] = titleii_sent

    text = comment.get('text_data', '')
    words = len(text.split(' '))
    analysis['words'] = words
    if len(text) < 13 or words < 3:
        analysis['untaggable'] = True

    return analysis
