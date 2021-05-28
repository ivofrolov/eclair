import logging
import argparse
import random

from eclair.api import get_problem


def get_exact_problem(args: argparse.Namespace):
    """Numbered problem command handler."""
    assert hasattr(args, 'number'), 'number argument not provided'
    problem = get_problem(args.number)
    print(problem)


def get_random_problem(args: argparse.Namespace):
    """Random problem command handler."""
    problem = get_problem(random.randint(1, 757))
    print(problem)


def entrypoint():
    """Sets up program environment."""
    parser = argparse.ArgumentParser(prog='python3 -m eclair')
    parser.add_argument('--verbose', '-v', action='count', default=0)

    subparsers = parser.add_subparsers()

    exact_parser = subparsers.add_parser('number')
    exact_parser.add_argument('number', metavar='N', type=int)
    exact_parser.set_defaults(func=get_exact_problem)

    random_parser = subparsers.add_parser('random')
    random_parser.set_defaults(func=get_random_problem)

    args = parser.parse_args()

    level = (5 - min(args.verbose, 5)) * 10
    logging.basicConfig(level=level, format='%(message)s')

    args.func(args)
