import logging
from urllib.request import urlopen
from urllib.parse import urlencode

from eclair.problem import ProblemPageParser, Problem


BASE_URL = 'https://projecteuler.net'


logger = logging.getLogger(__name__)


def get_problem(number: int) -> Problem:
    """Returns numbered problem statement."""
    url = '{0}/{1}'.format(BASE_URL, urlencode({'problem': number}))
    logger.debug('Executing query to %s', url)
    with urlopen(url) as response:
        logger.debug('Got %s response', response.reason)
        parser = ProblemPageParser()
        parser.feed(response.read().decode())
        return parser.problem
