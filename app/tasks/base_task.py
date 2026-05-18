import celery


class BaseTask(celery.Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5, "countdown": 60}
    retry_backoff = True
    retry_backoff_max = 10
    soft_time_limit = 60
    hard_time_limit = 60
    acks_late = True
    max_memory = 1000
