# lumie/q_vector/q_vector_impl.py
from __future__ import annotations

from typing import Any, Protocol, TypeVar

from lumie.symbol import Symbol

S = TypeVar('S', bound=Symbol)
V = TypeVar('V')
V_co = TypeVar('V_co', covariant=True)
V_contra = TypeVar('V_contra', contravariant=True)


class Zero(Protocol[V_co]):
    def __call__(self, /) -> V_co: ...


class UnaryPredicate(Protocol[V_contra]):
    def __call__(self, v: V_contra, /) -> bool: ...


class BinaryPredicate(Protocol[V_contra]):
    def __call__(self, v1: V_contra, v2: V_contra, /) -> bool: ...


class UnaryOp(Protocol[V]):
    def __call__(self, v: V, /) -> V: ...


class BinaryOp(Protocol[V]):
    def __call__(self, v1: V, v2: V, /) -> V: ...


class UnitVector(Protocol[V_co]):
    def __call__(self, index: int, /) -> V_co: ...


class ScalarMul(Protocol[V]):
    def __call__(self, v: V, scalar_num: int, scalar_den: int, /) -> V: ...


class DictToVector(Protocol[V_co]):
    def __call__(self, expr: dict[int, tuple[int, int]], /) -> V_co: ...


class VectorToDict(Protocol[V_contra]):
    def __call__(self, vector: V_contra, /) -> dict[int, tuple[int, int]]: ...


class QVectorImpl(Protocol[V]):
    zero: Zero[V]
    is_zero: UnaryPredicate[V]
    unit_vector: UnitVector[V]
    dict_to_vector: DictToVector[V]
    vector_to_dict: VectorToDict[V]
    add: BinaryOp[V]
    sub: BinaryOp[V]
    neg: UnaryOp[V]
    scalar_mul: ScalarMul[V]
    eq: BinaryPredicate[V]


def assert_q_vector_impl(obj: object) -> QVectorImpl[Any]:
    required_attrs = {
        'zero',
        'is_zero',
        'unit_vector',
        'dict_to_vector',
        'vector_to_dict',
        'add',
        'sub',
        'neg',
        'scalar_mul',
        'eq',
    }

    missing = []
    invalid = []

    for attr in required_attrs:
        if not hasattr(obj, attr):
            missing.append(attr)
        else:
            impl_attr = getattr(obj, attr)
            if not callable(impl_attr):
                invalid.append((attr, type(impl_attr)))

    if missing or invalid:
        parts = []
        if missing:
            parts.append(f'missing: {", ".join(missing)}')
        if invalid:
            parts.append('not callable: ' + ', '.join(f'{k} ({t})' for k, t in invalid))
        detail = '; '.join(parts)
        msg = f'{obj!r} is not a valid QVectorImpl ({detail})'
        raise TypeError(msg)

    return obj  # type: ignore
