# lumie/result.py
"""
A lightweight internal Result type.

This module provides a small Result abstraction used mainly at internal
backend boundaries, where returning an error value is preferable to raising
and catching exceptions.

Design intent:
- This is a utility for internal flows, not a primary user-facing API.
- Expected failures are represented as Result values rather than exceptions.
- Branching is commonly done via pattern matching on Ok / Err.
- Ok / Err are exposed for matching and representation, but are not intended
  to be instantiated directly.
- Type hints are best-effort. In some places, `Any` is used intentionally to
  avoid overstating guarantees on the concrete Ok / Err representations.

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
S = TypeVar('S')
E = TypeVar('E')
F = TypeVar('F')
T = TypeVar('T')


class UnwrapError(Exception):
    """Raised when unwrap() or unwrap_err() is called on the wrong Result variant."""


@final
class Ok(Generic[R]):
    """
    Internal representation of a successful Result.

    This class is exposed primarily so Result values can be pattern-matched:

        match result:
            case Ok(value): ...

    It is not intended to be instantiated directly or treated as the primary
    abstraction in user code. Construct values with ok(...), and prefer working
    against the Result interface.

    Some method signatures use `Any` intentionally. Ok/Err are concrete internal
    representations, and stricter typing on them would overstate guarantees that
    are only meaningful at the Result boundary.
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

    def and_then(self, func: Callable[[R], Result[S, Any]]) -> Result[S, Any]:
        return func(self._value)

    def map(self, func: Callable[[R], T]) -> Result[T, Any]:
        return ok(func(self._value))

    def map_err(self, func: Callable[[Any], F]) -> Result[R, F]:  # noqa: ARG002
        return cast('Result[R, F]', self)

    def __str__(self) -> str:
        return f'Ok({self._value})'

    def __repr__(self) -> str:
        return f'Ok({self._value!r})'


@final
class Err(Generic[E]):
    """
    Internal representation of a failed Result.

    This class is exposed primarily so Result values can be pattern-matched:

        match result:
            case Err(error): ...

    It is not intended to be instantiated directly or treated as the primary
    abstraction in user code. Construct values with err(...), and prefer working
    against the Result interface.

    Some method signatures use `Any` intentionally. In particular, methods such
    as and_then may not use their callable argument at all, so stricter typing on
    Err itself would add constraints without improving correctness at the Result
    boundary.
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

    def and_then(self, func: Callable[[Any], Result[S, E]]) -> Result[S, E]:  # noqa: ARG002
        return err(self._error)

    def map(self, func: Callable[[R], S]) -> Result[S, E]:  # noqa: ARG002
        return cast('Result[S, E]', err(self._error))

    def map_err(self, func: Callable[[E], F]) -> Result[Any, F]:
        return err(func(self._error))


class Result(Protocol[R_co, E]):
    """
    A Result represents either a successful value (Ok) or an error value (Err).

    This is a typing protocol used mainly for internal backend-facing flows.
    It is not a runtime base class.

    Typical usage is:
    - return ok(...) / err(...) from backend operations
    - branch on the result via pattern matching
    - use map / and_then / map_err when local transformation is more convenient

    Pattern matching is the most direct way to consume a Result:

        match result:
            case Ok(value): ...
            case Err(error): ...
    """

    @property
    def is_ok(self) -> bool:
        """
        Return True if this Result is Ok.

        This property is a runtime guard for operations such as unwrap().
        It is not intended as a type narrowing mechanism.

        In particular, type checkers should not be expected to treat
        `if result.is_ok:` as narrowing Result[T, E] to Ok[T], and this is
        intentional. When branching on Result values, prefer pattern matching
        on Ok / Err.
        """

    @property
    def is_err(self) -> bool:
        """
        Return True if this Result is Err.

        This property is a runtime guard for operations such as unwrap_err().
        It is not intended as a type narrowing mechanism.

        When branching on Result values, prefer pattern matching on Ok / Err.
        """

    def unwrap(self) -> R_co:
        """Return the success value, or raise UnwrapError if this is an Err."""

    def unwrap_or(self, default: T) -> R_co | T:
        """Return the success value, or default if this is an Err."""

    def unwrap_err(self) -> E:
        """Return the error value, or raise UnwrapError if this is an Ok."""

    def and_then(self, func: Callable[[R_co], Result[S, E]]) -> Result[S, E]:
        """
        Apply a function returning Result to the success value.

        This is useful when composing Result-returning operations without
        branching explicitly.
        """

    def map(self, func: Callable[[R_co], S]) -> Result[S, E]:
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

    err_type is for type checking only and has no runtime effect. It can be
    used when the error type cannot be inferred.

    Ok instances are created indirectly so that Ok remains matchable but is not
    directly instantiated in normal use.
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

    ok_type is for type checking only and has no runtime effect. It can be
    used when the success type cannot be inferred.

    Passing ok_type=None produces Result[None, E].

    Err instances are created indirectly so that Err remains matchable but is
    not directly instantiated in normal use.
    """

    instance = object.__new__(Err)
    object.__setattr__(instance, '_error', error)
    return instance
