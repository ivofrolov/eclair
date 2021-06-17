import dataclasses
from typing import Mapping

from eclair.fsm import (
    StatefulHTMLParser,
    SpecialState,
    SpecialSymbol,
    TransitionTable,
    TransitionTarget,
)


@dataclasses.dataclass
class Problem:
    """Represents task title and problem statement."""

    prefix: str = ''
    title: str = ''
    statement: str = ''

    def __str__(self) -> str:
        problem = f'{self.prefix}: {self.title}\n\n{self.statement}'
        return problem


class ProblemPageParser(StatefulHTMLParser):
    """Extracts problem statement from html page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.problem = Problem()

    def _set_problem_title(self, data: str):
        self.problem.title = data

    def _set_problem_prefix(self, data: str):
        self.problem.prefix = data

    def _extend_problem_statement(self, data: str):
        self.problem.statement += data + '\n'

    def extract_qualifier(self, attrs: Mapping[str, str]) -> str:
        qualifier = attrs.get('id', attrs.get('role'))
        return qualifier

    def build_transitions(self) -> TransitionTable:
        transitions = {
            SpecialState.SKIP: {
                ('h2', None): TransitionTarget('title', None),
                ('div', 'problem_info'): TransitionTarget('prefix_container', None),
                ('div', 'problem'): TransitionTarget('statement_container', None),
            },
            'title': {
                SpecialSymbol.DATA: TransitionTarget(
                    'title_data', self._set_problem_title
                )
            },
            'prefix_container': {('h3', None): TransitionTarget('prefix', None)},
            'prefix': {
                SpecialSymbol.DATA: TransitionTarget(
                    'prefix_data', self._set_problem_prefix
                )
            },
            'statement_container': {('p', None): TransitionTarget('statement', None)},
            'statement': {
                SpecialSymbol.DATA: TransitionTarget(
                    'statement_data', self._extend_problem_statement
                )
            },
        }
        return transitions
