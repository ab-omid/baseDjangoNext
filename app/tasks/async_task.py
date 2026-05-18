from functools import wraps
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar

from asgiref import sync
from celery import Celery, Task

_P = ParamSpec("_P")
_R = TypeVar("_R")


def async_task(app: Celery, *args: Any, **kwargs: Any) -> Callable[[Callable[_P, Coroutine[Any, Any, _R]]], Task]:
    """
    This function is a decorator that can be used to convert a regular function into a Celery task.
    The function takes in an instance of the Celery application as well as any additional arguments
    that need to be passed to the Celery task.

    Args:
        app (Celery): An instance of the Celery application.
        *args: Any additional positional arguments that need to be passed to the Celery task.
        **kwargs: Any additional keyword arguments that need to be passed to the Celery task.

    Returns:
        Callable[[Callable[_P, Coroutine[Any, Any, _R]]], Task]: A decorator that can be used to convert a regular function into a Celery task.
    """
    def _decorator(func: Callable[_P, Coroutine[Any, Any, _R]]) -> Task:
        sync_call = sync.AsyncToSync(func)

        @app.task(*args, **kwargs)
        @wraps(func)
        def _decorated(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            return sync_call(*args, **kwargs)

        return _decorated

    return _decorator
