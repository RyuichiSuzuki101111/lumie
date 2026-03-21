# lumie/scale/scalar_scale.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from typing_extensions import Self

from ._core import ComparisonResult, UnsupportedScaleError

if TYPE_CHECKING:
    from collections.abc import Callable

    from .scalar_scale_impl import ScalarScaleImpl


T = TypeVar('T')


class ScalarScale:
    impl: ClassVar[ScalarScaleImpl[Any]]

    __slots__ = ('_hash', '_raw')

    _raw: Any
    _hash: int | None

    def __init__(self, value: Any) -> None:  # noqa: ANN401
        if isinstance(value, type(self)):
            object.__setattr__(self, '_raw', value._raw)
        else:
            raw = type(self).impl.to_repr(value)
            object.__setattr__(self, '_raw', raw)
            shape = type(self).impl.shape(self._raw)
            if shape is not None:
                msg = f'Expected a scalar value, but got {value!r} with shape {shape}'
                raise ValueError(msg)
        object.__setattr__(self, '_hash', None)

    def __setattr__(self, key: str, value: Any) -> None:  # noqa: ANN401
        msg = f'{type(self).__name__} instances are immutable'
        raise AttributeError(msg)

    @classmethod
    def _with_raw(cls, raw: Any) -> Self:  # noqa: ANN401
        instance = cls.__new__(cls)
        object.__setattr__(instance, '_raw', raw)
        object.__setattr__(instance, '_hash', None)
        return instance

    def __abs__(self) -> Self:
        result = type(self).impl.abs(self._raw)
        return type(self)._with_raw(result)

    def __add__(self, other: Self) -> Self:
        if type(self) is not type(other):
            return NotImplemented
        result = type(self).impl.add(self._raw, other._raw)
        return type(self)._with_raw(result)

    def __sub__(self, other: Self) -> Self:
        if type(self) is not type(other):
            return NotImplemented
        result = type(self).impl.sub(self._raw, other._raw)
        return type(self)._with_raw(result)

    def __mul__(self, other: Self) -> Self:
        if type(self) is not type(other):
            return NotImplemented
        result = type(self).impl.mul(self._raw, other._raw)
        return type(self)._with_raw(result)

    def __truediv__(self, other: Self) -> Self:
        if type(self) is not type(other):
            return NotImplemented
        if type(self).impl.is_zero(other._raw):
            msg = 'Cannot divide by zero'
            raise ZeroDivisionError(msg)
        result = type(self).impl.div(self._raw, other._raw)
        return type(self)._with_raw(result)

    def __neg__(self) -> Self:
        result = type(self).impl.neg(self._raw)
        return type(self)._with_raw(result)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        assert isinstance(other, ScalarScale)
        result = ComparisonResult(type(self).impl.compare(self._raw, other._raw))
        return result is ComparisonResult.ORDERED_SAME

    def __lt__(self, other: Self) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        result = ComparisonResult(type(self).impl.compare(self._raw, other._raw))
        match result:
            case ComparisonResult.ORDERED_ASCENDING:
                return True
            case ComparisonResult.ORDERED_DESCENDING | ComparisonResult.ORDERED_SAME:
                return False
            case ComparisonResult.INCOMPARABLE:
                msg = f'Cannot compare {self!r} and {other!r}'
                raise ValueError(msg)

    def __le__(self, other: Self) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        result = ComparisonResult(type(self).impl.compare(self._raw, other._raw))
        match result:
            case ComparisonResult.ORDERED_ASCENDING | ComparisonResult.ORDERED_SAME:
                return True
            case ComparisonResult.ORDERED_DESCENDING:
                return False
            case ComparisonResult.INCOMPARABLE:
                msg = f'Cannot compare {self!r} and {other!r}'
                raise ValueError(msg)

    def __gt__(self, other: Self) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        result = ComparisonResult(type(self).impl.compare(self._raw, other._raw))
        match result:
            case ComparisonResult.ORDERED_DESCENDING:
                return True
            case ComparisonResult.ORDERED_ASCENDING | ComparisonResult.ORDERED_SAME:
                return False
            case ComparisonResult.INCOMPARABLE:
                msg = f'Cannot compare {self!r} and {other!r}'
                raise ValueError(msg)

    def __ge__(self, other: Self) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        result = ComparisonResult(type(self).impl.compare(self._raw, other._raw))
        match result:
            case ComparisonResult.ORDERED_DESCENDING | ComparisonResult.ORDERED_SAME:
                return True
            case ComparisonResult.ORDERED_ASCENDING:
                return False
            case ComparisonResult.INCOMPARABLE:
                msg = f'Cannot compare {self!r} and {other!r}'
                raise ValueError(msg)

    def __hash__(self) -> int:
        if self._hash is None:
            hash_value = type(self).impl.hash(self._raw)
            object.__setattr__(self, '_hash', hash_value)
        assert self._hash is not None
        return self._hash

    def as_(self, dtype: type[T]) -> T:
        try:
            return type(self).impl.as_(self._raw, dtype)
        except UnsupportedScaleError as exc:
            msg = f'{type(self).__name__} cannot be converted to {dtype.__name__}'
            raise TypeError(msg) from exc

    def __float__(self) -> float:
        try:
            return self.as_(float)
        except TypeError:
            msg = f'{type(self).__name__} cannot be converted to float'
            raise TypeError(msg) from None

    def __complex__(self) -> complex:
        try:
            return self.as_(complex)
        except TypeError:
            pass

        try:
            return complex(self.as_(float))
        except TypeError:
            msg = f'{type(self).__name__} cannot be converted to complex'
            raise TypeError(msg) from None

    def __str__(self) -> str:
        return type(self).impl.format_value(self._raw)

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}({type(self).impl.format_value_detailed(self._raw)})'
        )

    @classmethod
    def _reconstruct(cls, raw: Any, hash_: int | None) -> Self:  # noqa: ANN401
        instance = cls.__new__(cls)
        object.__setattr__(instance, '_raw', raw)
        object.__setattr__(instance, '_hash', hash_)
        return instance

    def __reduce__(self) -> tuple[Callable[..., Self], tuple[Any, int | None]]:
        return (type(self)._reconstruct, (self._raw, self._hash))
