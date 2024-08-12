"""
A library that instrument `rq` library for learning aspect.
"""

from typing import Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from wrapt import wrap_function_wrapper

from opentelemetry.instrumentation.rq.package import _instruments
from opentelemetry.instrumentation.rq.utils import _trace_enqueue_call


class RQInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        wrap_function_wrapper("rq.queue", "Queue.enqueue_call", _trace_enqueue_call)

    def _uninstrument(self, **kwargs):
        return super()._uninstrument(**kwargs)
