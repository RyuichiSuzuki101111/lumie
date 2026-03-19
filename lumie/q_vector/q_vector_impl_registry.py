import logging
from threading import RLock
from typing import Any, Literal

from .q_vector_impl import QVectorImpl, assert_q_vector_impl

_LOCK = RLock()
_LOCKED_Q_VECTOR_IMPLS: dict[str, QVectorImpl[Any]] = {}

logger = logging.getLogger(__name__)


def register_q_vector_impl(key: str, impl: QVectorImpl[Any]) -> None:
    with _LOCK:
        if key in _LOCKED_Q_VECTOR_IMPLS:
            if _LOCKED_Q_VECTOR_IMPLS[key] is impl:
                logger.debug(
                    'QVectorImpl with key %r is already registered with the same implementation, skipping',
                    key,
                )
                return  # Already registered, do nothing
            msg = f'QVectorImpl with key {key!r} is already registered'
            raise ValueError(msg)
        try:
            assert_q_vector_impl(impl)
        except TypeError as e:
            msg = f'{impl!r} does not implement QVectorImpl: {e}'
            raise TypeError(msg) from e

        _LOCKED_Q_VECTOR_IMPLS[key] = impl


def get_q_vector_impl(key: str) -> QVectorImpl[Any]:
    with _LOCK:
        if key not in _LOCKED_Q_VECTOR_IMPLS:
            msg = f'No QVectorImpl registered with key {key!r}'
            raise ValueError(msg)
        return _LOCKED_Q_VECTOR_IMPLS[key]


def restore(
    impls: dict[str, QVectorImpl[Any]], mode: Literal['merge', 'replace']
) -> None:
    with _LOCK:
        if mode == 'replace':
            _LOCKED_Q_VECTOR_IMPLS.clear()
        for key, impl in impls.items():
            if key in _LOCKED_Q_VECTOR_IMPLS:
                if _LOCKED_Q_VECTOR_IMPLS[key] is impl:
                    continue
                if mode == 'merge':
                    logger.warning(
                        'QVectorImpl with key %r is already registered, skipping', key
                    )
                    continue
                else:
                    msg = f'QVectorImpl with key {key!r} is already registered'
                    raise ValueError(msg)

            assert_q_vector_impl(impl)
            _LOCKED_Q_VECTOR_IMPLS[key] = impl


def snapshot() -> dict[str, QVectorImpl[Any]]:
    with _LOCK:
        return dict(_LOCKED_Q_VECTOR_IMPLS)
