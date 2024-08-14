"""A producer keep enqueuing job to RQ"""

import logging
import time

from redis import Redis
from rq import Queue

from opentelemetry.instrumentation.rq import RQInstrumentor
from src.opentelemetry import initialize
from src.tasks import task

if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    initialize(
        otlp_http_endpoint="http://localhost:4318", logger_names=("root", __name__)
    )

    redis = Redis()
    queue = Queue("task_queue", connection=redis)

    while True:
        job = queue.enqueue(task)
        time.sleep(10)
