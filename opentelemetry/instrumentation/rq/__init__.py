"""
A library that instrument `rq` library for learning aspect.
"""

import logging
from typing import Callable, Collection, Dict, Tuple, Union

import rq.job
import rq.queue
import rq.worker
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from rq.job import Job
from rq.queue import Queue
from rq.worker import Worker
from wrapt import wrap_function_wrapper

from opentelemetry import _logs, trace
from opentelemetry.instrumentation.rq.package import _instruments
from opentelemetry.instrumentation.rq.utils import (
    _add_handler_with_provider_to_logger,
    _extract_attributes,
    _extract_context_from_job_meta,
    _inject_context_to_job_meta,
    _remove_handler_with_provider_from_logger,
)

LOGGERS = ("rq.job", "rq.queue", "rq.registry", "rq.worker")


def _instrument_execute(force_flush: bool = False) -> Callable:
    """Instrument execute methods
    rq.worker.BaseWorker.execute_job(job, queue)
    rq.worker.Worker.perform_job(job, queue)
    job.perform()
    """

    def _inner(func: Callable, instance: Union[Job, Worker], args: Tuple, kwargs: Dict):
        """Instrument execution function"""
        if isinstance(instance, Worker):
            job, queue = args[0], args[1]
        else:
            job, queue = instance, None

        attributes: Dict = _extract_attributes(job=job, queue=queue)
        ctx: trace.Context = _extract_context_from_job_meta(job)

        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(
            name=func.__name__, kind=trace.SpanKind.CONSUMER, context=ctx
        ) as span:
            if span.is_recording():
                span.set_attributes(attributes=attributes)

            response = func(*args, **kwargs)

        if force_flush:
            trace.get_tracer_provider().force_flush()
            _logs.get_logger_provider().force_flush()

        return response

    return _inner


def _instruement_enqueue(func: Callable, instance: Queue, args: Tuple, kwargs: Dict):
    """Instrument rq.queue.Queue._queue_job"""
    job: Job = args[0]
    queue: Queue = instance
    attributes: Dict = _extract_attributes(job=job, queue=queue)

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(
        name="enqueue", kind=trace.SpanKind.PRODUCER
    ) as span:
        if span.is_recording():
            span.set_attributes(attributes=attributes)
            _inject_context_to_job_meta(job)
        response = func(*args, **kwargs)

    return response


class RQInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        self.log_provider: LoggerProvider = _logs.get_logger_provider()
        self.log_handler = LoggingHandler(
            level=logging.NOTSET, logger_provider=self.log_provider
        )
        _add_handler_with_provider_to_logger(LOGGERS, self.log_handler)

        wrap_function_wrapper("rq.queue", "Queue._enqueue_job", _instruement_enqueue)
        wrap_function_wrapper("rq.job", "Job.perform", _instrument_execute())
        wrap_function_wrapper(
            "rq.worker", "Worker.perform_job", _instrument_execute(force_flush=True)
        )
        wrap_function_wrapper("rq.worker", "Worker.execute_job", _instrument_execute())

    def _uninstrument(self, **kwargs):
        unwrap(rq.queue.Queue, "_enqueue_job")
        unwrap(rq.worker.Worker, "execute_job")
        unwrap(rq.worker.Worker, "perform_job")
        unwrap(rq.job.Job, "perform")
        _remove_handler_with_provider_from_logger(LOGGERS, self.log_handler)
