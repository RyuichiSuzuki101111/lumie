# lumie/q_vector/q_vector_impl.py
from __future__ import annotations

from typing import Protocol, TypeVar

from lumie.symbol import Symbol

S = TypeVar('S', bound=Symbol)
V = TypeVar('V')
V_co = TypeVar('V_co', covariant=True)
V_contra = TypeVar('V_contra', contravariant=True)


class UnaryPredicate(Protocol[V_contra]):
    def __call__(self, v: V_contra) -> bool: ...


class BinaryPredicate(Protocol[V_contra]):
    def __call__(self, v1: V_contra, v2: V_contra) -> bool: ...


class UnaryOp(Protocol[V]):
    def __call__(self, v: V) -> V: ...


class BinaryOp(Protocol[V]):
    def __call__(self, v1: V, v2: V) -> V: ...


class UnitVector(Protocol[V_co]):
    def __call__(self, index: int) -> V_co: ...


class ScalarMul(Protocol[V]):
    def __call__(self, v: V, scalar_num: int, scalar_den: int) -> V: ...


class DictToVector(Protocol[V_co]):
    def __call__(self, expr: dict[int, tuple[int, int]]) -> V_co: ...


class VectorToDict(Protocol[V_contra]):
    def __call__(self, vector: V_contra) -> dict[int, tuple[int, int]]: ...


class QVectorImpl(Protocol[V]):
    zero: V
    is_zero: UnaryPredicate[V]
    unit_vector: UnitVector[V]
    dict_to_vector: DictToVector[V]
    vector_to_dict: VectorToDict[V]
    add: BinaryOp[V]
    sub: BinaryOp[V]
    neg: UnaryOp[V]
    scalar_mul: ScalarMul[V]

    eq: BinaryPredicate[V]
