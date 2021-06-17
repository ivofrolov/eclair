from html.parser import HTMLParser
from enum import Enum
from typing import (
    Any,
    Callable,
    Hashable,
    Mapping,
    NamedTuple,
    NoReturn,
    Optional,
    Sequence,
    Tuple,
    Union,
)


class TransitionTarget(NamedTuple):
    state: str
    handler: Optional[Callable[Any, NoReturn]] = None


TransitionTable = Mapping[str, Mapping[Hashable, TransitionTarget]]


class SpecialSymbol(Enum):
    BACK = 'BACK'
    DATA = 'DATA'


class SpecialState(Enum):
    SKIP = 'SKIP'


class HtmlTraversalFSM:
    """Finite State Machine designed for HTML traversal."""

    def __init__(
        self,
        start_state: Union[str, SpecialState],
        transitions: TransitionTable,
    ):
        self.start_state = start_state
        self.transitions = transitions

        self.current_state = start_state
        self.states_stack = [start_state]

    def transition_exists(
        self, state: Union[str, SpecialState], symbol: Hashable
    ) -> bool:
        if state not in self.transitions:
            return False
        if symbol not in self.transitions[state]:
            return False
        return True

    def change_state(self, symbol: Hashable, data: Any = None):
        if symbol == SpecialSymbol.BACK:
            self.states_stack.pop()
            self.current_state = self.states_stack[-1]
            return

        if self.transition_exists(self.current_state, symbol):
            state, handler = self.transitions[self.current_state][symbol]
            if callable(handler):
                handler(data)
        else:
            state = SpecialState.SKIP

        self.states_stack.append(state)
        self.current_state = state


class StatefulHTMLParser(HTMLParser):
    """Traverses nested html tags and extracts useful data in one pass."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fsm = HtmlTraversalFSM('start', self.build_transitions())

    def build_transitions(self) -> TransitionTable:
        raise NotImplementedError

    def extract_qualifier(self, attrs: Mapping[str, str]) -> str:
        raise NotImplementedError

    def handle_starttag(self, tag: str, attrs: Sequence[Tuple[str, str]]):
        qualifier = self.extract_qualifier(dict(attrs))
        self._fsm.change_state((tag, qualifier))

    def handle_data(self, data: str):
        self._fsm.change_state(SpecialSymbol.DATA, data)
        self._fsm.change_state(SpecialSymbol.BACK)

    def handle_endtag(self, tag: str):
        self._fsm.change_state(SpecialSymbol.BACK)
