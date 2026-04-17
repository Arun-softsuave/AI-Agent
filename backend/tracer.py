import time
import mlflow
from functools import wraps

trace_store = {}

def auto_trace(func):

    @wraps(func)
    @mlflow.trace(name=func.__name__)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            status = "success"
            return result

        except Exception:
            status = "error"
            raise

        finally:
            elapsed = round(
                (time.perf_counter() - start) * 1000, 2
            )

            trace_store[func.__name__] = {
                "latency_ms": elapsed,
                "status": status
            }

            print(f"{func.__name__}: {elapsed} ms")

    return wrapper