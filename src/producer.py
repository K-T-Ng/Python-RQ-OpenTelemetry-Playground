"""A producer keep enqueuing job to RQ"""

import time

from redis import Redis
from rq import Queue

from src.tasks import task

if __name__ == "__main__":
    redis = Redis()
    queue = Queue("task_queue", connection=redis)

    while True:
        job = queue.enqueue(task)
        time.sleep(10)
