# lumie/result.py
"""
A lightweight Result type for Python.

This module provides a small Result abstraction for operations that may fail,
where returning an error value is preferable to raising and catching exceptions.

Design principles:
- Represent expected failures as values.
- Keep success / failure handling lightweight.
- Consume results naturally via pattern matching on Ok / Err.
- Ok / Err are part of the public shape of Result values, but are not
  instantiated directly.
- Type hints are best-effort and may use Any where stricter typing would
  overstate guarantees on concrete Result variants.

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
    final,
    overload,
)

if TYPE_CHECKING:
    from collections.abc import Callable

# R: success value
# E: error value
# S: mapped success value
# F: mapped error value
# T: generic auxiliary type (e.g. unwrap_or default)
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
    The successful variant of Result.

    This class is primarily used for pattern matching:

        match result:
            case Ok(value): ...

    Instances are constructed via ok(...), not by calling Ok directly.
    Prefer using the Result interface for operations.
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
        """
        Return True if this Result is Ok.

        This is a runtime guard for operations such as unwrap().
        It is not intended as a type narrowing mechanism.
        """
        return True

    @property
    def is_err(self) -> Literal[False]:
        """
        Return False if this Result is Ok.

        This is a runtime guard for operations such as unwrap_err().
        It is not intended as a type narrowing mechanism.
        """
        return False

    def unwrap(self) -> R:
        """Return the success value."""
        return self._value

    def unwrap_or(self, default: T) -> R | T:  # noqa: ARG002
        """Return the success value, ignoring the provided default."""
        return self._value

    def unwrap_err(self) -> Any:  # noqa: ANN401
        """Raise UnwrapError because this Result is Ok."""
        msg = f'Called unwrap_err on Ok: {self._value!r}'
        raise UnwrapError(msg)

    def and_then(self, func: Callable[[R], Result[S, E]]) -> Result[S, E]:
        """Apply a Result-returning function to the success value."""
        return func(self._value)

    def map(self, func: Callable[[R], S]) -> Result[S, Any]:
        """Transform the success value."""
        return ok(func(self._value))

    def map_err(self, func: Callable[[Any], F]) -> Result[R, F]:  # noqa: ARG002
        """Preserve the success value without applying the error transform."""
        return ok(self._value)

    def __str__(self) -> str:
        return f'Ok({self._value})'

    def __repr__(self) -> str:
        return f'Ok({self._value!r})'

    def __reduce__(self) -> Any:  # noqa: ANN401
        return ok, (self._value,)


@final
class Err(Generic[E]):
    """
    The error variant of Result.

    This class is primarily used for pattern matching:

        match result:
            case Err(error): ...

    Instances are constructed via err(...), not by calling Err directly.
    Prefer using the Result interface for operations.
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
        """
        Return False if this Result is Err.

        This is a runtime guard for operations such as unwrap().
        It is not intended as a type narrowing mechanism.
        """
        return False

    @property
    def is_err(self) -> Literal[True]:
        """
        Return True if this Result is Err.

        This is a runtime guard for operations such as unwrap_err().
        It is not intended as a type narrowing mechanism.
        """
        return True

    def unwrap(self) -> Any:  # noqa: ANN401
        """Raise UnwrapError because this Result is Err."""
        msg = f'Called unwrap on Err: {self._error!r}'
        raise UnwrapError(msg)

    def unwrap_or(self, default: T) -> T:
        """Return the provided default."""
        return default

    def unwrap_err(self) -> E:
        """Return the error value."""
        return self._error

    def and_then(self, func: Callable[[Any], Result[S, E]]) -> Result[S, E]:  # noqa: ARG002
        """Preserve the error without applying the function."""
        return err(self._error)

    def map(self, func: Callable[[R], S]) -> Result[S, E]:  # noqa: ARG002
        """Preserve the error without applying the success transform."""
        return err(self._error)

    def map_err(self, func: Callable[[E], F]) -> Result[Any, F]:
        """Transform the error value."""
        return err(func(self._error))

    def __str__(self) -> str:
        return f'Err({self._error})'

    def __repr__(self) -> str:
        return f'Err({self._error!r})'

    def __reduce__(self) -> Any:  # noqa: ANN401
        return err, (self._error,)


class Result(Protocol[R_co, E]):
    """
    A Result represents either a successful value (Ok) or an error value (Err).

    This is a typing protocol, not a runtime base class.

    It is intended for operations where failure is part of normal control flow
    and should be returned explicitly rather than raised as an exception.

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

        When branching on Result values, prefer pattern matching on Ok / Err.
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
        """Apply a Result-returning function to the success value."""

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

    err_type is for type checking only and has no runtime effect.
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

    ok_type is for type checking only and has no runtime effect.

    Passing ok_type=None produces Result[None, E].
    """

    instance = object.__new__(Err)
    object.__setattr__(instance, '_error', error)
    return instance
