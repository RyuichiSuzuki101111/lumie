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
S = TypeVar('S')
E = TypeVar('E')
F = TypeVar('F')
T = TypeVar('T')


class UnwrapError(Exception):
    """An error raised when trying to unwrap a Result that is an Err, or unwrap_err a Result that is an Ok."""


@final
class Ok(Generic[R]):
    """
    Represents a successful result.

    This class is exposed mainly to support structural pattern matching:
        match result:
            case Ok(value): ...

    It is not intended to be instantiated or used directly in application code.
    Use ok(...) to construct values, and operate on them via the Result interface.

    Note:
        Some method signatures use `Any`. This is intentional: Ok/Err are not the
        primary abstraction, and stricter typing here would imply guarantees that
        are only meaningful at the Result level.
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
    Represents a failed result.

    This class is exposed mainly to support structural pattern matching:
        match result:
            case Err(error): ...

    It is not intended to be instantiated or used directly in application code.
    Use err(...) to construct values, and operate on them via the Result interface.

    Note:
        Some method signatures use `Any`. This is intentional: Err methods do not
        always use their inputs (e.g. and_then), and stricter typing would
        over-constrain usage without improving correctness at the Result level.
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
    A Result represents a computation that may succeed (Ok) or fail (Err).

    This is a typing protocol, not a runtime base class. Values returned by
    ok(...) and err(...) conform to this interface.

    The primary usage is chaining:
        - map       (transform success)
        - and_then  (chain computations that may fail)
        - map_err   (transform error)

    Prefer chaining over branching. Pattern matching via Ok/Err is supported,
    but should be used sparingly in favor of compositional flow.
    """

    @property
    def is_ok(self) -> bool:
        """
        Return True if this Result is Ok.

        This property is intended as a runtime guard for operations like unwrap(),
        not as a type narrowing mechanism.

        In particular, type checkers do not treat `if result.is_ok:` as narrowing
        Result[T, E] to Ok[T], and this is intentional. The primary usage of Result
        is via chaining (map / and_then), not branching.

        Use this when you need to safely access the underlying value via unwrap(),
        typically at boundaries such as logging, debugging, or final result handling.
        """

    @property
    def is_err(self) -> bool:
        """
        Return True if this Result is Err.

        See is_ok for usage notes. This is primarily a runtime guard for unwrap_err(),
        not a type narrowing mechanism.
        """

    def unwrap(self) -> R_co:
        """Return the success value or raise UnwrapError if this is an Err."""

    def unwrap_or(self, default: T) -> R_co | T:
        """Return the success value or default if this is an Err."""

    def unwrap_err(self) -> E:
        """Return the error or raise UnwrapError if this is an Ok."""

    def and_then(self, func: Callable[[R_co], Result[S, E]]) -> Result[S, E]:
        """
        Chain computations that may fail.

        The error type is preserved (E is not changed).
        Use map_err to transform errors explicitly.
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

    Parameters:
        value:
            The success value.
        err_type:
            A type hint only parameter. It has no runtime effect, but can be used
            to specify the error type when it cannot be inferred by the type checker.

    Notes:
        Instances are created via object.__new__ to keep Ok non-instantiable
        from user code while remaining lightweight.
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

    Parameters:
        error:
            The error value.
        ok_type:
            A type hint only parameter. It has no runtime effect, but can be used
            to specify the success type when it cannot be inferred.

            Passing ok_type=None produces Result[None, E].

    Notes:
        Instances are created via object.__new__ to keep Err non-instantiable
        from user code while remaining lightweight.
    """

    instance = object.__new__(Err)
    object.__setattr__(instance, '_error', error)
    return instance
