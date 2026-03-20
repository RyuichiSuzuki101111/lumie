# lumie/symbol/symbol.py
from threading import RLock
from typing import Any, ClassVar
from uuid import UUID, uuid5
from weakref import WeakValueDictionary

from typing_extensions import Self

from lumie.constants import LUMIE_NAMESPACE

SYMBOL_NAMESPACE = uuid5(LUMIE_NAMESPACE, 'symbol')


class Symbol:
    _NAMESPACE: ClassVar[UUID] = uuid5(SYMBOL_NAMESPACE, 'Symbol')
    _LOCK: ClassVar[RLock] = RLock()
    _instances: ClassVar[WeakValueDictionary[str, Self]] = WeakValueDictionary()

    __slots__ = ('name', 'uid')
    name: str
    uid: UUID

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._NAMESPACE = uuid5(SYMBOL_NAMESPACE, cls.__name__)
        cls._instances = WeakValueDictionary()

    def __new__(cls, name: str, *, uid: UUID | None = None) -> Self:
        with cls._LOCK:
            expected_uid = uuid5(cls._NAMESPACE, name)
            if symbol := cls._instances.get(name):
                if symbol.uid != expected_uid:
                    msg = f"Existing symbol with name '{name}' has UID {symbol.uid}, which does not match the expected UID {expected_uid}"
                    raise ValueError(msg)
                return symbol

            if uid is not None and uid != expected_uid:
                msg = f"Provided UID {uid} does not match the expected UID {expected_uid} for name '{name}'"
                raise ValueError(msg)

            symbol = object.__new__(cls)
            final_uid = uid or expected_uid
            object.__setattr__(symbol, 'name', name)
            object.__setattr__(symbol, 'uid', final_uid)
            cls._instances[name] = symbol

        return symbol

    def __setattr__(self, key: str, value: Any) -> None:
        raise AttributeError('Symbol instances are immutable')

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Symbol):
            return NotImplemented
        return self.uid == other.uid

    def __hash__(self) -> int:
        return hash(self.uid)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r})'

    def __reduce__(self) -> tuple[type, tuple[str, UUID]]:
        return (self.__class__, (self.name, self.uid))
