# lumie/language/_term.py
from __future__ import annotations

from dataclasses import dataclass, field
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

    def __hash__(self) -> int: ...
    # Because the interest of Term is its form, not its semantics, two terms are considered equal if they have the same construction tree.
    # For example, (s * t) and (t * s) are not equal even if s and t are the same symbol.
    def __eq__(self, other: object) -> bool: ...


class TermMixIn(Generic[S]):
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

    def __eq__(self, other: object) -> bool:
        msg = 'Subclasses of TermMixIn must implement __eq__'
        raise NotImplementedError(msg)


class _CachedHash:
    # Subclass should have a _hash field of type int | None with default value None,
    # and implement _compute_hash method to compute the hash value when _hash is None.
    _hash: int | None

    def _compute_hash(self) -> int:
        msg = 'Subclasses of _CachedHash must implement _compute_hash'
        raise NotImplementedError(msg)

    def __hash__(self) -> int:
        if self._hash is None:
            hash_value = self._compute_hash()
            # Since the class is frozen, we need to use object.__setattr__ to set the _hash attribute.
            object.__setattr__(self, '_hash', hash_value)
        assert self._hash is not None
        return self._hash


@dataclass(frozen=True, slots=True)
class EmptyTerm(Generic[S], TermMixIn[S], _CachedHash):
    symbol_type: type[S]
    _hash: int | None = field(init=False, repr=False, default=None)

    def _compute_hash(self) -> int:
        return hash((type(self), self.symbol_type))

    def __eq__(self, value: object) -> bool:
        if self is value:
            return True
        if not isinstance(value, EmptyTerm):
            return NotImplemented
        return self.symbol_type == value.symbol_type


@dataclass(frozen=True, slots=True)
class Mul(Generic[S], TermMixIn[S], _CachedHash):
    lhs: Term[S]
    rhs: Term[S]
    _hash: int | None = field(init=False, repr=False, default=None)

    def _compute_hash(self) -> int:
        return hash((type(self), self.lhs, self.rhs))

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, Mul):
            return NotImplemented
        return self.lhs == other.lhs and self.rhs == other.rhs


@dataclass(frozen=True, slots=True)
class Div(Generic[S], TermMixIn[S], _CachedHash):
    lhs: Term[S]
    rhs: Term[S]
    _hash: int | None = field(init=False, repr=False, default=None)

    def _compute_hash(self) -> int:
        return hash((type(self), self.lhs, self.rhs))

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, Div):
            return NotImplemented
        return self.lhs == other.lhs and self.rhs == other.rhs


@dataclass(frozen=True, slots=True)
class Pow(Generic[S], TermMixIn[S], _CachedHash):
    base: Term[S]
    exponent_num: int
    exponent_den: int = 1
    _hash: int | None = field(init=False, repr=False, default=None)

    def _compute_hash(self) -> int:
        return hash((type(self), self.base, self.exponent_num, self.exponent_den))

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, Pow):
            return NotImplemented
        return (
            self.base == other.base
            and self.exponent_num == other.exponent_num
            and self.exponent_den == other.exponent_den
        )


@dataclass(frozen=True, slots=True)
class Invert(Generic[S], TermMixIn[S], _CachedHash):
    term: Term[S]
    _hash: int | None = field(init=False, repr=False, default=None)

    def _compute_hash(self) -> int:
        return hash((type(self), self.term))

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, Invert):
            return NotImplemented
        return self.term == other.term


@dataclass(frozen=True, slots=True)
class Alias(Generic[S], TermMixIn[S], _CachedHash):
    name: str
    target: Term[S]
    _hash: int | None = field(init=False, repr=False, default=None)

    def _compute_hash(self) -> int:
        return hash((type(self), self.name, self.target))

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, Alias):
            return NotImplemented
        return self.name == other.name and self.target == other.target

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name={self.name!r}, target={self.target!r})'
