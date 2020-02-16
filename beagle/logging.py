import functools
import logging
import time


def init_logger() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Beginning to {func.__name__!r}...")
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        logging.info(
            f"Finished to {func.__name__!r} in {time.perf_counter() - start_time:4f}s."
        )
        return value

    return wrapper
