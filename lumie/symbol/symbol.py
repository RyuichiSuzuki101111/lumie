# lumie/symbol/symbol.py
from threading import RLock
from typing import Any, ClassVar, Self
from uuid import UUID, uuid5
from weakref import WeakValueDictionary

from lumie.constants import LUMIE_NAMESPACE

SYMBOL_NAMESPACE = uuid5(LUMIE_NAMESPACE, "symbol")


class Symbol:
    _NAMESPACE: ClassVar[UUID] = uuid5(SYMBOL_NAMESPACE, "Symbol")
    _LOCK: ClassVar[RLock] = RLock()
    _instances: ClassVar[WeakValueDictionary[tuple[str, UUID | None], Self]] = (
        WeakValueDictionary()
    )

    __slots__ = ("name", "uid", "namespace", "context_uid")
    context_uid: UUID | None = None
    namespace: UUID
    name: str
    uid: UUID

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls._NAMESPACE = uuid5(SYMBOL_NAMESPACE, cls.__name__)
        cls._instances = WeakValueDictionary()

    def validate_uid(self) -> None:
        expected_namespace = (
            uuid5(self._NAMESPACE, self.context_uid.hex)
            if self.context_uid
            else self._NAMESPACE
        )
        expected_uid = uuid5(expected_namespace, self.name)
        if self.namespace != expected_namespace:
            raise ValueError(
                f"Namespace {self.namespace} does not match the expected namespace {expected_namespace} for name '{self.name}'"
            )
        if self.uid != expected_uid:
            raise ValueError(
                f"UID {self.uid} does not match the expected UID {expected_uid} for name '{self.name}'"
            )

    @classmethod
    def _create_with_full_attrs(
        cls, name: str, uid: UUID, namespace: UUID, context_uid: UUID | None = None
    ) -> Self:
        if (symbol := cls._instances.get((name, context_uid))) is not None:
            return symbol

        with cls._LOCK:
            if (symbol := cls._instances.get((name, context_uid))) is not None:
                return symbol

            symbol = super().__new__(cls)
            object.__setattr__(symbol, "name", name)
            object.__setattr__(symbol, "uid", uid)
            object.__setattr__(symbol, "namespace", namespace)
            object.__setattr__(symbol, "context_uid", context_uid)
            cls._instances[(name, context_uid)] = symbol
        symbol.validate_uid()
        return symbol

    def __new__(cls, name: str, *, context_uid: UUID | None = None) -> Self:
        if symbol := cls._instances.get((name, context_uid)):
            return symbol

        with cls._LOCK:
            if symbol := cls._instances.get((name, context_uid)):
                return symbol

            symbol = super().__new__(cls)

            namespace = (
                uuid5(cls._NAMESPACE, context_uid.hex)
                if context_uid
                else cls._NAMESPACE
            )
            uid_ = uuid5(namespace, name)
            object.__setattr__(symbol, "name", name)
            object.__setattr__(symbol, "uid", uid_)
            object.__setattr__(symbol, "namespace", namespace)
            object.__setattr__(symbol, "context_uid", context_uid)
            cls._instances[(name, context_uid)] = symbol

        return symbol

    def __setattr__(self, key: str, value: Any) -> None:
        raise AttributeError("Symbol instances are immutable")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Symbol):
            return NotImplemented
        return self.uid == other.uid and self.context_uid == other.context_uid

    def __hash__(self) -> int:
        return hash((self.uid, self.context_uid))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r}, context_uid={self.context_uid!r})"

    def __reduce__(
        self,
    ) -> Any:
        return (
            self._create_with_full_attrs,
            (self.name, self.uid, self.namespace, self.context_uid),
        )
