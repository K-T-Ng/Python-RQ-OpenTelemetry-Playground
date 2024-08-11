"""RQ worker"""

from redis import Redis
from rq import Queue, Worker

if __name__ == "__main__":
    redis = Redis(host="localhost", port=6379)
    queue = Queue("task_queue", connection=redis)

    worker = Worker([queue], connection=redis, name="rq-worker")
    worker.work()
