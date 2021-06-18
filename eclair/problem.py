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
        self.problem.statement += data

    def _end_problem_statement(self):
        self.problem.statement += '\n'

    def extract_qualifier(self, attrs: Mapping[str, str]) -> str:
        qualifier = attrs.get('id', attrs.get('role'))
        return qualifier

    def build_transitions(self) -> TransitionTable:
        transitions = {
            SpecialState.SKIP: {
                ('h2', None): TransitionTarget('title'),
                ('div', 'problem_info'): TransitionTarget('prefix_container'),
                ('div', 'problem'): TransitionTarget('statement_container'),
            },
            'title': {
                SpecialSymbol.DATA: TransitionTarget(
                    'title_data', on_enter=self._set_problem_title
                )
            },
            'prefix_container': {('h3', None): TransitionTarget('prefix')},
            'prefix': {
                SpecialSymbol.DATA: TransitionTarget(
                    'prefix_data', on_enter=self._set_problem_prefix
                )
            },
            'statement_container': {
                ('p', None): TransitionTarget(
                    'statement', on_exit=self._end_problem_statement
                ),
                SpecialSymbol.DATA: TransitionTarget(
                    'statement_data', on_enter=self._extend_problem_statement
                ),
            },
            'statement': {
                SpecialSymbol.DATA: TransitionTarget(
                    'statement_data', on_enter=self._extend_problem_statement
                ),
                SpecialSymbol.ANY: TransitionTarget('statement_markup'),
            },
            'statement_markup': {
                SpecialSymbol.DATA: TransitionTarget(
                    'statement_data', on_enter=self._extend_problem_statement
                ),
            },
        }
        return transitions
