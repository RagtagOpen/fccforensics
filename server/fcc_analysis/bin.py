import os
import argparse

from .index import CommentIndexer
from .analyze import CommentAnalyzer


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
    command_args = parser.parse_args(args=args)
    analyzer = CommentAnalyzer(**vars(command_args))
    analyzer.run()


def main():
    parser = argparse.ArgumentParser(description='Run commands to index and analyze FCC comments')
    parser.add_argument('command', choices=['index', 'analyze'])
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    {
        'index': index_command,
        'analyze': analyze_command,
    }[args.command](args.args)
