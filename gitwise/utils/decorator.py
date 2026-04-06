import time
import logging
"""decorator is basically a wrapper around a function or method that allows you to add extra behavior before or after it runs, without changing its code."""
def  log_duration(func):
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start = time.time()
        result = func(*args, **kwargs)  # run the original method
        end = time.time()
        logger.info(f"Task '{func.__name__}' completed in {end - start:.2f}s")
        return result
    return wrapper