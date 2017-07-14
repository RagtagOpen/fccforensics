import os
import argparse

from .index import CommentIndexer
from .analyze import CommentAnalyzer
from .create import IndexCreator
from .sentiment import SigTermsSentiment
from .breached import BreachChecker


def create_command(args):
    parser = argparse.ArgumentParser(description='Create fcc-comments index with mappings')
    parser.add_argument(
        '--endpoint', dest='endpoint',
        default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
    )
    command_args = parser.parse_args(args=args)

    creator = IndexCreator(**vars(command_args))
    creator.run()


def index_command(args):
    parser = argparse.ArgumentParser(description='Locally index FCC comments')
    parser.add_argument(
        '-l', '--lte', dest='lte',
        help='Only index comments sent before this'
    )
    parser.add_argument(
        '-g', '--gte', dest='gte',
        help='Only index comments sent after this'
    )
    parser.add_argument(
        '--endpoint', dest='endpoint',
        default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
    )
    parser.add_argument(
        '--no-verify', dest='verify', nargs='?',
        help='Don\'t verify SSL certs', default=True,
        const=False
    )
    parser.add_argument(
        '--fast-out', dest='fastout', nargs='?',
        help='Quit when we see a comment that we\'ve already ingested', default=True,
        const=False
    )
    command_args = parser.parse_args(args=args)

    indexer = CommentIndexer(**vars(command_args))
    indexer.run()


def analyze_command(args):
    parser = argparse.ArgumentParser(description='Analyzes indexes FCC comments')
    parser.add_argument(
        '--endpoint', dest='endpoint',
        default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
    )
    parser.add_argument(
        '--no-verify', dest='verify', nargs='?',
        help='Don\'t verify SSL certs', default=True,
        const=False
    )
    parser.add_argument(
        '--limit', dest='limit',
        default=10000
    )
    command_args = parser.parse_args(args=args)
    analyzer = CommentAnalyzer(**vars(command_args))
    analyzer.run()


def positive_sig_terms_command(args):
    parser = argparse.ArgumentParser(description='Tag comments that match positive significant terms')
    parser.add_argument(
        '--endpoint', dest='endpoint',
        default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
    )
    parser.add_argument(
        '--limit', dest='limit',
        default=10000
    )
    command_args = parser.parse_args(args=args)
    analyzer = SigTermsSentiment(**vars(command_args))
    analyzer.run()

def breached_command(args):
    parser = argparse.ArgumentParser(description='Analyze comments to check if they were in a breach')
    parser.add_argument(
        '--endpoint', dest='endpoint',
        default=os.environ.get('ES_ENDPOINT', 'http://127.0.0.1:9200/')
    )
    command_args = parser.parse_args(args=args)
    pwned = BreachChecker(**vars(command_args))
    pwned.run()

def main():
    parser = argparse.ArgumentParser(description='Run commands to index and analyze FCC comments')
    parser.add_argument('command', choices=['index', 'analyze', 'create', 'tag_sigterms', 'breached'])
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    {
        'create': create_command,
        'index': index_command,
        'analyze': analyze_command,
        'tag_sigterms': positive_sig_terms_command,
        'breached': breached_command
    }[args.command](args.args)
