from abc import ABC, abstractmethod
from typing import Generic, Optional, Tuple, TypeVar


InputType = TypeVar("InputType", bound=float)
OutputType = TypeVar("OutputType", bound=float)
TimeType = TypeVar("TimeType", bound=float)
T = TypeVar("T", bound=float)
Limits = Tuple[T, T]


class BaseController(ABC, Generic[InputType, OutputType, TimeType]):
    @abstractmethod
    def reset(self) -> None:
        raise RuntimeError("Can't call base controller")

    @abstractmethod
    def __call__(
        self,
        value: InputType,
        setpoint: InputType,
        t: Optional[TimeType]=None,
    ) -> OutputType:
        raise RuntimeError("Can't call base controller")

    @staticmethod
    def limit(value: T, limits: Optional[Limits[T]]) -> T:
        if limits is None:
            return value
        return min(max(value, limits[0]), limits[1])

    def update(
        self,
        value: InputType,
        setpoint: InputType,
        t: Optional[TimeType] = None,
    ) -> OutputType:
        return self(value=value, setpoint=setpoint, t=t)

