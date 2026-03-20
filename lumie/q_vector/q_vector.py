# lumie/q_vector/q_vector.py
from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, ClassVar, Generic, TypeVar

from typing_extensions import Self

from lumie.symbol import Symbol

from .q_vector_impl import QVectorImpl

S = TypeVar('S', bound=Symbol)


class QVector(Generic[S]):
    # QVector does not interested in the actual type of the vector representatino, i.e. V in QVectorBackend[V],
    # so we use Any here to avoid making QVector generic over the vector type.
    symbol_type: ClassVar[Any]
    impl: ClassVar[QVectorImpl[Any]]
    # NOTE:
    # Ideally this should be `ClassVar[Mapping[S, int]]`, but Python's type system
    # does not allow using class-level generics (S) in ClassVar in a sound way.
    # We use `Any` here and rely on __init_subclass__ to enforce correctness.

    # A mapping from symbol to indices (or ordinals of coordinates) in the vector representation.
    # This is used to convert between the user-facing symbol-based representation and the internal vector representation.
    symbol_index: ClassVar[Mapping[Any, int]]
    # The inverse mapping of symbol_index, from indices to symbols.
    index_symbol: ClassVar[Mapping[int, Any]]

    @classmethod
    def __init_subclass__(
        cls,
        impl: QVectorImpl[Any],
        symbol_index: dict[S, int],
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        cls.impl = impl
        symbol_index = dict(symbol_index)
        symbol_types = {type(symbol) for symbol in symbol_index}

        if len(symbol_types) != 1:
            msg = f'All symbols in symbol_index must be of the same type, got {symbol_types}'
            raise TypeError(msg)
        cls.symbol_type = next(iter(symbol_types))

        index_symbol: dict[int, S] = {}

        # check the symbol_index and build the inverse mapping at the same time
        for symbol, index in symbol_index.items():
            if not isinstance(symbol, cls.symbol_type):
                msg = f'Symbol index keys must be of type {cls.symbol_type}, got {symbol!r} of type {type(symbol)}'
                raise TypeError(msg)
            if not isinstance(index, int):
                msg = f'Symbol index values must be of type int, got {index!r} of type {type(index)}'
                raise TypeError(msg)
            if index_symbol.setdefault(index, symbol) is not symbol:
                msg = f'Index {index} is assigned to multiple symbols: {symbol!r} and {index_symbol[index]!r}'
                raise ValueError(msg)

        cls.symbol_index = MappingProxyType(symbol_index)
        cls.index_symbol = MappingProxyType(index_symbol)

    def __init__(
        self,
        expr: dict[S, tuple[int, int]],
    ) -> None:
        resolved_expr = {
            self.symbol_index[symbol]: value for symbol, value in expr.items()
        }
        self._vector = self.impl.dict_to_vector(resolved_expr)

    @classmethod
    def _with_vector(cls, vector: Any) -> Self:
        instance = cls.__new__(cls)
        instance._vector = vector
        return instance

    def to_dict(self) -> dict[S, tuple[int, int]]:
        result: dict[S, tuple[int, int]] = {}

        for index, value in self.impl.vector_to_dict(self._vector).items():
            if value != (0, 1):
                symbol = self.index_symbol[index]
                result[symbol] = value

        return result

    @classmethod
    def zero(cls) -> Self:
        # zero の表現はimplによっては状態を持つかもしれないので毎回implから取得するようにする
        return cls._with_vector(cls.impl.zero())

    @classmethod
    def unit_vector(cls, symbol: S) -> Self:
        if symbol not in cls.symbol_index:
            msg = f'Symbol {symbol!r} is not in symbol_index'
            raise ValueError(msg)
        index = cls.symbol_index[symbol]
        return cls._with_vector(cls.impl.unit_vector(index))

    def __add__(self, other: Self) -> Self:
        if type(self) is not type(other):
            return NotImplemented
        result_vector = self.impl.add(self._vector, other._vector)
        return type(self)._with_vector(result_vector)

    def __sub__(self, other: Self) -> Self:
        if type(self) is not type(other):
            return NotImplemented
        result_vector = self.impl.sub(self._vector, other._vector)
        return type(self)._with_vector(result_vector)

    def __neg__(self) -> Self:
        result_vector = self.impl.neg(self._vector)
        return type(self)._with_vector(result_vector)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        # Help type checkers understand both operands share the same impl.
        assert isinstance(other, type(self))
        return self.impl.eq(self._vector, other._vector)

    def scalar_mul(self, scalar_num: int, scalar_den: int) -> Self:
        result_vector = self.impl.scalar_mul(self._vector, scalar_num, scalar_den)
        return type(self)._with_vector(result_vector)
