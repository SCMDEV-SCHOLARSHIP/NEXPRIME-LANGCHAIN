from enum import Enum
from functools import wraps
from typing import ParamSpec, TypeVar, Callable
from sqlalchemy.ext.asyncio import async_scoped_session
from dependency_injector.wiring import inject, Provide


_T = TypeVar("_T")
_P = ParamSpec("_P")


class Propagation(Enum):
    REQUIRED = "required"
    REQUIRED_NEW = "required_new"


class Transactional:
    def __init__(self, propagation: Propagation = Propagation.REQUIRED):
        self.propagation = propagation

    def __call__(
        self,
        function: Callable[_P, _T],
    ) -> Callable[_P, _T]:
        @wraps(function)
        @inject
        async def decorator(
            *args: _P.args,
            session: async_scoped_session = Provide["session"],
            **kwargs: _P.kwargs
        ) -> _T:
            try:
                if self.propagation == Propagation.REQUIRED:
                    result = await self._run_required(
                        function=function,
                        session=session,
                        args=args,
                        kwargs=kwargs,
                    )
                elif self.propagation == Propagation.REQUIRED_NEW:
                    result = await self._run_required_new(
                        function=function,
                        session=session,
                        args=args,
                        kwargs=kwargs,
                    )
                else:
                    result = await self._run_required(
                        function=function,
                        session=session,
                        args=args,
                        kwargs=kwargs,
                    )
            except Exception as e:
                await session.rollback()
                raise e

            return result

        return decorator

    async def _run_required(self, function, session, args, kwargs):
        result = await function(*args, **kwargs)
        await session.commit()
        return result

    async def _run_required_new(self, function, session, args, kwargs):
        session.begin()
        result = await function(*args, **kwargs)
        await session.commit()
        return result
