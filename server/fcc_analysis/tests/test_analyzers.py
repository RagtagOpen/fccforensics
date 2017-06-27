import os
import json
from unittest import TestCase

from fcc_analysis.analyzers import (
    source, fulladdress, capsemail, fingerprint, titleii, proceeding_keys
)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class AnalyzerTestCase(TestCase):
    maxDiff = 1000

    def get_comment(self, name):
        path = os.path.join(DATA_DIR, '{}.json'.format(name))
        with open(path, 'r') as f:
            return json.load(f)

    def test_unprecedented_bot(self):
        comment = self.get_comment('unprecedented-bot')

        self.assertEqual(source(comment), 'bot.unprecedented')
        self.assertTrue(fulladdress(comment))
        self.assertTrue(capsemail(comment))
        self.assertEqual(
            fingerprint(comment),
            'a administration american and as at bipartisan bureaucratic commission communications consensus consideration creation currently damaging economy enabled end everyone fcc federal flourish for forward free grab help i ii imposed innovation internet is job known lighttouch more obama obamas obstructing of on open overreach plan positive power promote regulatory repeal restore smothering step than that the title to truly under unprecedented urge will years'
        )

    def test_good_bot(self):
        pass

    def test_source(self):
        samples = {
            'johnoliver': [
                'I support strong net neutrality backed by title 2 oversight of isps',
                'I support strong net neutrality backed by title 2 oversight of ISP\'s.',
                'I support strong Net Neutrality oversight backed by title 2 oversight of ISPs.',
                # 'I SUPPORT STRONG NET NEUTRALITY BACKED BY TITLE II (2) OVERSIGHT OF ISPS.',
                'I support strong net neutrality oversight backed by Title II oversight of ISP\'s.',
                # 'I support strong net neutrality backed by title oversight of Title II oversight of ISPs.',
                'I specifically support strong Net Neutrality, backed by Title II oversight of ISP\'s.',
                'I specifically support strong net neutrality backed by Title II oversight of ISP\'s!!!',
                'i strongly support Net Neutrality backed by TItle II oversight.',
                'I support strong net neutrality by Title II oversight of ISPs.',
                'I strongly urge the FCC to maintain strong net neutrality rules backed by Title II.',
                'Support Strong Net Neutrality backed by Title II Oversight of ISP\'s.',
                'I am in support of strong net neutrality rules backed by Title II!',
                'I specifically support strong net neutrality backed by title (2) two oversite of isps.'
            ],
            'form.freeourinternet': [
                'In 2015, President Obama’s FCC passed rules treating the Internet as a government regulated public utility for the first time in history. Those pushing hardest for the new rules were Silicon Valley monopolies like Google and leftist globalists like George Soros.'
            ],
            'unknown': [
                'I support net neutrality. The internet is key to freedom of speech and to leading our daily lives. It should be equally available to everyone.'
                'I firmly support the Open Internet Rule (or commonly known as Net Neutrality). Specifically, I demand that FCC maintains its stance to classify Internet service providers under the Communication Act of 1934 Title II (Common Carrier).  Also, please re-open FCC investigation of zero-rating practices by wireless providers T-Mobile, AT&T and Verizon so that Internet Service Providers do not pick winners and losers of content providers. Further, I strongly reject Laissez-faire economics and the hands-off approach toward government regulations espoused by the Chairman of the Federal Communications Commission Ajit Varadaraj Pai.'
            ],
            'bot.recursive': [
                "To the FCC:  Hi, I'd like to comment on Internet freedom. I want to advocate Ajit Pai to reverse Barack Obama's plan to control broadband. Americans, not Washington bureaucrats, should select whatever applications we want. Barack Obama's plan to control broadband is a exploitation  of net neutrality. It disrupted a market-based policy that functioned very smoothly for many years with Republican and Democrat consensus."
                "To the FCC: I am concerned about internet regulations. I would like to implore the FCC to rescind Tom Wheeler's scheme to take over the Internet. Individuals, as opposed to big government, should use whatever applications they desire. Tom Wheeler's scheme to take over the Internet is a perversion of net neutrality. It disrupted a market-based policy that performed very smoothly for two decades with both parties' backing."
            ]
        }

        for sourcename, sample_list in samples.items():

            for text in sample_list:
                comment = {'text_data': text}
                self.assertEqual(source(comment), sourcename, msg='No match for {}: \n    "{}"'.format(sourcename, text))

    def test_titleii(self):

        pro = [
            'Preserve neutrality and keep title 2',
            'Preserve net neutrality and title 2! Don\'t allow ISPs to throttle my usage based on incentives they get from corporations!',
            'Preserve net neutrality and the listing of ISPs under title 2'
            'I highly implore you to keep high net neutrality rules and regulations. ISPs have already tried to prevent people using services that they had payed for and preferred.',
            'I strongly support title II regulations for ISP, net neutrality from the FCC.',
            'I strongly support net neutrality. Many people have little to no choice in the cable and internet providers and this will hurt the people who do not have many choices in their ISPs',
            'I support Title ll and net neutrality, do not change!!',
            'Preserve net neutrality and Title 2 regulations for internet providers so we can have a free and open internet.',
            'Keep the Internet fair! Keep net neutrality!!',
            'please preserve net neutral rules in title II.',
            'I support net neutrality and maintaining title 2 status.',
            'Network Neutrality Preserve Title II',
            'I support strong net neutrality under title 2.',
            'keep title 2 and net neutrality',
            'Do not repeal net neutrality laws, the internet is a basic right!',
            'FCC Chairman Ajit Pai,\n\nI specifically support strong net neutrality that is backed by title 2 oversight of ISPs.',
            'Strongly support net neutrality and Title 2!'
        ]

        for text in pro:
            comment = {'text_data': text}
            self.assertTrue(titleii(comment), msg='Not classified as pro-title ii:\n    "{}"'.format(text[:100]))

        anti = [
            'Dear Express Restoring Internet Freedom, Please reverse the 2014 changes &amp; restraints on the internet. The Obama administration made a poor decision against our internet freedoms &amp; uses. Thank you for your kind attention.',
            'Rollback Obamas internet takeover.',
            'Please roll back the Title II regulations',
        ]
        for text in anti:
            comment = {'text_data': text}
            self.assertTrue(titleii(comment) is False, msg='Not classified as anti-title ii:\n    "{}"'.format(text[:100]))

    def test_proceeding_keys(self):
        self.assertEqual(
            proceeding_keys({'proceedings': [{'foo': 'hello', 'bar': 'qux', 'qux': 'test'}]}),
            proceeding_keys({'proceedings': [{'bar': 'qux', 'foo': 'hello', 'qux': 'test'}]})
        )
        self.assertIsInstance(proceeding_keys({'proceedings': [{'bar': 'qux', 'foo': 'hello', 'qux': 'test'}]}), str)
