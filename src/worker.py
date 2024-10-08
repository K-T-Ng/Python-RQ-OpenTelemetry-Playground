"""RQ worker"""

import logging

from redis import Redis
from rq import Queue, Worker

from opentelemetry.instrumentation.rq import RQInstrumentor
from src.opentelemetry import initialize

if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    initialize(
        otlp_http_endpoint="http://localhost:4318", logger_names=("root", __name__)
    )

    redis = Redis(host="localhost", port=6379)
    queue = Queue("task_queue", connection=redis)

    worker = Worker([queue], connection=redis, name="rq-worker")
    worker.work()
