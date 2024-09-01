"""Unit tests for opentelemetry/instrumentation/rq"""

import logging
import unittest
import unittest.mock
from typing import List

import fakeredis
from rq.job import Job
from rq.queue import Queue
from rq.worker import Worker

from opentelemetry import _logs as logs_api
from opentelemetry.instrumentation.rq import RQInstrumentor
from opentelemetry.sdk import trace
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import ConsoleLogExporter, SimpleLogRecordProcessor
from opentelemetry.sdk.trace import _Span
from opentelemetry.test.globals_test import reset_logging_globals
from opentelemetry.test.test_base import TestBase


class TestRQInstrumentation(TestBase):

    def setUp(self):
        """Setup for testing
        - Setup tracer and meter from opentelemetry.test.test_base.TestBase
        - Setup logger
        - Setup fake redis connection to mockup redis for RQ
        - Instrument RQ
        """
        super().setUp()

        reset_logging_globals()
        self.logger_provider, self.console_exporter = self._create_log_provider()
        logs_api.set_logger_provider(self.logger_provider)

        self.fake_redis = fakeredis.FakeRedis()

        RQInstrumentor().instrument()

    def tearDown(self):
        """Teardown for testing
        - Uninstrument RQ
        - Teardown logger for testing
        - Teardown tracer and meter from opentelemetry.test.test_base.TestBase
        """
        RQInstrumentor().uninstrument()
        reset_logging_globals()
        super().tearDown()

    def test_instrument_enqueue(self):
        """Test for rq.enqueue._enqueue_job

        Assuming that it is triggered by job and queue, without
        worker here. We expected that
            - there are `job` and `queue` meta in the `span.attributes` only.
            - the traceparent is updated to `job.meta`
        """
        job = Job.create(
            func=print, args=(10,), id="job_id", connection=self.fake_redis
        )
        queue = Queue(name="queue_name", connection=self.fake_redis)

        expected_attributes = {
            "job.id": "job_id",
            "job.func_name": "builtins.print",
            "queue.name": "queue_name",
        }

        queue._enqueue_job(job)

        spans: List[_Span] = self.memory_exporter.get_finished_spans()
        span = spans[0]

        self.assertSpanHasAttributes(span, expected_attributes)
        self.assertNotIn("worker.name", span.attributes)
        self.assertIn("traceparent", job.meta)

    def test_instrument_execute(self):
        """Test for the following methods for task execution"""
        job = Job.create(
            func=print, args=(10,), id="job_id", connection=self.fake_redis
        )
        queue = Queue(name="queue_name", connection=self.fake_redis)
        worker = Worker(
            queues=["queue_name"], name="worker_name", connection=self.fake_redis
        )

        # Generate consumer spans
        worker.execute_job(job, queue)
        expected_consumer_attributes = {
            "job.id": "job_id",
            "job.func_name": "builtins.print",
            "queue.name": "queue_name",
            "worker.name": "worker_name",
        }

        spans: List[_Span] = self.sorted_spans(
            self.memory_exporter.get_finished_spans()
        )
        span = spans[0]

        self.assertSpanHasAttributes(span, expected_consumer_attributes)

    def _create_log_provider(self, **kwargs):
        """Helper to create a configured logger provider.

        Creatges and configures a `LoggerProvider` with a
        `SimpleLogProcessor` and a `ConsoleLogExporter`
        All the parameters passed are forwarded to the LoggerProvider
        constructor.

        Returns:
            A list with the tracer provider in the first element and the
            in-memory span exporter in the second.
        """
        log_provider = LoggerProvider(**kwargs)
        console_exporter = ConsoleLogExporter()
        log_processor = SimpleLogRecordProcessor(console_exporter)
        log_provider.add_log_record_processor(log_processor)
        return log_provider, console_exporter
