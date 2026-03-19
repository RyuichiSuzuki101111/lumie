# lumie/symbol/symbol.py
from threading import RLock
from typing import Any, ClassVar, Self
from uuid import UUID, uuid5
from weakref import WeakValueDictionary

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

    def validate_uid(self) -> None:
        expected_uid = uuid5(self._NAMESPACE, self.name)
        if self.uid != expected_uid:
            raise ValueError(
                f"UID {self.uid} does not match the expected UID {expected_uid} for name '{self.name}'"
            )

    @classmethod
    def _create_with_full_attrs(cls, name: str, uid: UUID) -> Self:
        if (symbol := cls._instances.get(name)) is not None:
            return symbol

        with cls._LOCK:
            if (symbol := cls._instances.get(name)) is not None:
                return symbol

            symbol = super().__new__(cls)
            object.__setattr__(symbol, 'name', name)
            object.__setattr__(symbol, 'uid', uid)
            cls._instances[name] = symbol
        symbol.validate_uid()
        return symbol

    def __new__(cls, name: str) -> Self:
        with cls._LOCK:
            if symbol := cls._instances.get(name):
                return symbol

            symbol = super().__new__(cls)
            uid_ = uuid5(cls._NAMESPACE, name)
            object.__setattr__(symbol, 'name', name)
            object.__setattr__(symbol, 'uid', uid_)
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

    def __reduce__(
        self,
    ) -> Any:
        return (type(self)._create_with_full_attrs, (self.name, self.uid))
