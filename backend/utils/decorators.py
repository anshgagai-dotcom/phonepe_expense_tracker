"""
Performance timing decorator
"""
import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger("PhonePeTracker")

def timer(func: Callable) -> Callable:
    """Measure and log function execution time"""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        logger.info(f"Execution of {func.__name__} took {end_time - start_time:.6f} seconds.")
        return result
    return wrapper
