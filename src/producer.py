"""A producer keep enqueuing job to RQ"""

import logging
import time

from redis import Redis
from rq import Queue

from opentelemetry.instrumentation.rq import RQInstrumentor
from src.init_otel import get_logger, init_otel
from src.tasks import task

if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    init_otel()
    logger = get_logger()
    RQInstrumentor().instrument()

    redis = Redis()
    queue = Queue("task_queue", connection=redis)

    while True:
        job = queue.enqueue(task)
        time.sleep(10)
