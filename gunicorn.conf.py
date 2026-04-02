import os


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")
workers = env_int("GUNICORN_WORKERS", 4)
threads = env_int("GUNICORN_THREADS", 1)
timeout = env_int("GUNICORN_TIMEOUT", 60)
graceful_timeout = env_int("GUNICORN_GRACEFUL_TIMEOUT", 30)
accesslog = os.getenv("GUNICORN_ACCESSLOG", "-")
errorlog = os.getenv("GUNICORN_ERRORLOG", "-")
capture_output = True
worker_tmp_dir = "/tmp"
