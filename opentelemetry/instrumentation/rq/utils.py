"""Utils for supporting PoC RQ instrumentation library"""

from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from rq.job import Job
from rq.queue import Queue
from rq.worker import Worker

from opentelemetry import trace


def _inject_context_to_job_meta(job: Job):
    TraceContextTextMapPropagator().inject(job.meta)


def _extract_context_from_job_meta(job: Job):
    TraceContextTextMapPropagator().extract(carrier=job.meta)


def _trace__enqueue_job(func, instance, args, kwargs):
    job: Job = args[0]
    queue: Queue = instance

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(
        name=func.__name__, kind=trace.SpanKind.PRODUCER
    ) as span:
        if span.is_recording():
            span.set_attribute("job_id", job.get_id())
            span.set_attribute("queue_name", queue.name)
        _inject_context_to_job_meta(job)
        response = func(*args, **kwargs)
    return response


def _trace_perform_job(func, instance, args, kwargs):
    job: Job = args[0]
    queue: Queue = args[1]
    worker: Worker = instance

    tracer = trace.get_tracer(__name__)
    ctx = TraceContextTextMapPropagator().extract(job.meta)
    with tracer.start_as_current_span(
        name="perform_job", kind=trace.SpanKind.CONSUMER, context=ctx
    ) as span:
        if span.is_recording():
            span.set_attribute("job.id", job.get_id())
            span.set_attribute("queue_name", queue.name)
            span.set_attribute("worker_name", worker.name)
        response = func(*args, **kwargs)

    trace.get_tracer_provider().force_flush()
    return response
