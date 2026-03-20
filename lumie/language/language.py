# lumie/language/language.py
from __future__ import annotations

from threading import RLock
from typing import TYPE_CHECKING, Generic, TypeVar

from .term import Alias, EmptyTerm

if TYPE_CHECKING:
    from .symbol import Symbol

S = TypeVar('S', bound='Symbol')


class Language(Generic[S]):
    def __init__(self, symbol_type: type[S]):
        self.symbol_type = symbol_type
        self._lock: RLock = RLock()
        self._names: set[str] = set()
        self._symbols: dict[str, S] = {}
        self._aliases: dict[str, Alias[S]] = {}
        self._is_frozen: bool = False

    def empty_term(self) -> EmptyTerm[S]:
        return EmptyTerm(self.symbol_type)

    def add_symbol(self, symbol: S) -> None:
        with self._lock:
            if not isinstance(symbol, self.symbol_type):
                msg = f'Symbol must be an instance of {self.symbol_type.__name__}, got {type(symbol).__name__}'
                raise TypeError(msg)
            if self._is_frozen:
                msg = 'Cannot add symbol to a frozen language'
                raise ValueError(msg)
            if symbol.name in self._names:
                msg = f'Symbol name {symbol.name!r} already exists in the language'
                raise ValueError(msg)

            self._names.add(symbol.name)
            self._symbols[symbol.name] = symbol

    def add_alias(self, alias: Alias[S]) -> None:
        with self._lock:
            if not isinstance(alias, Alias):
                msg = f'Alias must be an instance of Alias, got {type(alias).__name__}'
                raise TypeError(msg)
            if self._is_frozen:
                msg = 'Cannot add alias to a frozen language'
                raise ValueError(msg)
            if alias.name in self._names:
                msg = f'Symbol name {alias.name!r} already exists in the language'
                raise ValueError(msg)
            self._names.add(alias.name)
            self._aliases[alias.name] = alias

    def freeze(self) -> None:
        with self._lock:
            self._is_frozen = True
