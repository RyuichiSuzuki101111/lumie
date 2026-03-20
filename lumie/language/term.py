# lumie/language/_term.py
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

if TYPE_CHECKING:
    from .symbol import Symbol


S = TypeVar('S', bound='Symbol')


class Term(Protocol[S]):
    def __mul__(self, other: Term[S]) -> Mul[S]: ...
    def __truediv__(self, other: Term[S]) -> Div[S]: ...
    def __pow__(self, exp: int) -> Pow[S]: ...
    def invert(self) -> Term[S]: ...
    def rational_power(self, exp_num: int, exp_den: int) -> Pow[S]: ...
    def alias(self, name: str) -> Alias[S]: ...
    @classmethod
    def empty(cls) -> EmptyTerm[S]: ...

    # Because Term is not interested in the semantics of terms, two terms are considered equal if they have the same construction tree.
    # For example, (s * t) and (t * s) are not equal even if s and t are the same symbol.
    def __eq__(self, other: object) -> bool: ...


class _TermMixIn(Generic[S]):
    def __mul__(self, other: Term[S]) -> Mul[S]:
        return Mul(self, other)

    def __truediv__(self, other: Term[S]) -> Div[S]:
        return Div(self, other)

    def __pow__(self, exp: int) -> Pow[S]:
        return self.rational_power(exp, 1)

    def invert(self) -> Invert[S]:
        return Invert(self)

    def rational_power(self, exp_num: int, exp_den: int) -> Pow[S]:
        return Pow(self, exp_num, exp_den)

    def alias(self, name: str) -> Alias[S]:
        return Alias(name, self)

    @classmethod
    def empty(cls) -> EmptyTerm[S]:
        # 例えば Div(s, s) のような Term の reduce 結果として EmptyTerm が必要になることがある。
        return EmptyTerm()


@dataclass(frozen=True, slots=True)
class EmptyTerm(Generic[S], _TermMixIn[S]):
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, EmptyTerm):
            return NotImplemented
        return True


@dataclass(frozen=True, slots=True)
class Mul(Generic[S], _TermMixIn[S]):
    lhs: Term[S]
    rhs: Term[S]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mul):
            return NotImplemented
        return self.lhs == other.lhs and self.rhs == other.rhs


@dataclass(frozen=True, slots=True)
class Div(Generic[S], _TermMixIn[S]):
    lhs: Term[S]
    rhs: Term[S]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Div):
            return NotImplemented
        return self.lhs == other.lhs and self.rhs == other.rhs


@dataclass(frozen=True, slots=True)
class Pow(Generic[S], _TermMixIn[S]):
    base: Term[S]
    exponent_num: int
    exponent_den: int = 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pow):
            return NotImplemented
        return (
            self.base == other.base
            and self.exponent_num == other.exponent_num
            and self.exponent_den == other.exponent_den
        )


@dataclass(frozen=True, slots=True)
class Invert(Generic[S], _TermMixIn[S]):
    term: Term[S]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Invert):
            return NotImplemented
        return self.term == other.term


@dataclass(frozen=True, slots=True)
class Alias(Generic[S], _TermMixIn[S]):
    name: str
    target: Term[S]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Alias):
            return NotImplemented
        return self.name == other.name and self.target == other.target

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'Alias(name={self.name!r}, target={self.target!r})'
