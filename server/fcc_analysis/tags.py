import json

sources = {
    'positive': [
        "form.battleforthenet", "reddit.technology", "blog.venturebeat", "bot.internetuser",
        "form.dearfcc", "bot.illogically-named", "form.signforgood", "form.freepress",
        "form.freepress2",  "form.demandprogress", "bot.maga", "bot.dissapear",
        "bot.telecommunications_act", "bot.thenewsearchengine", "es_terms_positive",
        "form.aclu", "bot.day_of_action", "bot.serious", "bot.mercy", "bot.save_the_internet",
        "form.techcrunch", "bot.freelance"
    ],
    'negative': [
        "bot.american-jobs", "bot.unprecedented", "bot.outraged",
        "form.diminished-investment", "form.freeourinternet", "form.fwact", "form.tpa",
        "bot.best_cop", "bot.economics_free_zone", "bot.corrupt_result", "bot.recursive",
        "form.att", "bot.telephone_monopoly", "bot.titleii_takeover", "es_terms_negative",
        "bot.rammed", "bot.wheeler", "bot.commensense", "bot.free_market_internet",
        "form.protecting_taxpayers"]
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
                            {'term': {'analysis.untaggable': True}},
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

source_meta = {
    'bot.recursive': {
        'icon': 'bot',
        'sentiment': 'negative',
        'sample': 'With respect to net neutrality and Title II. I encourage the commission to overturn Tom Wheeler\'s order to control the Internet. Internet users, rather than unelected bureaucrats, deserve to purchase whichever products we choose. Tom Wheeler\'s order to control the Internet is a exploitation  of net neutrality. It undid a pro-consumer framework that performed fabulously successfully for two decades with both parties\' support.'
    },
    'bot.american-jobs': {
        'icon': 'bot',
        'sentiment': 'negative',
        'sample': 'The free-market Internet was an incredible engine of economic growth, innovation, and job creation since the 1990s and has already been substantially slowed by the 2015 Net Neutrality rules. The slowdown in investment is destroying jobs and risks a big future tax hike to make up for lost private investment. Save American jobs by repealing Net Neutrality'
    },
    'bot.unprecedented': {
        'icon': 'form',
        'sentiment': 'negative',
        'url': 'http://cfif.org/v/index.php/commentary/62-technology-and-telecom/3596-center-for-individual-freedom-mobilizes-americans-opposed-to-the-obama-administrations-title-ii-internet-power-grab-',
        'sample': 'The unprecedented regulatory power the Obama Administration imposed on the internet is smothering innovation, damaging the American economy and obstructing job creation. I urge the Federal Communications Commission to end the bureaucratic regulatory overreach of the internet known as Title II and restore the bipartisan light-touch regulatory consensus that enabled the internet to flourish for more than 20 years. The plan currently under consideration at the FCC to repeal Obama\'s Title II power grab is a positive step forward and will help to promote a truly free and open internet for everyone.'
    },
    'bot.outraged': {
        'icon': 'bot',
        'sentiment': 'negative',
        'sample': '''I was outraged by the Obama/Wheeler FCC's decision to reclassify the Internet as a regulated "public utility" under a Depression-era law written for the old Ma Bell telephone monopoly.

Government utility regulation of the Internet risks devastating private investment, undermining competition, and stalling innovation. It also puts consumers at serious risk of being hit with a new "broadband tax" to cover the lack of private sector investment due to these regulations.

The liberal extremist groups that ginned up fake support for reclassification include the group Free Press, which was cited 62 times in the Title II order.

Free Press was founded by ultraliberal college professor Robert McChesney who has admitted: "At the moment, the battle over network neutrality is not to completely eliminate the telephone and cable companies. We are not at that point yet. But the ultimate goal is to get rid of the media capitalists in the phone and cable companies and to divest them from control."

Clearly, these extremists groups are openly hostile to America's free-market economy.

The Trump/Pai FCC is right to revisit this issue. I urge you to stand up to the radical extremists who took over the FCC under Obama and protect our free-market Internet by rescinding the Title II order.'''
    },
    'form.diminished-investment': {
        'icon': 'form',
        'sentiment': 'negative',
        'url': 'http://action.americancommitment.org/ctas/advocacy-251-repeal-obamas-internet-regulations/letter',
        'sample': '''Obama’s Title II order has diminished broadband investment, stifled innovation, and left American consumers potentially on the hook for a new broadband tax.

These regulations ended a decades-long bipartisan consensus that the Internet should be regulated through a light touch framework that worked better than anyone could have imagined and made the Internet what it is.

For these reasons I urge you to fully repeal the Obama/Wheeler Internet regulations.'''
    },
    'form.freeourinternet': {
        'icon': 'form',
        'sentiment': 'negative',
        'url': 'http://freeourinternet.org/take-action/',
        'sample': '''In 2015, wealthy leftist billionaires and powerful Silicon Valley monopolies took the internet out of the hands of the people and placed it firmly under the thumb of the federal the government, monopolies like Google and global billionaires like George Soros. Not surprisingly, today Obama's new Internet gatekeepers are censoring our viewpoints, banning our online activities and silencing dissenting voices. As Google Chairman Eric Schmidt admitted, "We're not arguing for censorship, we're arguing just take it off the page...make it harder to find."

It took only two years and a green light from Obama for companies like Google and Facebook and their liberal allies like George Soros to take total control of the dominant information and communications platform in the world today.

We simply can't afford to let Obama's disastrous rules stand. The FCC must stand up for a truly free and open Internet by immediately rolling back his cynical and self-serving Internet takeover. The future of a free and open Internet is at stake'''
    },
    'form.fwact': {
        'icon': 'form',
        'sentiment': 'negative',
        'url': 'https://fwact.org/M0VU4IR',
        'sample': '''Dear Express Restoring Internet Freedom,

 I'm asking you to support the rollback of Obama's takeover of the internet and title II regulations.

 Regards,
 Jay Joyner
 1791 Oakhurst Ave
 Winter Park, FL 32789'''
    },
    'form.tpa': {
        'icon': 'form',
        'sentiment': 'negative',
        'url': 'http://www.tpaaction.org/',
        'sample': '''As a concerned taxpayer and consumer, I am writing to urge the FCC to set the internet free and remove the inappropriate, unnecessary and overly vast regulations currently holding back the full potential of the internet. Due to the grip of the utility-style regulations imposed under the previous Commission, taxpayers have been put at risk, the threat of new fees on consumer bills still looms large, investment in internet infrastructure has not realized its full potential, innovations have gone undeveloped and unrealized, and twenty years of the appropriate level of oversight of the internet has been reversed.

We must dial-back the poorly conceived application of Title II in the Open Internet Order so that American taxpayers can benefit from an unrestrained and truly open internet that scales back the unlimited power of the government, protects consumers from new taxes and encourages future investment and endless innovations.'''
    },
    'bot.best_cop': {
        'icon': 'bot',
        'sentiment': 'negative',
        'sample': '''The Title II order created a gaping gap in privacy protections by taking the best cop, the FTC, off the beat. That is reason enough to support Chairman Pai's proposal to restore Internet freedom. Restore privacy by repealing Net Neutrality.'''
    },
    'bot.economics_free_zone': {
        'icon': 'bot',
        'sentiment': 'negative',
        'sample': '''The FCC's Net Neutrality rules were written in the Obama White House by political staff and Tech Industry special interests who overruled the FCC's own experts. The FCC's own chief economist Tim Brennan called the rules "an economics-free zone." They should be repealed.'''
    },
    'bot.corrupt_result': {
        'icon': 'bot',
        'sentiment': 'negative',
        'sample': '''Obama's Net Neutrality order was the corrupt result of a corrupt process controlled by Silicon Valley special interests. It gives some of the biggest companies in the world a free ride at the expense of consumers and should be immediately repealed!'''
    },
    'form.att': {
        'icon': 'form',
        'sentiment': 'negative',
        'url': 'http://about.att.com/sites/open_internet',
        'sample': '''I am writing today in support of preserving an open internet that is transparent and free from blocking, censorship and discriminatory throttling and to encourage you and other members of Congress to work together to pass open internet legislation.

Congress has the power to end the political back and forth and create lasting open internet protections that apply to everyone and will remain in place regardless of which party is in power. I agree with the current FCC that heavy-handed regulations will do more harm than good. But, we need legislation to put this issue to rest once and for all and ensure an open internet for decades to come.'''
    },
    'bot.telephone_monopoly': {
        'icon': 'bot',
        'sentiment': 'negative',
        'sample': 'Title II is a Depression-era regulatory framework designed for a telephone monopoly that no longer exists. It was wrong to apply it to the Internet and the FCC should repeal it and go back to the free-market approach that worked so well.'
    },
    'bot.titleii_takeover': {
        'icon': 'bot',
        'sentiment': 'negative',
        'sample': '''Dear FCC Commissioner ,

 The Obama-era FCC regulations known as "Title II" enable the federal government to exert an extraordinary and unnecessary amount of regulatory control over the internet. This bureaucratic overreach impedes innovation, stifles investment and continues to create economic uncertainty for one of the largest sectors of the U.S. economy.

 I support Chairman Pai's proposal to roll back Title II and restore the sensible regulatory framework that enjoyed broad bipartisan consensus and enabled the internet to thrive for more than two decades.

 I strongly urge all of the FCC Commissioners to support the Chairman's proposal to repeal the harmful Title II internet takeover.'''
    },
    'form.aclu': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'https://action.aclu.org/secure/comment-net-neutrality',
        'sample': 'I strongly oppose Chairman Pai&apos;s proposal to reverse net neutrality protections because a free and open internet is vital for our democracy, for our businesses, and for our daily lives. It would give giant internet companies the power to prioritize what we read, watch, and explore online. I won&apos;t stand for it. It&apos;s about my right to be heard and my right to hear others. I submit my public comment to oppose Chairman Pai&apos;s proposal to reverse net neutrality protections.'
    },
    'form.battleforthenet': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'https://www.battleforthenet.com/',
        'sample': '''The FCC Open Internet Rules (net neutrality rules) are extremely important to me. I urge you to protect them.

  Most Americans only have one choice for true high speed Internet access: our local cable company. Cable companies (and wireless carriers) are actively lobbying Congress and the FCC for the power to:

  * Block sites and apps, to charge them "access fees"
  * Slow sites and apps to a crawl, to establish paid "fast lanes" (normal speed) and slow lanes (artificially low speeds)
  * Impose arbitrarily low data caps, so they can charge sites to escape those caps, or privilege their own services ("zero rating")

  They're doing it so they can use their monopoly power to stand between me and the sites I want to access, extorting money from us both. I'll be forced to pay more to access the sites I want, and sites will have to pay a kind of protection money to every major cable company or wireless carrier—just to continue working properly! The FCC's Open Internet Rules are the only thing standing in their way.

  I'm sending this to letter to my two senators, my representative, the White House, and the FCC. First, to the FCC: don’t interfere with my ability to access what I want on the Internet, or with websites' ability to reach me. You should leave the existing rules in place, and enforce them.

  To my senators: you have the power to stop FCC Chair Ajit Pai from abusing the rules by refusing to vote for his reconfirmation. I expect you to use that power. Pai, a former Verizon employee, has made it clear he intends to gut the rules to please his former employer and other major carriers, despite overwhelming support for the rules from voters in both parties. I urge you publicly oppose Pai's confirmation on these grounds.

  To the White House: Ajit Pai, a former Verizon employee, is acting in the interests of his former employer, not the American people. America deserves better. Appoint an FCC Chair who will protect the economic miracle that is the Internet from media monopolies like AT&T, Time Warner Cable, and Comcast/NBC/Universal.

  To my representative: please publicly oppose Ajit Pai's plan to oppose the rules, and do everything you can to persuade the Senate and the White House to oppose Pai's nomination.

  I would be happy to speak more with anyone on your staff about the rules and why they’re so important to me. Please notify me of any opportunities to meet with you or your staff.
Allison Sanbongi'''
    },
    'reddit.technology': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'https://www.reddit.com/r/technology/comments/6894i9/heres_how_to_contact_the_fcc_with_your_thoughts/?st=j5lzcn7t&sh=e7e2f698',
        'sample': 'It is my understanding that the FCC Chairman intends to reverse net neutrality rules and put big Internet Service Providers in charge of the internet. I am firmly against this action, and believe that these ISPs will operate solely in their own interests and not in the interests of what is best for the American public. This will put ISPs in a prime position to abuse their status and encourage anticompetitive behavior, and as such, will be deleterious to the health of the American economy and the best interests of American citizens.'
    },
    'blog.venturebeat': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'https://venturebeat.com/2017/05/08/how-to-protest-the-fccs-plan-to-dismantle-net-neutrality/',
        'sample': 'I support the existing Net Neutrality rules, which classify internet service providers under the Title II provision of the Telecommunications Act. Please DO NOT roll back these regulations. Thanks!'
    },
    'bot.internetuser': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'https://www.eff.org/deeplinks/2017/06/nlpcs-false-report-diverts-attention-concerns-real-net-neutrality-supporters',
        'sample': '''As an Internet user, I'm asking the FCC to protect the net neutrality protections currently in place.

The FCC should throw out Chairman Ajit Pai's proposal to give the ISP monopolies like Comcast, AT&T, and Verizon the authority to create Internet fast lanes, stripping Internet users of the meaningful access and privacy protections we fought for and just recently won.

I'm concerned about ISPs being allowed to discriminate against certain types of data or websites, because users will have fewer options and a less diverse Internet. Thankfully, the current net neutrality rules ensure that Internet providers can't slow or block our ability to see certain websites or create Internet "fast lanes" by charging websites and online service money to reach customers faster. That's exactly the right balance to ensure the Internet remains a level playing field that benefits small businesses and Internet users as well as larger players. Pai's proposed repeal of the rules would transform ISPs into Internet gatekeepers with an effective veto right on innovation and expression. That's not the kind of Internet we want to pass on to future generations of technology users.

I urge you to keep Title II net neutrality in place, and safeguard Internet users like me.

Sincerely,
Antonio Mitchell'''
    },
    'form.dearfcc': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'https://dearfcc.org/',
        'sample': '''Dear FCC,

The FCC needs to stand up for Internet users like me and keep the net neutrality rules that are already in effect.

The FCC should reject Chairman Ajit Pai’s proposal to hand the telecom giants like AT&T, Comcast, and Verizon the legal cover to throttle whatever they please, stripping consumers of the vital access and privacy rules we fought for and won just two years ago.

I’m worried about creating a tiered Internet with “fast lanes” for certain sites or services because ISPs could have too much power to determine what I can do online, and effectively kill of the competition.

Thankfully, the existing net neutrality rules ensure that Internet providers can’t slow or block our access to certain web services or create Internet “fast lanes” by charging websites and online service money to reach customers faster. That’s the right kind of forward-looking approach to make sure competition in the Internet space is fair and benefits small businesses and consumers as well as entrenched Internet companies. Pai’s proposed repeal of the rules would help turn ISPs into Internet gatekeepers with the ability to veto new expression and innovation. That’s not the kind of Internet we want to pass on to future generations of technology users.'''
    },
    'bot.illogically-named': {
        'icon': 'bot',
        'sentiment': 'positive',
        'sample': '''This illogically named "restoring internet freedom" filing is aimed squarely at the freedom of the internet, not at the Internet Service Providers who are gunning for more money and less citizen involvement in keeping the internet free. Regulating the internet like a utility (which is the most appropriate category for the service provided) protects consumer rights from corporate entites (ISPs) whose only purpose is to generate shareholder value, not protect their customers rights or data. Please, do NOT deregulate the protection of the internet, and do NOT adopt these corporate-favoring rules to dismantle the freedom that the internet was built on. It's bad for business, and bad for America. NO on filing 17-108'''
    },
    'form.signforgood': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'https://petitions.signforgood.com/ProtectNetNeutrality/',
        'sample': '''Don't kill net neutrality. We deserve a free and open Internet - one where the flow of data is determined by the interests of Internet users'''
    },
    'form.freepress': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'http://act.freepress.net/sign/internet_NN_pai/',
        'sample': 'Net Neutrality is not negotiable. It’s essential to everything we need in our society and democracy'
    },
    'form.freepress2': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'http://act.freepress.net/letter/internet_fcc_nprm_nn_2017/',
        'sample': '''Cable and phone companies provide access to the internet. They're telecommunications carriers. They do not (and should not) have the right to censor or slow down my speech and my access to online content. When I use my broadband service, I decide who I communicate with and what information I transmit. I want the FCC to retain the ability to stop my internet service provider from interfering with my communications choices. The courts have already told the FCC that to do this, ISPs must remain under Title II.  \n\nI'm urging FCC Chairman Ajit Pai to preserve real Net Neutrality rules and keep Title II in place for broadband internet access.''',
    },
    'form.demandprogress': {
        'icon': 'form',
        'sentiment': 'positive',
        'url': 'https://act.demandprogress.org/sign/trump-pai-attack-net-neutrality/',
        'sample': 'A free and open internet is critical for Americans to connect with their friends and family, exercise their freedom of speech, and create innovative new businesses. In 2015, the FCC established strong net neutrality rules to protect the free and open internet Americans depend on. Please reject any plan from Trump or his FCC Chair to roll back net neutrality rules and open the door to a corporate controlled internet.'
    },
    'bot.dissapear': {
        'icon': 'bot',
        'sentiment': 'positive',
        'sample': 'make sure net neutrality does not dissapear. It is the only thing saving the internet at this moment. If it is removed many webservices will be at risk.'
    },
    'bot.telecommunications_act': {
        'icon': 'bot',
        'sentiment': 'positive',
        'sample': '''I am in favor of strong net neutrality under Title II of the Telecommunications Act.


Sincerely,
Paul Ng'''
    },
    'bot.thenewsearchengine': {
        'sentiment': 'positive',
        'icon': 'bot',
        'sample': '''We should not leave the ability for small companies to compete with large online businesses up to the whims of our internet providers. It is out responsibility to defend our right to free market competition. IF THENEWSEARCHENGINE  is better than Google, Google's wealth should not strike down the new engine if our internet providers choose not to be benevolent. Save net neutrality.'''
    },
    'bot.maga': {
        'sentiment': 'positive',
        'icon': 'bot',
        'sample': 'Leave the net neutrality alone. Internet speed should not be for sale. There is nothing wrong with out current system save for the greedy corporations who wish to turn the internet into their own pay-to-play and a government willing to let them do it. You serve the American people not just Verizon, AT&T, etc. IF you think the current protests are bad, try touching new neutrality. I will never understand why a nation who has come so far is hell bent on going back to the 18th century. No other modern nation is so mesmorized by money that it jeopardizes the well-being of its citizens. Is this how we MAGA?'
    },
    'johnoliver': {
        'sentiment': 'positive',
        'icon': 'form',
        'url': 'https://www.youtube.com/watch?v=92vuuZt7wak',
        'sample': 'I support strong net neutrality backed by title II oversights of ISP'''
    },
    'bot.rammed': {
        'sentiment': 'negative',
        'icon': 'bot',
        'sample': '''Before leaving office, the Obama Administration rammed through a massive scheme that gave the federal government broad regulatory control over the internet. That misguided policy decision is threatening innovation and hurting broadband investment in one of the largest and most important sectors of the U.S. economy.

I support the Federal Communications Commission's decision to roll back Title II and allow for free market principles to guide our digital economy''',
    },
    'bot.wheeler': {
        'sentiment': 'negative',
        'icon': 'bot',
        'sample': '''In 2015, Chairman Tom Wheeler\x92s Federal Communications Commission (FCC) imposed restrictive Title II, utility-style regulations under the guise of an \x93open internet.\x94 Not only have these regulations inhibited innovation in the internet ecosystem, they hurt taxpayers and consumers by expanding the regulatory reach of the FCC and limiting investment in internet infrastructure. We cannot allow this revolutionary tool to be bogged down with excessive government interference.\n \nIt is past time for the FCC, an agency that is funded by American taxpayers, to free the internet of burdensome regulations. By rolling back the misguided 2015 regulations we can restore an unrestricted and truly open internet. I thank the Commissioners for considering these comments during the reply period.''',
    },
    'bot.commensense': {
        'sentiment': 'negative',
        'icon': 'bot',
        'sample': '''The current FCC regulatory scheme known as "Title II" represents an unprecedented increase in government control over the internet. Such over-regulation is hurting our economy and suffocating innovation.

I support Chairman Pai\'s plan to return to a commonsense regulatory framework that allows for the internet to grow without useless government interference. The internet has flourished for decades without the heavy hand of government over-regulation.  It\x92s time we return to what works''',
    },
    'bot.day_of_action': {
        'sentiment': 'positive',
        'icon': 'bot',
        'sample': '''On July 12 is the Protect Net Neutrality Day of Action! This would be the day to protect our freedom of internet and Fight to escape the control of our life by the ISPs - the corporations we all despise. Do not let them get away with this, fight For Our Future as if our life depend on it!''',
    },
    'bot.serious': {
        'sentiment': 'positive',
        'icon': 'bot',
        'sample': '''Dear Ladies and Gentlemen. Net neutrality is a serious topic. Please do not implement weakend regulations. TO keep it short and save my breath: All possible negative scenarios were discussed in the past. More than that: some of them were getting reality and thus the discussion started back in 2010/ So please keep it as it is and do something useful.''',
    },
    'bot.mercy': {
        'sentiment': 'positive',
        'icon': 'bot',
        'sample': '''We need net neutralityto continue. A free and open internet is the single greatest technology of our time, and control should not be at the mercy of corporations.''',
    },
    'bot.save_the_internet': {
        'sentiment': 'positive',
        'icon': 'bot',
        'sample': '''Please save the internet from the corporations. Tom Wheeler was right. Let the new neutrality stand.''',
    },
    'form.techcrunch': {
        'sentiment': 'positive',
        'icon': 'form',
        'sample': '''Paragraph 82 asks for input on whether throttling should be regulated. In the past ISPs have throttled content based on their own determination of what was lawful or permissible, and had to be forced to stop in the courts''',
        'url': 'https://techcrunch.com/2017/04/27/how-to-comment-on-the-fccs-proposal-to-revoke-net-neutrality/',
    },
    'bot.free_market_internet': {
        'sentiment': 'negative',
        'icon': 'bot',
        'sample': '''The free-market Internet was an incredible engine of economic growth, innovation, and job creation since the 1990s and has already been substantially slowed by the 2015 Net Neutrality rules. The slowdown in investment is destroying jobs and risks a big future tax hike to make up for lost private investment. Save American jobs by repealing Net Neutrality.''',
    },
    'form.protecting_taxpayers': {
        'sentiment': 'negative',
        'icon': 'form',
        'sample': '''As a concerned taxpayer and consumer, I am writing to urge the FCC to set the internet free and remove the inappropriate, unnecessary and overly vast regulations currently holding back the full potential of the internet. Due to the grip of the utility-style regulations imposed under the previous Commission, taxpayers have been put at risk, the threat of new fees on consumer bills still looms large, investment in internet infrastructure has not realized its full potential, innovations have gone undeveloped and unrealized, and twenty years of the appropriate level of oversight of the internet has been reversed. We must dial-back the poorly conceived application of Title II in the Open Internet Order so that American taxpayers can benefit from an unrestrained and truly open internet that scales back the unlimited power of the government, protects consumers from new taxes and encourages future investment and endless innovations.''',
        'url': 'https://www.protectingtaxpayers.org/take-action/',
    },
    'bot.freelance': {
        'sentiment': 'positive',
        'icon': 'bot',
        'sample': '''Please Save Net Neutrality and Title ll rules. As a freelance translator I rely on internet spped to do my work and corporations would interfere with my searches if given the change. Do the right thing and keep the needed regulations. Thank you.''',
    },
    'bot.unfair': {
        'sentiment': 'positive',
        'icon': 'bot',
        'sample': '''Allowing broadband providers to throttle their service is unfair business practive. Weakening protections for consumers for the sake of big business is foolish and a countrer to the FCC's mandate. This proposal clearly gets rid of net neutrality. I am opposed to this. Save net neutrality and protect consumers.''',
    },
    'form.microbusiness': {
        'sentiment': 'positive',
        'icon': 'form',
        'url': 'http://www.carvedwoodenspoons.com/blog/protect-net-neutrality',
        'sample': '''Chairman Pai's proposed plan to repeal net neutrality protections would put a huge burden on microbusinesses like mine.

As an internet business, net neutrality is essential to the success of my business and my ability to care for myself and my family. The FCC needs to ensure equal opportunities for microbusinesses to compete with larger and more established brands by upholding net neutrality protections.

The internet has opened the door for me and 1.8 million other sellers to turn our passion into a business by connecting us to a global market of buyers. For 32% of creative entrepreneurs on the platform, our creative business is our sole occupation. A decrease in sales in the internet slow lane or higher cost to participate in Chairman Pai's pay-to-play environment would create significant obstacles for me and other businesses to care for ourselves and our families.

Moreover, 87% of Etsy sellers in the U.S. are women, and most run their microbusinesses out of their homes. By rolling back the bright line rules that ensure net neutrality, Chairman Pai is not only taking away our livelihood, he is also putting up barriers to entrepreneurship for a whole cohort of Americans.

My business growth depends on equal access to consumers. Any rule that allows broadband providers to negotiate special deals with some companies would undermine my ability to compete online.

We need a free and open internet that works for everyone, not just telecom companies that stand to benefit from the FCC's proposed rules.

I'm sending this to the FCC's open proceeding and to my members of Congress. Please publicly support the FCC's existing net neutrality rules based on Title II and microbusinesses like mine.''',
    },
    'form.ofa': {
        'sentiment': 'positive',
        'icon': 'form',
        'url': 'https://www.ofa.us/protect-net-neutrality/',
        'sample': '''Net neutrality guarantees a free and open internet. Without it, internet service providers could block or censor websites, or create “fast” and “slow” lanes. ISPs can't be allowed to abuse their position, potentially hurting businesses and consumers across the country, and privileging their own content over competitors. Revoking net neutrality by changing the Title II classification of internet access would be bad for people, bad for competition and entrepreneurship, and it's bad for the internet. I fully support keeping the current Title II classification of internet access and keeping the internet free and open.''',
    },
}

if __name__ == '__main__':
    for key in queries:
        print('%s\t%s\n' % (key, json.dumps(queries[key])))
