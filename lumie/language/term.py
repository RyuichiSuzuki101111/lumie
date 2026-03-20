# lumie/language/term.py
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, TypeVar, overload

from lumie.symbol.symbol import Symbol

if TYPE_CHECKING:
    from ._term import Alias, Div, EmptyTerm, Mul, Pow, _Term

__all__ = ('Term',)

S = TypeVar('S', bound=Symbol)


class Term(_Term[S], Protocol[S]): ...


@overload
def __getattr__(name: Literal['Mul']) -> type[Mul]: ...
@overload
def __getattr__(name: Literal['Div']) -> type[Div]: ...
@overload
def __getattr__(name: Literal['Pow']) -> type[Pow]: ...
@overload
def __getattr__(name: Literal['Alias']) -> type[Alias]: ...
@overload
def __getattr__(name: Literal['NullTerm']) -> type[EmptyTerm]: ...


def __getattr__(name: str) -> object:
    if name in {'Mul', 'Div', 'Pow', 'Alias', 'NullTerm'}:
        from . import _term

        attr = getattr(_term, name)
        globals()[name] = attr
        return attr
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
