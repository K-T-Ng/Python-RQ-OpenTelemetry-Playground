import fakeredis
import pytest
from rq.job import Job
from rq.queue import Queue
from rq.worker import Worker

from opentelemetry.instrumentation.rq import utils

MOCK_REDIS_CONNECTION = fakeredis.FakeRedis()


class TestUtils:
    @classmethod
    def setup_class(self):
        self.mock_redis_connection = fakeredis.FakeRedis()

    @pytest.mark.parametrize(
        "job,queue,worker,expected",
        [
            (
                Job.create(
                    print, args=(10,), id="job_id", connection=MOCK_REDIS_CONNECTION
                ),
                Queue(name="queue_name", connection=MOCK_REDIS_CONNECTION),
                Worker(
                    name="worker_name",
                    queues=["queue_name"],
                    connection=MOCK_REDIS_CONNECTION,
                ),
                {
                    "job.id": "job_id",
                    "job.func_name": "builtins.print",
                    "queue.name": "queue_name",
                    "worker.name": "worker_name",
                },
            ),
            (
                None,
                Queue(name="queue_name", connection=MOCK_REDIS_CONNECTION),
                Worker(
                    name="worker_name",
                    queues=["queue_name"],
                    connection=MOCK_REDIS_CONNECTION,
                ),
                {
                    "queue.name": "queue_name",
                    "worker.name": "worker_name",
                },
            ),
            (
                Job.create(
                    print, args=(10,), id="job_id", connection=MOCK_REDIS_CONNECTION
                ),
                None,
                Worker(
                    name="worker_name",
                    queues=["queue_name"],
                    connection=MOCK_REDIS_CONNECTION,
                ),
                {
                    "job.id": "job_id",
                    "job.func_name": "builtins.print",
                    "worker.name": "worker_name",
                },
            ),
            (
                Job.create(
                    print, args=(10,), id="job_id", connection=MOCK_REDIS_CONNECTION
                ),
                Queue(name="queue_name", connection=MOCK_REDIS_CONNECTION),
                None,
                {
                    "job.id": "job_id",
                    "job.func_name": "builtins.print",
                    "queue.name": "queue_name",
                },
            ),
        ],
    )
    def test_extrace_attributes(self, job, queue, worker, expected):
        output = utils._extract_attributes(job, queue, worker)
        assert output == expected
