"""RQ worker"""

import logging

from redis import Redis
from rq import Queue, Worker

from src.init_otel import get_logger, init_otel

if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    init_otel()
    logger = get_logger()

    redis = Redis(host="localhost", port=6379)
    queue = Queue("task_queue", connection=redis)

    worker = Worker([queue], connection=redis, name="rq-worker")
    worker.work()
