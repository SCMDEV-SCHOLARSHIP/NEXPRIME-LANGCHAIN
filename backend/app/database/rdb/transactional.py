from enum import Enum
from functools import wraps
from typing import ParamSpec, TypeVar, Callable

from app.database.rdb import session

_T = TypeVar("_T")
_P = ParamSpec("_P")


class Propagation(Enum):
    REQUIRED = "required"
    REQUIRED_NEW = "required_new"


class Transactional:
    def __init__(self, propagation: Propagation = Propagation.REQUIRED):
        self.propagation = propagation

    def __call__(self, function: Callable[_P, _T]) -> Callable[_P, _T]:
        @wraps(function)
        async def decorator(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            try:
                if self.propagation == Propagation.REQUIRED:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                elif self.propagation == Propagation.REQUIRED_NEW:
                    result = await self._run_required_new(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                else:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
            except Exception as e:
                await session.rollback()
                raise e

            return result

        return decorator

    async def _run_required(self, function, args, kwargs):
        result = await function(*args, **kwargs)
        await session.commit()
        return result

    async def _run_required_new(self, function, args, kwargs):
        session.begin()
        result = await function(*args, **kwargs)
        await session.commit()
        return result
