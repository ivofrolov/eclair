import logging
import argparse
import random
from pathlib import Path
from string import Template
from typing import List, Optional

from eclair.api import get_problem
from eclair.problem import Problem


TEMPLATE_SUFFIX = '.tmpl'
TEMPLATES_PATH = Path(__file__).resolve(strict=True).parent.joinpath('templates')


def available_formats() -> List[str]:
    """Returns available template names (extensions) for problem rendering."""
    formats = [p.stem for p in Path(TEMPLATES_PATH).glob(f'*{TEMPLATE_SUFFIX}')]
    return formats


def load_template(format_: str) -> Template:
    """Returns template file contents."""
    template_path = Path(TEMPLATES_PATH).joinpath(f'{format_}{TEMPLATE_SUFFIX}')
    template = Template(template_path.read_text())
    return template


def render_problem(problem: Problem, format_: Optional[str] = None):
    """Outputs problem statement to stdout."""
    template = load_template(format_) if format_ else None
    print(problem.render(template))


def get_exact_problem(args: argparse.Namespace):
    """Numbered problem command handler."""
    assert hasattr(args, 'number'), 'number argument not provided'
    problem = get_problem(args.number)
    render_problem(problem, getattr(args, 'format', None))


def get_random_problem(args: argparse.Namespace):
    """Random problem command handler."""
    problem = get_problem(random.randint(1, 757))
    render_problem(problem, getattr(args, 'format', None))


def entrypoint():
    """Sets up program environment."""
    parser = argparse.ArgumentParser(prog='python3 -m eclair')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument(
        '--format', '-f', choices=available_formats(), help='default is plain text'
    )

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
