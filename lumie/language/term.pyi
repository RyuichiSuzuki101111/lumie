# lumie/language/term.pyi
from __future__ import annotations

from typing import Protocol, TypeVar

from lumie.symbol import Symbol

from ._term import Alias, Div, EmptyTerm, Mul, Pow, _Term

__all__ = ('Alias', 'Div', 'EmptyTerm', 'Mul', 'Pow', 'Term')

S = TypeVar('S', bound=Symbol)

class Term(_Term[S], Protocol): ...
