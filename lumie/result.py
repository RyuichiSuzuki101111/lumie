# lumie/result.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any, NoReturn, Protocol, TypeVar, cast, overload

if TYPE_CHECKING:
    from collections.abc import Callable

R_co = TypeVar('R_co', covariant=True)
E_co = TypeVar('E_co', covariant=True)
R = TypeVar('R')
E = TypeVar('E')
T = TypeVar('T')


class _Missing:
    """A sentinel value to indicate that a value was not provided. This is used to distinguish between a value that was explicitly provided as None and a value that was not provided at all."""


MISSING = _Missing()


class UnwrapError(Exception):
    """An error raised when trying to unwrap a Result that is an Err, or unwrap_err a Result that is an Ok."""


class Result(Protocol[R_co, E_co]):
    def is_ok(self) -> bool: ...
    def is_err(self) -> bool: ...
    @overload
    def unwrap(self) -> R_co: ...
    @overload
    def unwrap(self, default: T) -> R_co | T: ...
    @overload
    def unwrap_err(self) -> E_co: ...
    @overload
    def unwrap_err(self, default: T) -> E_co | T: ...
    def map(self, func: Callable[[R_co], T]) -> Result[T, E_co]: ...
    def map_err(self, func: Callable[[E_co], T]) -> Result[R_co, T]: ...


class Ok(Result[R, Any]):
    def __init__(self, value: R) -> None:
        self._value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    @overload
    def unwrap(self) -> R: ...

    @overload
    def unwrap(self, default: T) -> R | T: ...

    def unwrap(self, default: T | _Missing = MISSING) -> R:  # noqa: ARG002
        return self._value

    @overload
    def unwrap_err(self) -> NoReturn: ...
    @overload
    def unwrap_err(self, default: T) -> T: ...

    def unwrap_err(self, default: T | _Missing = MISSING) -> T:
        if default is MISSING:
            msg = 'No error in Ok result'
            raise UnwrapError(msg)
        assert not isinstance(default, _Missing)
        return default

    def map(self, func: Callable[[R], T]) -> Result[T, Any]:
        return Ok(func(self._value))

    def map_err(self, func: Callable[[Any], T]) -> Result[R, T]:  # noqa: ARG002
        return cast('Result[R, T]', self)


class Err(Result[Any, E]):
    def __init__(self, error: E) -> None:
        self._error = error

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    @overload
    def unwrap(self) -> NoReturn: ...
    @overload
    def unwrap(self, default: T) -> T: ...

    def unwrap(self, default: T | _Missing = MISSING) -> T:
        if default is MISSING:
            msg = 'No result in Err result'
            raise UnwrapError(msg)
        assert not isinstance(default, _Missing)
        return default

    @overload
    def unwrap_err(self) -> E: ...
    @overload
    def unwrap_err(self, default: T) -> E | T: ...

    def unwrap_err(self, default: T | _Missing = MISSING) -> E | T:  # noqa: ARG002
        return self._error

    def map(self, func: Callable[[R], T]) -> Result[T, E]:  # noqa: ARG002
        return cast('Result[T, E]', self)

    def map_err(self, func: Callable[[E], T]) -> Result[Any, T]:
        return Err(func(self._error))
