# lumie/result.pyi
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, TypeVar, overload

R_co = TypeVar('R_co', covariant=True)
R = TypeVar('R')
S = TypeVar('S')
E = TypeVar('E')
F = TypeVar('F')
T = TypeVar('T')

class UnwrapError(Exception):
    pass

class Result(Protocol[R_co, E]):
    @property
    def is_ok(self) -> bool: ...
    @property
    def is_err(self) -> bool: ...
    def unwrap(self) -> R_co: ...
    def unwrap_or(self, default: T) -> R_co | T: ...
    def unwrap_err(self) -> E: ...
    def and_then(self, func: Callable[[R_co], Result[S, E]]) -> Result[S, E]: ...
    def map(self, func: Callable[[R_co], S]) -> Result[S, E]: ...
    def map_err(self, func: Callable[[E], F]) -> Result[R_co, F]: ...

class Ok(Result[R, Any]):
    __match_args__ = ('_value',)
    __slots__ = ('_value',)
    _value: R

@overload
def ok(value: R) -> Result[R, Any]: ...
@overload
def ok(value: R, *, err_type: type[E]) -> Result[R, E]: ...

class Err(Result[Any, E]):
    __match_args__ = ('_error',)
    __slots__ = ('_error',)
    _error: E

@overload
def err(error: E) -> Result[Any, E]: ...
@overload
def err(error: E, *, ok_type: type[R]) -> Result[R, E]: ...
@overload
def err(error: E, *, ok_type: None) -> Result[None, E]: ...
