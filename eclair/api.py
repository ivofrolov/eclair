import logging
import enum
import dataclasses

from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.parse import urlencode


BASE_URL = 'https://projecteuler.net'


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Problem:
    prefix: str = ''
    title: str = ''
    content: str = ''

    def __str__(self):
        problem = f'{self.prefix}. {self.title}\n\n{self.content}'
        return problem


class ParseState(enum.IntEnum):
    start = enum.auto()
    idle = enum.auto()
    title = enum.auto()
    prefix = enum.auto()
    content = enum.auto()


class ProblemPageParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = ParseState.start
        self._problem = Problem()

    @property
    def problem(self) -> Problem:
        return self._problem

    def next_state(self):
        self._state = self._state.next()

    def handle_starttag(self, tag: str, attrs):
        # <div id="content">
        if tag == 'div' and self._state == ParseState.start:
            attrs = dict(attrs)
            if attrs.get('id') == 'content':
                self._state = ParseState.idle
                return

        # <h2>Multiples of 3 and 5</h2>
        if tag == 'h2' and self._state == ParseState.idle:
            self._state = ParseState.title
            return

        # <h3>Problem 1</h3>
        if tag == 'h3' and self._state == ParseState.idle:
            self._state = ParseState.prefix
            return

        # <div class="problem_content" role="problem">
        if tag == 'div' and self._state == ParseState.idle:
            attrs = dict(attrs)
            if attrs.get('role') == 'problem':
                self._state = ParseState.content
                return

        if tag != 'p' and self._state == ParseState.content:
            self._state = ParseState.idle

    def handle_data(self, data: str):
        if self._state == ParseState.title:
            self._problem.title = data.strip()
            self._state = ParseState.idle
            return

        if self._state == ParseState.prefix:
            self._problem.prefix = data.strip()
            self._state = ParseState.idle
            return

        if self._state == ParseState.content:
            self._problem.content = (self._problem.content + '\n' + data).strip()
            return


def get_problem(number: int) -> Problem:
    url = '{0}/{1}'.format(BASE_URL, urlencode({'problem': number}))
    logger.debug('Executing query to %s', url)
    with urlopen(url) as response:
        parser = ProblemPageParser()
        parser.feed(response.read().decode())
        return parser.problem