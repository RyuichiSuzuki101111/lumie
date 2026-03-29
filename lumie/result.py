# lumie/result.py
"""
A lightweight Result type for Python.

Design principles:
- Treat Result as a flow container, not a sum type to be pattern-matched eagerly.
- Prefer chaining (map / and_then) over branching.
- Ok / Err are exposed for pattern matching, but cannot be instantiated directly.
- Type hints are best-effort and may use Any where strict typing would harm usability.

Use ok(...) and err(...) to construct values.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    Protocol,
    TypeVar,
    cast,
    final,
    overload,
)

if TYPE_CHECKING:
    from collections.abc import Callable

R_co = TypeVar('R_co', covariant=True)
R = TypeVar('R')
E = TypeVar('E')
F = TypeVar('F')
T = TypeVar('T')


class UnwrapError(Exception):
    """An error raised when trying to unwrap a Result that is an Err, or unwrap_err a Result that is an Ok."""


@final
class Ok(Generic[R]):
    """
    Represents a successful result.

    This class is intended for pattern matching only:
        match result:
            case Ok(value): ...

    Do not instantiate directly. Use ok(...) instead.
    """

    __match_args__ = ('_value',)
    __slots__ = ('_value',)
    _value: R

    def __init__(self, value: R) -> None:  # noqa: ARG002
        msg = 'Ok cannot be instantiated directly, use ok() instead'
        raise TypeError(msg)

    def __setattr__(self, key: str, value: Any) -> None:  # noqa: ANN401
        msg = 'Ok instances are immutable'
        raise AttributeError(msg)

    @property
    def is_ok(self) -> Literal[True]:
        return True

    @property
    def is_err(self) -> Literal[False]:
        return False

    def unwrap(self) -> R:
        return self._value

    def unwrap_or(self, default: T) -> R | T:  # noqa: ARG002
        return self._value

    def unwrap_err(self) -> Any:  # noqa: ANN401
        msg = f'Called unwrap_err on Ok: {self._value!r}'
        raise UnwrapError(msg)

    def and_then(self, func: Callable[[R], Result[T, E]]) -> Result[T, E]:
        return func(self._value)

    def map(self, func: Callable[[R], T]) -> Result[T, Any]:
        return ok(func(self._value))

    def map_err(self, func: Callable[[Any], T]) -> Result[R, T]:  # noqa: ARG002
        return cast('Result[R, T]', self)

    def __str__(self) -> str:
        return f'Ok({self._value})'

    def __repr__(self) -> str:
        return f'Ok({self._value!r})'


@final
class Err(Generic[E]):
    """
    Represents a failed result.

    This class is intended for pattern matching only:
        match result:
            case Err(error): ...

    Do not instantiate directly. Use err(...) instead.
    """

    __match_args__ = ('_error',)
    __slots__ = ('_error',)
    _error: E

    def __init__(self, error: E) -> None:  # noqa: ARG002
        msg = 'Err cannot be instantiated directly, use err() instead'
        raise TypeError(msg)

    def __setattr__(self, key: str, value: Any) -> None:  # noqa: ANN401
        msg = 'Err instances are immutable'
        raise AttributeError(msg)

    @property
    def is_ok(self) -> Literal[False]:
        return False

    @property
    def is_err(self) -> Literal[True]:
        return True

    def unwrap(self) -> Any:  # noqa: ANN401
        msg = f'Called unwrap on Err: {self._error!r}'
        raise UnwrapError(msg)

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_err(self) -> E:
        return self._error

    def and_then(self, func: Callable[[Any], Result[T, E]]) -> Result[T, E]:  # noqa: ARG002
        return err(self._error)

    def map(self, func: Callable[[R], T]) -> Result[T, E]:  # noqa: ARG002
        return cast('Result[T, E]', err(self._error))

    def map_err(self, func: Callable[[E], F]) -> Result[Any, F]:
        return err(func(self._error))


class Result(Protocol[R_co, E]):
    """
    A Result represents a computation that may succeed (Ok) or fail (Err).

    The primary usage is chaining via:
        - map       (transform success)
        - and_then  (chain computations)
        - map_err   (transform error)

    Avoid branching on Ok/Err where possible; prefer chaining.
    """

    @property
    def is_ok(self) -> bool: ...
    @property
    def is_err(self) -> bool: ...

    def unwrap(self) -> R_co:
        """Return the success value or raise UnwrapError if this is an Err."""

    def unwrap_or(self, default: T) -> R_co | T:
        """Return the success value or default if this is an Err."""

    def unwrap_err(self) -> E:
        """Return the error or raise UnwrapError if this is an Ok."""

    def and_then(self, func: Callable[[R_co], Result[T, E]]) -> Result[T, E]:
        """
        Chain computations that may fail.

        The error type is preserved (E is not changed).
        Use map_err to transform errors explicitly.
        """

    def map(self, func: Callable[[R_co], T]) -> Result[T, E]:
        """Transform the success value, preserving the error."""

    def map_err(self, func: Callable[[E], F]) -> Result[R_co, F]:
        """Transform the error value, preserving the success."""


class _Missing(Enum):
    MISSING = auto()


MISSING = _Missing.MISSING


@overload
def ok(value: R) -> Result[R, Any]: ...
@overload
def ok(value: R, *, err_type: type[E]) -> Result[R, E]: ...
def ok(value: R, *, err_type: type[E] | _Missing = MISSING) -> Result[R, Any]:  # noqa: ARG001
    """
    Construct a successful Result.

    err_type is only for type hinting and has no effect at runtime.
    It can be used to specify the error type when it cannot be inferred.
    """

    instance = object.__new__(Ok)
    object.__setattr__(instance, '_value', value)
    return instance


@overload
def err(error: E) -> Result[Any, E]: ...
@overload
def err(error: E, *, ok_type: type[R]) -> Result[R, E]: ...
@overload
def err(error: E, *, ok_type: None) -> Result[None, E]: ...


def err(error: E, *, ok_type: type[R] | None | _Missing = MISSING) -> Result[Any, E]:  # noqa: ARG001
    """
    Construct a failed Result.

    ok_type is only for type hinting and has no effect at runtime.
    It can be used to specify the success type when it cannot be inferred.

    Passing ok_type=None produces Result[None, E].
    """

    instance = object.__new__(Err)
    object.__setattr__(instance, '_error', error)
    return instance
