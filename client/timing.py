import functools
import time
from typing import Any, Callable

from log_config import main_logger as logger


# 额外：一个更简洁的版本，适合生产环境
def simple_timer(func: Callable) -> Callable:
    """简洁版计时装饰器，只输出总时间"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"⏱️  {func.__name__} took {elapsed * 1_000_000:.2f} μs")
        return result

    return wrapper
