"""
Instrumentation va o'lchovlar
"""
import time
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


def measure_time(func: Callable) -> Callable:
    """Funksiya bajarilish vaqtini o'lchash"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = time.time() - start
            logger.info(f"⏱️ {func.__name__} took {elapsed:.2f} seconds")

    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        start = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.time() - start
            logger.info(f"⏱️ {func.__name__} took {elapsed:.2f} seconds")

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


import asyncio

