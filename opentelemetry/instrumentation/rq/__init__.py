"""
A library that instrument `rq` library for learning aspect.
"""

from typing import Collection

import rq.queue
import rq.worker
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from wrapt import wrap_function_wrapper

from opentelemetry.instrumentation.rq.package import _instruments
from opentelemetry.instrumentation.rq.utils import (
    _trace__enqueue_job,
    _trace_perform_job,
)


class RQInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        wrap_function_wrapper("rq.queue", "Queue._enqueue_job", _trace__enqueue_job)
        wrap_function_wrapper("rq.worker", "Worker.perform_job", _trace_perform_job)

    def _uninstrument(self, **kwargs):
        unwrap(rq.worker.Worker, "perform_job")
        unwrap(rq.queue.Queue, "_enqueue_job")
